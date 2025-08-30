from django.core.management.base import (
    CommandError,
)

from m3_django_compat import (
    BaseCommand,
    get_model,
)
from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)

from educommon.django.db import (
    partitioning,
)
from educommon.logger import (
    info as logger_info,
)


class Command(BaseCommand):
    """Переносит все записи из таблицы БД в ее разделы.

    Если до включения партиционирования таблицы БД в ней находились записи, то
    с помощью данной команды их можно перенести в соответствующие разделы.
    Подробнее см. в `educommon.django.db.partitioning.split_table`.

    """

    help = 'Command moves all the records from database table to partitions of this table.'

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки для команды переноса данных в разделы."""
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
        parser.add_argument(
            '--timeout',
            action='store',
            dest='timeout',
            default=0.0,
            type=float,
            help=('Timeout (in seconds) between the data transfer iterations. It used to reduce the database load.'),
        )
        parser.add_argument(
            '--cursor_itersize',
            action='store',
            dest='cursor_itersize',
            type=int,
            default=None,
            help='Количество строк загруженных за раз при загрузке строк при работе команды.',
        )

    def handle(self, *args, **options):
        """Основная логика команды.

        Проверяет наличие модели и заданного поля, затем запускает
        процесс переноса данных в секции таблицы.
        """
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        timeout = options['timeout']
        cursor_itersize = options['cursor_itersize']

        try:
            model = get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(e.message)

        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise CommandError('Invalid field name ({0})'.format(field_name))

        logger_info('Split table started\n')

        partitioning.split_table(model, field_name, timeout, cursor_itersize)

        logger_info('Split table ended\n')
