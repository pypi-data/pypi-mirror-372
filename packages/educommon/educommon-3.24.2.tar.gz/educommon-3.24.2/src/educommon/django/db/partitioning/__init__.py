"""Средства для реализации партиционирования таблиц в СУБД PostgreSQL.

В настоящее время поддерживается только помесячное разбиение таблиц БД на
разделы.

Для использования партиционирования таблиц необходимо выполнить следующие
шаги:

1. Проинициализировать средства партиционирования для базы данных. Для
   этого следует выполнить функцию *init*. Функция должна выполняться
   ОДИН раз для КАЖДОЙ базы данных, используемых системой. В результате
   выполнения функции в указанной БД будут созданы необходимые функции
   для поддержки партиционирования.
2. Включить партиционирование для конкретных таблиц с помощью функции
   *set_partitioning*. В результате для указанной таблицы будут созданы
   необходимые триггеры. После этого при добавлении/редактировании записей
   партиционированной таблицы записи будут размещаться в разделах таблицы.
   Если соответствующие разделы отсутствуют, то они будут создаваться
   автоматически.
3. При необходимости, можно выполнить перенос записей из родительской таблицы в
   ее разделы. Для этого предназначена функция *split_table*. Для снижения
   нагрузки на СУБД записи переносятся по отдельности, при этом можно задачть
   время ожидания между переносом каждой записи.

После выполнения указанных действий с партиционированной таблицей можно
продолжать работать как с обычной таблицей.

Подробнее о партиционировании можно почитать в дкоументации PostgreSQL
(раздел 5.9).
"""

import re
from contextlib import (
    closing,
)
from os import (
    path,
)
from time import (
    sleep,
)
from types import (
    MethodType,
)
from typing import (
    Optional,
)

from django.conf import (
    settings,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.db import (
    connections,
    router,
)
from django.db.models.sql.compiler import (
    cursor_iter,
)
from django.db.utils import (
    DEFAULT_DB_ALIAS,
)
from django.utils.functional import (
    cached_property,
)

from m3_django_compat import (
    ModelOptions,
    commit_unless_managed,
)

from educommon.django.db.observer import (
    ModelObserverBase,
)
from educommon.django.db.partitioning.const import (
    CURSOR_ITERSIZE,
    INSERT_CURSOR_ITERSIZE,
    PARTITION_TRIGGERS_FUNCTIONS,
)


_MESSAGE_PREFIX = '[Partitioning] '


def _check_system_settings(database_alias):
    """Проверка конфигурации системы. Перечень проверок:

    1. Указанный алиас БД есть в конфигурации системы.
    2. Указанная БД управляется СУБД PostgreSQL.
    """
    if database_alias not in settings.DATABASES:
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}"{database_alias}" database not found.')

    database_engine = settings.DATABASES[database_alias]['ENGINE']
    if database_engine not in (
        'django.db.backends.postgresql_psycopg2',
        'django.db.backends.postgresql',
    ):
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}only PostgreSQL DBMS supported.')


def is_initialized(database_alias):
    """Проверяет, проинициализированы ли средства партиционирования.

    :param str database_alias: Алиас БД, в которой будет проверяться наличие
        средств партиционирования.

    :rtype: bool
    """
    # Проверка наличия схемы partitioning.
    with closing(connections[database_alias].cursor()) as cursor:
        cursor.execute("select 1 from pg_namespace where nspname = 'partitioning'")
        if cursor.fetchone() is None:
            return False

    # Проверка наличия всех функций схемы.
    function_names = PARTITION_TRIGGERS_FUNCTIONS
    for function_name in function_names:
        with closing(connections[database_alias].cursor()) as cursor:
            cursor.execute(
                'select 1 '
                'from pg_proc proc '
                'inner join pg_namespace ns on ns.oid = proc.pronamespace '
                "where proc.proname = %s and ns.nspname = 'partitioning' "
                'limit 1',
                [function_name],
            )
            if cursor.fetchone() is None:
                return False

    return True


def _execute_sql_file(database_alias, file_name, params=None):
    """Выполняет SQL-скрипт из файла с подстановкой параметров."""
    cursor = connections[database_alias].cursor()

    file_path = path.join(path.dirname(__file__), file_name)
    with open(file_path, 'r') as f:
        file_contents = f.read()

    if params:
        file_contents = file_contents.format(**params)

    file_contents = file_contents.replace('%', '%%').replace('%%%%', '%')

    cursor.execute(file_contents)

    commit_unless_managed(database_alias)


