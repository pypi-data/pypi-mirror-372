"""
Команда переноса данных из локального AuditLog'а в educommon'овский.
"""
import sys
from datetime import (
    datetime as dt,
)
from typing import (
    TYPE_CHECKING,
    Generator,
    Optional,
    Type,
)

from dateutil.relativedelta import (
    relativedelta,
)
from django.apps import (
    apps,
)
from django.core.management.base import (
    BaseCommand,
    OutputWrapper,
)
from django.db.models import (
    ManyToManyField,
    Model,
)

from educommon.audit_log.models import (
    AuditLog,
    Table,
)
from educommon.audit_log.utils import (
    get_model_by_table,
)


if TYPE_CHECKING:
    from django.db.models.query import (
        QuerySet,
    )


PROJECT_LOCAL_AUDIT_LOG_APP = {
    'eduschl': 'web_edu_audit_log',
    'edussuz': 'audit_log_ssuz',
    'edukndg': 'audit_log_kndg'
}
LOG_OPERATION_MAP = {
    'N': AuditLog.OPERATION_CREATE,
    'I': AuditLog.OPERATION_CREATE,
    'U': AuditLog.OPERATION_UPDATE,
    'D': AuditLog.OPERATION_DELETE,
}
LOCAL_AUDIT_LOG_MODEL_NAME = 'Log'
DEFAULT_DATE_YEAR_RANGE = 1


class BulkSaver:
    """Контекстный менеджер для группового сохранения записей."""

    def __init__(self, bulk_size: int) -> None:
        self._bulk_size = bulk_size
        self._bulk_list = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._bulk_save()

    def save(self, audit_log: AuditLog):
        self._bulk_list.append(audit_log)
        if len(self._bulk_list) >= self._bulk_size:
            self._bulk_save()

    def _bulk_save(self):
        AuditLog.objects.bulk_create(self._bulk_list)
        self._bulk_list.clear()


class LogMigrator:
    """Класс для миграции логов из локального AuditLog'а в educommon'овский."""

    def __init__(self, stdout: OutputWrapper):
        """Инициализация."""
        self._stdout = stdout

    @staticmethod
    def get_model(model_name: str) -> Optional[Type[Model]]:
        """Bозвращает класс модели по имени."""
        for mod in apps.get_models():
            if mod.__name__ == model_name and mod.__module__.find('django') == -1:
                return mod

        return None

    def _get_educommon_table(self, model_name: str, create: bool = False) -> tuple[Optional[Table], str]:
        """Возвращает таблицу, отслеживаемую системой аудита."""
        model_cls = self.get_model(model_name)

        if not model_cls:
            return None, f'Не найдено Django моделей с именем {model_name}'
        try:
            return Table.objects.get(name=model_cls._meta.db_table), ''
        except Table.DoesNotExist:
            is_loggable_mixin_use = getattr(model_cls, 'need_to_log', False)

            if not is_loggable_mixin_use:
                return None, (
                    f'В таблицу {model_name} не добавлен LoggableModelMixin'
                )

            if create:
                return Table.objects.create(
                    name=model_cls._meta.db_table,
                    schema='public',
                    logged=True,
                ), ''

        return None, (
            f'В educommon не найдено таблицы с именем {model_cls._meta.db_table}. '
            'Таблицу можно создать, указав флаг force_create_educommon_table'
        )

    @staticmethod
    def _get_fields_map(table: Table) -> dict[str, str]:
        """Возвращает словарь соответствия поля модели и его названия."""
        return {
            field.name: field.attname
            for field in get_model_by_table(table)._meta.get_fields()
            if field.concrete and not isinstance(field, ManyToManyField)
        }

    def _get_local_audit_log_query(
        self,
        project: str,
        model_name: str,
        date_from: dt,
        date_to: dt
    ) -> tuple[Optional['QuerySet'], str]:
        """Возвращает QuerySet с локальными логами."""
        if not (audit_log_app_name := PROJECT_LOCAL_AUDIT_LOG_APP.get(project)):
            return None, 'Неизвестное название проекта.'

        audit_log_model = apps.get_model(audit_log_app_name, LOCAL_AUDIT_LOG_MODEL_NAME)

        if not audit_log_model:
            return None, 'Не найдена локальная модель логов.'

        return audit_log_model.objects.filter(
            model=model_name,
            date__lt=date_to,
            date__gte=date_from,
        ), ''

    @staticmethod
    def _prepare_local_logs(query: 'QuerySet') -> Generator[tuple, None, None]:
        """Подготавливает данные логов для дальнейшего использования."""
        query = query.values_list(
            'user_id',
            'date',
            'model_id',
            'object_json',
            'ip',
            'operation',
        ).order_by(
            'date',
        )
        for user_id, date_, model_id, object_json, ip, operation in query.iterator():
            yield user_id, date_, model_id, ip, operation, object_json

    @staticmethod
    def _prepare_object_dict(fields_map: dict, object_dict: Optional[dict]) -> dict[str, str]:
        """Подготавливает данные о объекте для AuditLog.

        В основном требуется только для переименования ForeignKey-полей вида
        `period` в `period_id`
        """
        if not object_dict:
            return {}

        filled_field_names = set(fields_map).intersection(object_dict)
        return {
            fields_map[field_name]: object_dict[field_name]
            for field_name in filled_field_names
        }

    def process(
        self,
        model_name: str,
        project: str,
        bulk_save_size: int,
        date_from: Optional[dt] = None,
        date_to: Optional[dt] = None,
        force_create_educommon_table: bool = False,
    ):
        """Перенос записей из локального AuditLog'а в educommon."""
        table, error = self._get_educommon_table(model_name, force_create_educommon_table)
        if error:
            self._stdout.write(error)
            return

        fields_map = self._get_fields_map(table)

        first_audit_log_date = self._get_first_audit_log_date(table)
        date_to = dt.combine((date_to or dt.today()), dt.max.time())

        date_to = min(date_to, first_audit_log_date)
        date_from = date_from or (date_to - relativedelta(years=DEFAULT_DATE_YEAR_RANGE))

        self._stdout.write(
            f'Поиск записей в локальном Auditlog с {date_from} по {date_to}... ',
            ending='',
        )

        local_audit_log_query, error = self._get_local_audit_log_query(
            project=project,
            model_name=model_name,
            date_from=date_from,
            date_to=date_to,
        )
        if error:
            self._stdout.write(error)
            return

        total_count = local_audit_log_query.count()
        self._stdout.write(f'Найдено {total_count} запись(ей).')

        local_logs = self._prepare_local_logs(local_audit_log_query)
        self._stdout.write(f'Подготовка к работе... (занимает некоторое время)', ending='\r',)
        with BulkSaver(bulk_save_size) as bulk:
            for count, (user_id, date_, object_id, ip, operation, data_dict) in enumerate(local_logs, start=1):
                object_dict = self._prepare_object_dict(fields_map, data_dict[0].get('fields', {}))

                operation = LOG_OPERATION_MAP[operation]

                if operation == AuditLog.OPERATION_UPDATE:
                    changes = object_dict
                else:
                    # Если объект быз создан или удалён, то изменений нет.
                    changes = {}

                bulk.save(AuditLog(
                    user_id=user_id,
                    ip=ip,
                    time=date_,
                    table_id=table.id,
                    data=object_dict,
                    changes=changes,
                    object_id=object_id,
                    operation=operation,
                ))

                self._stdout.write(
                    f'Обработано {(count / total_count) * 100:5.2f}% запись(ей)... (Последняя от {date_})',
                    ending='\r',
                )

    def _get_first_audit_log_date(self, table: str) -> dt:
        """Возвращает первую дату/время появления audit_log по переданной таблице.

        В случае отсуствия логов прекращает выполнение команды за отсутствием данных для переноса.
        """
        first_log = AuditLog.objects.filter(
            table=table,
        ).order_by('time').first()

        if not first_log:
            self._stdout.write('Не найдены локальные логи переданной модели. Завершение команды.')
            sys.exit()

        return first_log.time


