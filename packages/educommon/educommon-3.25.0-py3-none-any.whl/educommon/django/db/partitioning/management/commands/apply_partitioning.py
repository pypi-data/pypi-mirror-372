from django.core.exceptions import (
    FieldDoesNotExist,
)
from django.core.management.base import (
    CommandError,
)
from django.db import (
    router,
)

from m3_django_compat import (
    BaseCommand,
    get_model,
)

from educommon.django.db import (
    partitioning,
)
from educommon.logger import (
    info as logger_info,
)


class Command(BaseCommand):
    """Применяет партицирование к таблице переданной модели.

    Команда, если это необходимо, сперва инициализирует средства партицирования
    для БД, в которой хранится переданная модель, а затем создает необходимые
    триггеры. Подробнее см. в `educommon.django.db.partitioning.init` и
    `educommon.django.db.partitioning.set_partitioning_for_model`.
    """

    help = 'Applies partitioning to the table.'  # noqa: A003

    def add_arguments(self, parser):
        """Обработка аргументов команды."""
        parser.add_argument(
            '--app_label',
            type=str,
            help='App label of an application.',
        )
        parser.add_argument(
            '--model_name',
            type=str,
            help='Model name.',
        )
        parser.add_argument(
            '--field_name',
            type=str,
            help='Field name. It will be the partition key.',
        )
        parser.add_argument('--is_foreign_table', type=bool, default=False, help='Партицирование для внешних таблиц')
        parser.add_argument('--schemas_names', type=str, default=None, help='Cхемы внешних таблиц при партицировании.')

    def handle(self, *args, **options):
        """Выполнение команды."""
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        is_foreign_table = options['is_foreign_table']
        schemas_names = options['schemas_names']

        logger_info('Apply partitioning started\n')
        try:
            django_db_model = get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(e.message)

        try:
            django_db_model._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise CommandError('Invalid field name ({0})'.format(field_name))

        db_alias = router.db_for_write(django_db_model)

        if not partitioning.is_initialized(db_alias):
            partitioning.init(db_alias)

        # Дополнительно пробросим схемы для работ с внешними таблицами
        if is_foreign_table:
            partitioning.set_partitioned_function_search_path(db_alias, schemas_names)

        partitioning.set_partitioning_for_model(django_db_model, field_name, force=True)

        logger_info('Apply partitioning ended\n')