def init(database_alias=DEFAULT_DB_ALIAS, force=False):
    """Осуществляет инициализацию средств партиционирования таблиц БД.

    Под средствами партиционирования понимается набор функций, создаваемых
    в указанной базе данных. С помощью этих функций реализуется автоматическое
    создание разделов таблиц и управление записями в разделах.

    :param str database_alias: Алиас базы данных, в которой нужно
        инициализировать средства партиционирования.

    :raises django.core.exceptions.ImproperlyConfigured: если указанная БД
        размещена в СУБД, отличной от PostgreSQL.
    """
    _check_system_settings(database_alias)

    if not force and is_initialized(database_alias):
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}always initialized')

    _execute_sql_file(
        database_alias,
        'partitioning.sql',
        dict(
            view_name_suffix=PartitioningObserver.view_name_suffix,
        ),
    )


def _get_model_params(model):
    """Возвращает параметры модели: алиас БД, имя таблицы и имя PK-колонки."""
    database_alias = router.db_for_write(model)
    table_name = model._meta.db_table
    pk_column_name = model._meta.pk.name

    return database_alias, table_name, pk_column_name


def is_model_partitioned(model):
    """Возвращает True, если для модели включено партиционирование.

    :rtype: bool
    """
    database_alias, table_name, _ = _get_model_params(model)

    with closing(connections[database_alias].cursor()) as cursor:
        cursor.execute("select 1 from pg_namespace where nspname = 'partitioning' limit 1")
        if cursor.fetchone() is None:
            return False

        cursor.execute('select partitioning.is_table_partitioned(%s)', (table_name,))

        return cursor.fetchone()[0]


def set_partitioning_for_model(model, column_name, force=False):
    """Включает партиционирование указанной таблицы или модели.

    Для включения партиционирования для указанной таблицы создаются триггеры,
    вызывающие функции управления партиционированием. Перед включением
    партиционирования для таблиц БД должны быть проинициализированы средства
    партиционирования с помощью функции init().

    :param model: Модель, для которой включается партиционирование.
        Алиас используемой БД определяется с помощью метода db_for_write
        роутера Django.
    :param str column_name: Имя поля модели, содержащее значение даты. Это
        значение будет определять раздел таблицы, в который будет помещена
        запись.

    :raises m3_django_compat.exceptions.FieldDoesNotExist: если модель *model* не
        содержит поля *column_name*
    """
    database_alias, table_name, pk_column_name = _get_model_params(model)
    view_name_suffix = PartitioningObserver.view_name_suffix

    # для проверки наличия поля в модели
    ModelOptions(model).get_field(column_name)

    if not force and not is_initialized(database_alias):
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}not initialized')

    _execute_sql_file(database_alias, 'triggers.sql', locals())


def split_table(model, column_name: str, timeout: float = 0, cursor_itersize: Optional[int] = None):
    """Переносит записи из разбиваемой таблицы в ее разделы.

    Недостающие разделы будут созданы автоматически.

    :param model: Модель, записи которой нужно перенести в разделы. Алиас
        используемой БД определяется с помощью метода db_for_write роутера
        Django.
    :param str column_name: Имя поля модели, содержащее значение даты. Это
        значение будет определять раздел таблицы, в который будет помещена
        запись.
    :param float timeout: Время ожидания в секундах  между переносом записей
        (можно использовать для снижения нагрузки на СУБД).
    :param int cursor_itersize: Количество записей, попадающих в итератор курсора бд
        при запросе разбиения таблиц.

    :raises m3_django_compat.exceptions.FieldDoesNotExist: если модель *model* не
        содержит поля *column_name*
    """
    database_alias, table_name, pk_column_name = _get_model_params(model)

    if not cursor_itersize:
        cursor_itersize = INSERT_CURSOR_ITERSIZE

    # для проверки наличия поля в модели
    ModelOptions(model).get_field(column_name)

    if not is_initialized(database_alias):
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}not initialized')

    if not is_model_partitioned(model):
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}not applyed for {table_name}')

    if settings.DATABASES[database_alias]['DISABLE_SERVER_SIDE_CURSORS']:
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}split_table does not support DISABLE_SERVER_SIDE_CURSORS.')

    connection = connections[database_alias]

    ids_cursor = connection.chunked_cursor()
    ids_cursor.execute(
        # сырой SQL используется для того, чтобы извлечь только записи
        # из родительской таблицы без записей, уже размещенных в разделах
        'select {pk_column_name} from only {table_name}'.format(**locals())
    )

    move_cursor = connection.cursor()

    results = cursor_iter(ids_cursor, connection.features.empty_fetchmany_value, 1, cursor_itersize)
    for rows in results:
        # Если всего одна запись, то используем строку, чтобы не получать ошибку sql-запроса на обновление
        if len(rows) == 1:
            pk_column_values = f'{rows[0]}'.replace(',', '')
        else:
            pk_column_values = tuple(pkv for (pkv,) in rows)
        # Этот update выполняется для того, чтобы сработала триггерная
        # функция partitioning.before_update.
        move_cursor.execute(
            (
                'update {table_name} '
                'set {pk_column_name} = {pk_column_name} '
                'where {pk_column_name} in {pk_column_values}'
            ).format(**locals())
        )

        if timeout:
            sleep(timeout)