class Command(BaseCommand):
    """Команда переноса данных из локального AuditLog'а в educommon'овский."""

    help = (
        'Команда для переноса данных из локального AuditLog`а в educommon.audit_log.models.AuditLog.\n'
        'Пример использования:\n'
        'audit_log_migrate_data --project eduschl --model_name Mark --date_from 10.10.2024'
    )

    @staticmethod
    def _get_date(date_string: str) -> dt:
        return dt.strptime(date_string, '%d.%m.%Y')

    def add_arguments(self, parser):
        parser.add_argument(
            '--model_name',
            type=str,
            help='Название модели из локального лога',
        )
        parser.add_argument(
            '--project',
            type=str,
            help='Наименование (код) продукта, в котором применяется команда',
        )
        parser.add_argument(
            '--date_from',
            type=self._get_date,
            required=False,
            help=(
                'Дата, с которой будут переноситься логи в формате ДД.ММ.ГГГГ. '
                'Значение по умолчанию - на год раньше даты, указанной в --date_to'
            ),
        )
        parser.add_argument(
            '--date_to',
            type=self._get_date,
            required=False,
            help=(
                'Дата, по которую будут переноситься логи в формате ДД.ММ.ГГГГ.'
                'Значение по умолчанию - текущая дата.'
            ),
        )
        parser.add_argument(
            '--force_create_educommon_table',
            action='store_true',
            default=False,
            help=(
                'Создание отслеживаемой таблицы (educommon.audit_log.models.Table), '
                'если она еще не была создана'
            ),
        )
        parser.add_argument(
            '--bulk_save_size',
            type=int,
            default=500,
            help='По сколько записей за раз будет сохраняться. По умолчанию 500',
        )

    def handle(
        self,
        model_name: str,
        project: str,
        date_from: Optional[dt],
        date_to: Optional[dt],
        force_create_educommon_table: bool,
        bulk_save_size: int,
        *args,
        **options,
    ):
        """Выполнение переноса записей."""
        self.stdout.write('Начало работы команды.')
        LogMigrator(self.stdout).process(
            model_name=model_name,
            project=project,
            date_from=date_from,
            date_to=date_to,
            force_create_educommon_table=force_create_educommon_table,
            bulk_save_size=bulk_save_size,
        )

        self.stdout.write(self.style.SUCCESS('Выполнение команды завершено.'))
