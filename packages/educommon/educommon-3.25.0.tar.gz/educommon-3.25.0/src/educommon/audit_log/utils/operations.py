# pylint: disable=abstract-method
import codecs
import os

from django.conf import (
    settings,
)
from django.db.migrations.operations.base import (
    Operation,
)

from educommon.audit_log.constants import (
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    get_db_connection_params,
    get_json_auto_now_fields_by_model,
)


class ReinstallAuditLog(Operation):
    """Пересоздаёт функции журнала изменений в БД.

    Используется для миграции после модификации sql файла.

    Удаляет схему audit. В этой схеме не должно храниться никаких таблиц
    с данными.
    После удаления устанавливает audit_log заново.
    """

    reversible = True

    @staticmethod
    def _read_sql(filename):
        """Читает SQL-файл и экранирует знаки процента."""
        sql_file_path = os.path.join(SQL_FILES_DIR, filename)
        with codecs.open(sql_file_path, 'r', 'utf-8') as sql_file:
            sql = sql_file.read().replace('%', '%%')
        return sql

    @property
    def _install_sql(self):
        """Генерирует SQL-скрипт для установки схемы audit_log.

        Подставляет параметры подключения к БД и lock_id
        в шаблон SQL-файла install_audit_log.sql.
        """
        params = get_db_connection_params()
        params['lock_id'] = PG_LOCK_ID
        params['auto_now_fields'] = get_json_auto_now_fields_by_model()

        return self._read_sql('install_audit_log.sql').format(**params)

    def state_forwards(self, app_label, state):
        """Не изменяет состояние проекта в памяти.

        Метод требуется по контракту абстрактного базового класса Operation.
        """
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Применяет SQL-скрипт установки audit_log, если используется основная БД."""
        if schema_editor.connection.alias == settings.DEFAULT_DB_ALIAS:
            schema_editor.execute(self._install_sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """Откат миграции не реализован (no-op).

        Метод присутствует, чтобы соответствовать контракту Django.
        """
        return None