def clear_table(model, column_name: str, column_value: str, timeout=0, cursor_itersize: Optional[int] = None):
    """Удаление записей по условию.

    С помощью данной команды удаляются записи из основной (не секционированной)
    таблицы, у которых значение в column_name меньше значения из column_value.

    :param model: Модель, записи которой нужно удалить. Алиас
        используемой БД определяется с помощью метода db_for_write роутера
        Django.
    :param str column_name: Имя поля модели, содержащее значение для условия
        удаления записи.
    :param str column_value: Значение, до начала которого по полю column_name
        будут удаляться записи.
    :param float timeout: Время ожидания в секундах  между удалением 100
        записей (можно использовать для снижения нагрузки на СУБД).
    :param int cursor_itersize: Количество записей, попадающих в итератор курсора бд
        при запросе удаления таблиц.
    """
    database_alias, table_name, pk_column_name = _get_model_params(model)

    if not cursor_itersize:
        cursor_itersize = CURSOR_ITERSIZE

    connection = connections[database_alias]

    if settings.DATABASES[database_alias]['DISABLE_SERVER_SIDE_CURSORS']:
        raise ImproperlyConfigured(f'{_MESSAGE_PREFIX}clear_table does not support DISABLE_SERVER_SIDE_CURSORS.')

    ids_cursor = connection.chunked_cursor()
    ids_cursor.execute(
        # сырой SQL используется для того, чтобы извлечь только записи
        # из родительской таблицы без записей, уже размещенных в разделах
        "select {pk_column_name} from only {table_name} where {column_name} < '{column_value}'".format(**locals())
    )

    delete_cursor = connection.cursor()

    results = cursor_iter(
        ids_cursor,
        connection.features.empty_fetchmany_value,
        1,
        cursor_itersize,
    )
    for rows in results:
        # Если всего одна запись, то используем строку, чтобы не получать ошибку sql-запроса на удаление
        if len(rows) == 1:
            pk_column_values = f'{rows[0]}'.replace(',', '')
        else:
            pk_column_values = tuple(pkv for (pkv,) in rows)
        delete_cursor.execute(
            ('delete from {table_name} where {pk_column_name} in {pk_column_values}').format(**locals())
        )

        if timeout:
            sleep(timeout)


def get_model_partitions(model):
    """Возвращает названия разделов таблицы.

    :param model: Модель, записи которой перенесены в разделы. Алиас
        используемой БД определяется с помощью метода db_for_write роутера
        Django.

    :rtype: tuple
    """
    database_alias, table_name, _ = _get_model_params(model)
    connection = connections[database_alias]
    cursor = connection.cursor()

    cursor.execute(
        'select inhrelid::regclass::text as partition_name '
        'from pg_inherits '
        "where inhparent = '{}'::regclass::oid "
        'order by partition_name'.format(table_name)
    )

    return tuple(partition_name for (partition_name,) in cursor)


