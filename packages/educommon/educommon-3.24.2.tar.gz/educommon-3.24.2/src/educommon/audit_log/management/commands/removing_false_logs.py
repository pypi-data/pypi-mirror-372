"""
Команда удаления ложных логов в таблицах audit_log_auditlog и state_log_all.
"""
import codecs
import os

import psycopg2
from django.apps import (
    apps,
)
from django.core.management.base import (
    BaseCommand,
)
from django.utils.functional import (
    cached_property,
)

from psycopg2.extras import (
    Json,
)

from educommon.audit_log.constants import (
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    get_db_connection_params,
    get_dict_auto_now_fields_by_model,
)


NEW_AUDIT_LOG_REMOVING_FALSE_LOGS_SQL_FILE_NAME = 'new_audit_log_removing_false_logs.sql'
OLD_AUDIT_LOG_REMOVING_FALSE_LOGS_SQL_FILE_NAME = 'old_audit_log_removing_false_logs.sql'
NEW_AUDIT_LOG_TABLE_NAME = 'audit_log_auditlog'
OLD_AUDIT_LOG_TABLE_NAME = 'state_log_all'


class Command(BaseCommand):
    """Команда удаления ложных логов в таблицах audit_log_auditlog и state_log_all."""

    help = 'Команда удаления ложных логов в таблицах audit_log_auditlog и state_log_all..'

    @cached_property
    def auto_now_fields_new_audit_log(self) -> dict[str, list[str]]:
        """Возвращает словарь с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.

        Returns:
            Словарь, где ключ это название таблицы, а значение это список названий полей имеющими auto_now=True.
        """

        return get_dict_auto_now_fields_by_model()

    @cached_property
    def auto_now_fields_old_audit_log(self) -> dict[str, list[str]]:
        """Возвращает словарь с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.

        Returns:
            Словарь, где ключ это название модели, а значение это список названий полей имеющими auto_now=True.
        """

        return {
            model.__name__: fields
            for model in apps.get_models()
            if (fields := self.auto_now_fields_new_audit_log.get(model._meta.db_table))
        }

    def _check_exists_table(self, cursor, table_name: str) -> bool:
        """Запуск SQL-скрипта для проверки существования таблицы.

        Args:
            cursor: Объект-курсор для работы с базой данных.
            table_name: Название таблицы БД.

        Returns:
            Флаг существования таблицы.
        """
        exists_table = """
            SELECT 1 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'public' AND TABLE_NAME = '{table_name}';
        """.format(table_name=table_name)

        cursor.execute(exists_table)

        return bool(cursor.fetchone())

    def _delete_log(self, cursor, table_name: str, sql_file_name: str, auto_now_fields) -> None:
        """Запуск SQL-скрипта по удалению ложных логов.

        Args:
            cursor: Объект-курсор для работы с базой данных.
            table_name: Название таблицы БД.
            sql_file_name: Название SQL файла.
            auto_now_fields: Словарь с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.
        """
        if self._check_exists_table(cursor, table_name):
            self.stdout.write(f'Удаление ложных записей в таблице {table_name}.')
            cursor.execute(self._prepare_sql(sql_file_name, auto_now_fields, table_name))
            self.stdout.write(self.style.SUCCESS(f'Успешно удалены ложные записи в таблице {table_name}.'))
        else:
            self.stdout.write(self.style.ERROR(f'Таблица {table_name} не найдена.'))

    def _read_sql(self, sql_file_name: str) -> str:
        """Чтение SQL-кода из файла.

        Args:
            sql_file_name: Название SQL файла.

        Returns:
            SQL-кода из файла.
        """
        sql_file_path = os.path.join(SQL_FILES_DIR, sql_file_name)

        with codecs.open(sql_file_path, 'r', 'utf-8') as sql_file:
            sql = sql_file.read()

        self.stdout.write(f'Выполнение {sql_file_name}.')

        return sql

    def _prepare_sql(self, sql_file_name: str, auto_now_fields: dict[str, list[str]], table_name: str) -> str:
        """Подготовка SQL-кода.

        Args:
            sql_file_name: Название SQL файла.
            auto_now_fields: Словарь с полями, имеющими auto_now=True, для моделей с флагом need_to_log = True.
            table_name: Название таблицы БД.

        Returns:
            SQL-кода из файла, с добавленными параметрами.
        """
        self.stdout.write(f'Подготовка SQL-кода для удаления ложных логов в таблице {table_name}.')

        params = {
            'auto_now_fields': Json(auto_now_fields),
        }

        return self._read_sql(sql_file_name).format(**params)

    def handle(self, *args, **options) -> None:
        """Формирование SQL-кода и его исполнение."""
        self.stdout.write('Начало работы команды.')

        connection = psycopg2.connect(**get_db_connection_params())
        cursor = connection.cursor()

        # Удаление ложных записей в таблице audit_log_auditlog.
        self._delete_log(
            cursor=cursor,
            table_name=NEW_AUDIT_LOG_TABLE_NAME,
            sql_file_name=NEW_AUDIT_LOG_REMOVING_FALSE_LOGS_SQL_FILE_NAME,
            auto_now_fields=self.auto_now_fields_new_audit_log,
        )
        # Удаление ложных записей в таблице state_log_all.
        self._delete_log(
            cursor=cursor,
            table_name=OLD_AUDIT_LOG_TABLE_NAME,
            sql_file_name=OLD_AUDIT_LOG_REMOVING_FALSE_LOGS_SQL_FILE_NAME,
            auto_now_fields=self.auto_now_fields_old_audit_log,
        )

        connection.commit()
        self.stdout.write(self.style.SUCCESS('Выполнение команды завершено.'))
