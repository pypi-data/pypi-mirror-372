# TODO - EDUSCHL-23454
import os
from contextlib import (
    closing,
)
from functools import (
    reduce,
)
from operator import (
    and_,
)
from os import (
    path,
)
from typing import (
    Dict,
    Iterable,
    Set,
)

from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.db import (
    connection,
    connections,
)
from django.db.models import (
    Q,
)
from django.db.models.fields import (
    related,
)
from django.db.transaction import (
    atomic,
)
from django.http import (
    HttpRequest,
)
from psycopg2.extras import (
    Json,
)

from m3_django_compat import (
    get_related,
)

from educommon import (
    ioc,
)
from educommon.audit_log.constants import (
    EXCLUDED_TABLES,
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.logger import (
    error as logger_error,
)
from educommon.utils.misc import (
    cached_property,
)
from educommon.utils.seqtools import (
    make_chunks,
)


def configure(force_update_triggers: bool = False):
    """Изменяет параметры подключения к сервисной БД, обновляет триггеры."""
    if getattr(settings, 'USE_AUDIT_LOG_FOR_ALL_MODELS', False):
        need_to_log_table_names = get_all_table_names(settings.DEFAULT_DB_ALIAS, 'public')
    else:
        need_to_log_table_names = get_need_to_log_table_names()

    changed_table = update_or_create_tables(need_to_log_table_names)

    params = get_db_connection_params()
    params['need_to_update_triggers'] = force_update_triggers or changed_table
    params['lock_id'] = PG_LOCK_ID

    execute_sql_file(settings.DEFAULT_DB_ALIAS, os.path.join(SQL_FILES_DIR, 'configure_audit_log.sql'), params)


def get_all_table_names(db_alias: str, schema: str) -> Set[str]:
    """Возвращает перечень наименований всех существующих таблиц в БД в схеме."""
    with connections[db_alias].cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """,
            [schema],
        )
        rows = cursor.fetchall()

    return {row[0] for row in rows}


def get_need_to_log_table_names() -> Set[str]:
    """Возвращает перечень наименований таблиц моделей, которые отмечены как отслеживаемые."""
    table_names = {model._meta.db_table for model in apps.get_models() if getattr(model, 'need_to_log', False)}

    return table_names


def get_table_names_for_app_labels(app_labels: Iterable[str]) -> Set[str]:
    """Возвращает множество с именами таблиц для указанных приложений."""
    tables = set()
    for app_label in app_labels:
        try:
            app_config = apps.get_app_config(app_label)
            tables.update(model._meta.db_table for model in app_config.get_models())
        except LookupError:
            continue

    return tables


def update_or_create_tables(need_to_log_table_names: Iterable[str]) -> bool:
    """Создаёт записи Table для отслеживаемых таблиц, либо меняет флаг logged.

    Возвращает признак были ли созданы или изменены записи.
    """
    Table = apps.get_model('audit_log', 'Table')

    need_to_log_table_names = set(need_to_log_table_names)
    existed_table_names = set(Table.objects.filter(schema='public').values_list('name', flat=True))

    # Таблицы сервисных приложений, которые не должны отслеживаться аудит-логом
    allowed_service_apps_labels = getattr(settings, 'ALLOWED_SERVICE_APPS_LABELS', [])
    service_table_names = get_table_names_for_app_labels(allowed_service_apps_labels)

    # Проверка конфликтных таблиц: должны логироваться, но находятся в сервисных приложениях
    conflicting_tables = need_to_log_table_names & service_table_names
    if conflicting_tables:
        tables = ', '.join(sorted(conflicting_tables))
        error_msg = (
            f'Невозможно включить логирование для сервисных таблиц: {tables}. '
            'Исключите их из отслеживания или перенесите таблицы в основную БД.'
        )
        logger_error(error_msg)
        raise ValueError(error_msg)

    to_create_table_names = need_to_log_table_names - existed_table_names
    to_disable_table_names = existed_table_names - need_to_log_table_names

    # Включение логирования для существующих записей таблиц
    enabled_count = Table.objects.filter(
        schema='public',
        name__in=need_to_log_table_names,
        logged=False,
    ).update(
        logged=True,
    )

    # Отключение логирования для существующих записей таблиц
    disabled_count = Table.objects.filter(
        schema='public',
        name__in=to_disable_table_names,
        logged=True,
    ).update(
        logged=False,
    )

    # Создание записей таблиц, которые теперь отслеживаемые
    Table.objects.bulk_create(
        objs=[Table(name=table, schema='public') for table in to_create_table_names],
    )

    if to_create_table_names or enabled_count or disabled_count:
        changed = True
    else:
        changed = False

    return changed


def clear_audit_logs(
    chunk_size: int = 1_000,
    db_alias: str = settings.SERVICE_DB_ALIAS,
) -> Dict[str, int]:
    """Удаляет записи AuditLog для таблиц, которые больше не отслеживаются."""
    Table = apps.get_model('audit_log', 'Table')
    AuditLog = apps.get_model('audit_log', 'AuditLog')

    # Имена удаленных таблиц с кол-вом удаленных записей audit_log
    deleted_table_counts = {}

    not_logged_tables = Table.objects.filter(
        schema='public',
        logged=False,
    ).only('id', 'name')

    # SQL-запрос для удаления ограниченного кол-ва записей (chunk) из AuditLog
    delete_audit_logs_sql = """
        WITH deleted AS (
            DELETE FROM {audit_log_table}
            WHERE id = ANY(ARRAY(
                SELECT id FROM {audit_log_table}
                WHERE table_id=%(table_id)s
                LIMIT %(chunk_size)s
                ))
            RETURNING id
        )
        SELECT count(*) FROM deleted;
    """.format(audit_log_table=AuditLog._meta.db_table)

    # SQL-запрос для удаления записи из Table
    delete_table_sql = """
        DELETE FROM {table} WHERE "{table}"."id" = %(table_id)s
    """.format(table=Table._meta.db_table)

    for table in not_logged_tables:
        deleted_total = 0
        with connections[db_alias].cursor() as cursor:
            sql_params = {
                'table_id': table.id,
                'chunk_size': chunk_size,
            }
            while True:
                cursor.execute(delete_audit_logs_sql, sql_params)
                deleted = cursor.fetchone()[0]
                if not deleted:
                    break

                deleted_total += deleted

            cursor.execute(delete_table_sql, sql_params)

        deleted_table_counts[table.name] = deleted_total

    return deleted_table_counts


def is_initialized(database_alias):
    """Проверяет, проинициализированы ли средства журналирования.

    :param str database_alias: Алиас БД, в которой будет проверяться наличие
        средств журналирования.

    :rtype: bool
    """
    # Проверка наличия схемы audit.
    with closing(connections[database_alias].cursor()) as cursor:
        cursor.execute("select 1 from pg_namespace where nspname = 'audit'")
        if cursor.fetchone() is None:
            return False

    # Проверка наличия таблицы postgresql_errors
    with closing(connections[database_alias].cursor()) as cursor:
        cursor.execute(
            'select 1 from information_schema.tables where table_schema = %s and table_name = %s',
            ('audit', 'postgresql_errors'),
        )
        if cursor.fetchone() is None:
            return False

    # Проверка наличия всех функций схемы.
    function_names = (
        'get_param',
        'get_table_id',
        'on_modify',
        'is_valid_options',
        'str_to_ip',
        'log_postgres_error',
        'drop_all_triggers',
        'create_triggers',
    )
    for function_name in function_names:
        with closing(connections[database_alias].cursor()) as cursor:
            cursor.execute(
                'select 1 '
                'from pg_proc proc '
                'inner join pg_namespace ns on ns.oid = proc.pronamespace '
                'where proc.proname = %s and ns.nspname = %s '
                'limit 1',
                [function_name, 'audit'],
            )
            if cursor.fetchone() is None:
                return False

    return True


def check_connection_fdw():
    """Проверяет подключение к сервисной БД через PostgreSQL FDW.

    :returns: Кортеж из двух элементов: первый указывает на работоспособность
        подключения (``True`` - есть, ``False`` - нет подключения), второй --
        содержит текст ошибки, если подключения нет.
    :rtype: tuple
    """
    with closing(connection.cursor()) as cursor:
        try:
            cursor.execute('SELECT 1 FROM "audit"."audit_log" LIMIT 1')
        except Exception as error:
            return False, str(error)
        else:
            return True, None


@atomic
def execute_sql_file(database_alias, file_name, params=None):
    """Исполняет SQL-скрипт, из файла по указанному пути."""
    cursor = connections[database_alias].cursor()

    file_path = path.join(path.dirname(__file__), file_name)
    with open(file_path, 'r') as f:
        file_contents = f.read()

    if params:
        file_contents = file_contents.format(**params)

    cursor.execute(file_contents)


def get_db_connection_params():
    """Возвращает параметры подключения к сервисной БД."""
    target_db_conf = settings.DATABASES[settings.SERVICE_DB_ALIAS]
    return dict(
        host=target_db_conf['HOST'],
        dbname=target_db_conf['NAME'],
        port=target_db_conf['PORT'],
        user=target_db_conf['USER'],
        password=target_db_conf['PASSWORD'],
    )


@atomic()
def set_db_param(key, value):
    """Устанавливает параметры в custom settings postgresql."""
    cursor = connection.cursor()
    if value:
        value = str(value)
    else:
        value = ''

    sql = 'SELECT set_config(%s, %s, False);'
    cursor.execute(sql, (key, value))


def get_ip(request):
    """Возвращает ip источника запроса.

    :param request: запрос
    :type django.http.HttpRequest

    :return IP адрес
    :rtype str or None
    """
    assert isinstance(request, HttpRequest), type(request)

    # Берем ip из X-Real-IP, если параметр установлен.
    # Вернет адрес первого недоверенного прокси.
    http_x_real_ip = request.META.get('HTTP_X_REAL_IP', None)
    if http_x_real_ip is not None:
        return http_x_real_ip

    # Берем первый ip из X-Forwarded-For, если параметр установлен.
    # Вернет первый адрес в цепочке прокси.
    x_forward_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forward_for is not None:
        x_forward_ip, _, _ = x_forward_for.partition(',')
        return x_forward_ip.strip()

    return request.META.get('REMOTE_ADDR', None)


def make_hstore_filter(field, value):
    """Создает lookup фильтр из строки.

    :param str field: название поля (type hstore).
    :param str value: значение, по которому фильтруется queryset.
    Если строка, то разбивается на отдельные слова.
    """
    result = reduce(and_, (Q(**{f'{field}__values__icontains': x}) for x in value.split(' ')))
    return result


class ModelRegistry:
    """Реестр моделей Django по имени таблицы.

    Позволяет получать класс модели по имени таблицы из базы данных.
    Использует кэшируемое свойство для построения соответствия
    между именами таблиц и их моделями, включая автоматически
    создаваемые модели, но исключая proxy-модели.
    """

    @cached_property
    def table_model(self):
        return {
            model._meta.db_table: model
            for model in apps.get_models(include_auto_created=True)
            if not (model._meta.proxy)
        }

    def get_model(self, table_name):
        return self.table_model.get(table_name)


model_registry = ModelRegistry()


def get_model_choices(excluded=None):
    """Список выбора для комбобокса.

    Ключ - id таблицы, отображаемое значение - name
    и verbose_name модели.
    """
    total_exclude = EXCLUDED_TABLES
    table_class = apps.get_model('audit_log', 'Table')
    if excluded:
        total_exclude += tuple(excluded)
    tables = (table for table in table_class.objects.iterator() if (table.schema, table.name) not in total_exclude)

    result = sorted(((table.id, get_table_name(table)) for table in tables), key=lambda x: x[1])

    return tuple(result)


def _get_m2m_model_fields(model):
    """Возвращает поля автоматически созданной m2m таблицы.

    :return Два поля типа ForeignKey или None, если таблица не
            соответствует автоматически созданной.
    """
    result = [field for field in model._meta.get_fields() if isinstance(field, related.ForeignKey)]
    if len(result) == 2:
        return result


def get_table_name(table):
    """Возвращает имя таблицы в понятном пользователю виде."""
    model = get_model_by_table(table)
    if model:
        class_name = model.__name__
        verbose_name = model._meta.verbose_name.capitalize()
        if model._meta.auto_created:
            fields = _get_m2m_model_fields(model)
            if fields:
                names = [get_related(f).parent_model._meta.verbose_name for f in fields]
                verbose_name = 'Связь {}, {}'.format(names[0], names[1])

        return f'{verbose_name} - {class_name}'
    else:
        return table.name


def get_model_by_table(table):
    """Возвращает класс модели по имени таблицы."""
    assert isinstance(table, apps.get_model('audit_log', 'Table'))
    return model_registry.get_model(table.name)


def get_audit_log_context(request):
    """Возвращает параметры контекста журналирования изменений."""
    result = {}

    current_user = ioc.get('get_current_user')(request)
    if current_user and current_user.is_authenticated:
        ContentType = apps.get_model('contenttypes', 'ContentType')

        result['user_id'] = current_user.id
        content_type = ContentType.objects.get_for_model(current_user)
        result['user_type_id'] = content_type.id
    else:
        result['user_id'] = result['user_type_id'] = 0

    result['ip'] = get_ip(request)

    return result


def get_dict_auto_now_fields_by_model() -> dict[str, list[str]]:
    """Возвращает словарь с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.

    Returns:
        Словарь, где ключ это название таблицы, а значение это список названий полей имеющими auto_now=True.
    """
    auto_now_fields = {}

    for model in apps.get_models():
        if not getattr(model, 'need_to_log', False):
            continue

        auto_now_field_names = [
            field.name
            for field in model._meta.get_fields()
            if getattr(field, 'auto_now', False)
        ]

        if auto_now_field_names:
            auto_now_fields[model._meta.db_table] = auto_now_field_names

    return auto_now_fields


def get_json_auto_now_fields_by_model() -> Json:
    """Возвращает Json с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.

    Returns:
        Json, где ключ это название таблицы, а значение это список названий полей имеющими auto_now=True.
    """
    return Json(get_dict_auto_now_fields_by_model())