def reset_partition_constraints(model, column_name, partition_name):
    """Переустанавливает ограничения для указанного раздела.

    :param model: Модель, записи которой перенесены в разделы. Алиас
        используемой БД определяется с помощью метода db_for_write роутера
        Django.
    :param str column_name: Имя поля модели, содержащее значение даты. Это
        значение определяет раздел таблицы, в который будет помещена запись.
    :param str partition_name: Имя раздела.
    """
    database_alias, table_name, _ = _get_model_params(model)

    r = re.match('^' + table_name + '_y(\d{4})m(\d{2})$', partition_name)
    year, month = list(map(int, r.groups()))

    connection = connections[database_alias]
    cursor = connection.cursor()

    cursor.execute(
        'select partitioning.set_partition_constraint(%s, %s, %s, %s)', (partition_name, column_name, year, month)
    )

    commit_unless_managed(database_alias)


def drop_partitions_before_date(model, date):
    """Удаление старых партиций модели вплоть до месяца переданной даты.

    :param Model: модель
    :type Model: django.db.models.base.ModelBase
    :param date: дата, до которой необходимо осуществить удаление партиций
    :type date: datetime.date or datetime.datetime
    """
    if is_model_partitioned(model):
        database_alias, table_name, _ = _get_model_params(model)
        all_partitions = get_model_partitions(model)
        filter_partition_name = f'{table_name}_y{date.year}m{date.strftime("%m")}'
        filtered_partitions = filter(lambda p: (p <= filter_partition_name), all_partitions)
        connection = connections[database_alias]
        with connection.cursor() as cursor:
            for partition in filtered_partitions:
                cursor.execute('DROP TABLE IF EXISTS {};'.format(partition))


def set_partitioned_function_search_path(database_alias: str, schema_names: Optional[str] = None):
    """ "Проставляет параметры поиска для существующих функций партицирования.

    Это необходимо для корректной работы с таблицами к которым обращаются как к внешним через postgres_fdw.
    """
    schema_names = schema_names or 'public'
    _execute_sql_file(
        database_alias,
        'partitioning_set_search_path.sql',
        dict(
            schema_names=schema_names,
        ),
    )


class PartitioningObserver(ModelObserverBase):
    """Оптимизирует операции вставки в партиционированные таблицы.

    При добавлении записей в партиционированную таблицу добавление происходит
    следующим образом:

        1. добавляется запись в основную таблицу;
        2. такая же запись добавляется в соответствующий раздел таблицы;
        3. эта же запись удаляется из основной таблицы.

    Добавление записи в основную таблицу необходимо для того, чтобы корректно
    работал Django ORM - после вставки считывается ``id`` созданного объекта, а
    возвращается он только если добавить запись в основную таблицу.

    Для обхода этой проблемы можно использовать представление, которое
    создается для каждой партиционированной таблицы. Данный наблюдатель перед
    вставкой меняет значение параметра ``db_table`` на имя представления,
    чтобы вставка происходила в представление, а не в основную таблицу. После
    вставки значение ``db_table`` восстанавливается.
    """

    view_name_suffix = '__partitioning_view'

    __models = {}

    @cached_property
    def _partitioning_ready(self):
        """Кэширует информацию о том, проинициализировано ли партиционирование в БД."""
        return {database_alias: is_initialized(database_alias) for database_alias in connections}

    def _is_observable(self, model):
        """Возвращает True только для моделей с включенным партиционированием.

        :rtype: bool
        """
        if not self._partitioning_ready[router.db_for_write(model)]:
            return False

        if model not in self.__models:
            self.__models[model] = is_model_partitioned(model)

        return self.__models[model]

    def pre_save(self, instance, context, **kwargs):
        """Оборачивает метод _save_table объекта для подмены имени таблицы.

        После замены метода ``_save_table`` ДО вызова оригинального метода
        в ``instance._meta.db_table`` записывается имя представления, через
        которое будет выполняться добавление записи, а ПОСЛЕ вызова метода
        значение ``db_table`` восстанавливается.
        """
        if instance.pk is None:
            instance_save_table = instance._save_table

            def wrapper(self, *args, **kwargs):
                suffix = PartitioningObserver.view_name_suffix
                db_table = self._meta.db_table
                try:
                    self._meta.db_table += suffix
                    instance_save_table(*args, **kwargs)
                finally:
                    self._meta.db_table = db_table

            instance._save_table = MethodType(wrapper, instance)

    def post_save(self, instance, context, **kwargs):
        """Восстанавливает метод _save_table объекта."""

        if '_save_table' in instance.__dict__:
            del instance.__dict__['_save_table']
