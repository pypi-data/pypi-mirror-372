import codecs
import os

from django.conf import (
    settings,
)
from django.core.management.base import (
    BaseCommand,
)
from django.db import (
    connection,
)

from educommon.audit_log.constants import (
    INSTALL_AUDIT_LOG_SQL_FILE_NAME,
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    clear_audit_logs,
    configure,
    get_json_auto_now_fields_by_model,
    get_db_connection_params,
)


DEFAULT_QUERYSET_CHUNK_SIZE = 1_000


class Command(BaseCommand):
    """Пересоздаёт функции журнала изменений в БД.

    Используется для миграции после модификации sql файла.

    Удаляет схему audit. В этой схеме не должно храниться никаких таблиц
    с данными.
    После удаления устанавливает audit_log заново.
    Через настройки проекта возможна передача дополнительных sql файлов
    для выполнения вместе с основным скриптом установки.
    """

    help = 'Команда для переустановки audit_log.'

    def add_arguments(self, parser) -> None:
        """Добавление аргументов команды."""
        parser.add_argument(
            '--clear_audit_logs',
            action='store_true',
            default=False,
            help='Удалить записи из audit_log для неотслеживаемых таблиц',
        )
        parser.add_argument(
            '--chunk_size',
            type=int,
            default=DEFAULT_QUERYSET_CHUNK_SIZE,
            help='Кол-во единовременно удаляемых записей',
        )

    def _read_sql(self, sql_file_path: str) -> str:
        """Чтение SQL-кода из файла."""
        with codecs.open(sql_file_path, 'r', 'utf-8') as sql_file:
            sql = sql_file.read()

        file_name = os.path.basename(sql_file_path)
        self.stdout.write(f'reading {file_name}..\n')

        return sql

    def _prepare_sql(self) -> list[str]:
        """Подготовка SQL-кода."""
        params = get_db_connection_params()
        params['lock_id'] = PG_LOCK_ID
        params['auto_now_fields'] = get_json_auto_now_fields_by_model()

        self.stdout.write('preparing SQL-code..\n')

        sql_files = [
            os.path.join(SQL_FILES_DIR, INSTALL_AUDIT_LOG_SQL_FILE_NAME),
            *getattr(settings, 'AUDIT_LOG_EXTENSION_SCRIPTS', [])
        ]

        sql_scripts = []
        for sql_file_path in sql_files:
            sql_scripts.append(self._read_sql(sql_file_path).format(**params))

        return sql_scripts

    def handle(self, *args, **options) -> None:
        """Формирование SQL-кода и его исполнение."""
        self.stdout.write('start reinstalling audit_log..\n')

        cursor = connection.cursor()

        for sql in self._prepare_sql():
            cursor.execute(sql)

        configure(force_update_triggers=True)

        if options['clear_audit_logs']:
            self.stdout.write('clearing audit_log...\n')

            deleted_table_counts = clear_audit_logs(chunk_size=options['chunk_size'])

            if deleted_table_counts:
                self.stdout.write('deleted audit_log records for tables:\n')
                for deleted_table, count in deleted_table_counts.items():
                    self.stdout.write(f'\t{deleted_table}: {count}\n')

        self.stdout.write('reinstalling audit_log finished.\n')
