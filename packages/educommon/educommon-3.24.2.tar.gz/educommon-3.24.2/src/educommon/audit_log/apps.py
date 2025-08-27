# pylint: disable=function-redefined, unused-argument
from contextlib import (
    closing,
)

from django.apps import (
    AppConfig,
)
from django.conf import (
    settings,
)
from django.core.checks import (
    Critical,
    register,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.db import (
    connections,
)
from django.db.models.signals import (
    post_migrate,
)

from educommon.utils.db.postgresql import (
    create_extension,
    is_extension_exists,
)


class AppConfig(AppConfig):
    """Конфигурация подсистемы логирования изменений в БД.

    При инициализации приложения:
    - подключает обработку сигнала post_migrate;
    - создаёт необходимые расширения PostgreSQL (hstore, postgres_fdw);
    - проверяет и настраивает подключение к сервисной БД через FDW;
    - выполняет установку и проверку инфраструктуры AuditLog.
    """

    name = __name__.rpartition('.')[0]

    @property
    def _dispatch_uid(self):
        """Уникальный идентификатор для подключения сигнала post_migrate.

        Используется для предотвращения дублирующего подключения обработчиков.
        """
        return '.'.join(
            (
                self.name,
                self.__class__.__name__,
                self._configure_audit_log.__name__,
            )
        )

    def _create_postgresql_extensions(self):
        """Создает в БД необходимые расширения PostgreSQL.

        Расширения создаются только при наличии прав. Если прав нет, ничего не
        происходит. При запуске системы будет критическая ошибка Django и
        сообщение о необходимости создания недостающих расширений.
        """
        alias = settings.DEFAULT_DB_ALIAS
        if not is_extension_exists(alias, 'postgres_fdw'):
            if create_extension(alias, 'postgres_fdw', quite=True):
                with closing(connections[alias].cursor()) as cursor:
                    cursor.execute('GRANT USAGE ON FOREIGN DATA WRAPPER postgres_fdw TO PUBLIC')

        for alias in (settings.DEFAULT_DB_ALIAS, settings.SERVICE_DB_ALIAS):
            if not is_extension_exists(alias, 'hstore'):
                create_extension(alias, 'hstore', quite=True)

    def _configure_audit_log(self, connection):
        """Настраивает AuditLog при первом подключении к БД."""
        # Настройка параметров подключения к сервисной БД, обновление триггеров
        from educommon.audit_log.utils import (
            configure,
        )

        configure()

        # Проверка подключения подключения к сервисной БД через FDW.
        from educommon.audit_log.utils import (
            check_connection_fdw,
        )

        success, error_message = check_connection_fdw()
        if not success:
            raise ImproperlyConfigured(
                '{0} - Ошибка подключения к сервисной базе через '
                "postgres_fdw. Необходимо убедится что 'Журнал изменений' "
                'настроен корректно.'.format(error_message)
            )

    def _configure_db(self, **kwargs):
        """Инициализирует расширения PostgreSQL и настраивает AuditLog.

        Вызывается после применения миграций. Если AuditLog уже инициализирован,
        выполняется его настройка.
        """
        from educommon.audit_log.utils import (
            is_initialized,
        )

        self._create_postgresql_extensions()
        if is_initialized(settings.DEFAULT_DB_ALIAS):
            self._configure_audit_log(connections[settings.DEFAULT_DB_ALIAS])

    def ready(self):
        """Вызывается при готовности приложения.

        Подключает обработчик _configure_db к сигналу post_migrate.
        """
        post_migrate.connect(self._configure_db, sender=self)


@register
def check_postgres_fdw(app_configs, **kwargs):
    """Проверяет наличие в основной БД расширения postgres_fdw."""
    errors = []

    if not is_extension_exists(settings.DEFAULT_DB_ALIAS, 'postgres_fdw'):
        dbname = settings.DATABASES[settings.DEFAULT_DB_ALIAS]['NAME']
        msg = ("'postgres_fdw' PostgreSQL extension not installed in '{}' database.").format(dbname)
        hint = (
            "Execute this SQL in '{dbname}' database:\n"
            '{indent}CREATE EXTENSION postgres_fdw;\n'
            '{indent}GRANT USAGE ON FOREIGN DATA WRAPPER postgres_fdw '
            'TO PUBLIC;'
        ).format(indent=' ' * 14, dbname=dbname)
        errors.append(Critical(msg, hint, id='audit_log.C001'))

    return errors


@register
def check_hstore(app_configs, **kwargs):
    """Проверяет наличие в основной и в сервисной БД расширения hstore."""
    errors = []

    msg = "'hstore' PostgreSQL extension not installed in '{}' database."
    hint = "Execute this SQL in '{dbname}' database:\n{indent}CREATE EXTENSION hstore;"
    indent = ' ' * 14

    def check(alias, message_id):
        dbname = settings.DATABASES[alias]['NAME']
        if not is_extension_exists(alias, 'hstore'):
            errors.append(
                Critical(
                    msg.format(dbname),
                    hint.format(indent=indent, dbname=dbname),
                    id=message_id,
                )
            )

    check(settings.DEFAULT_DB_ALIAS, 'audit_log.C002')
    check(settings.SERVICE_DB_ALIAS, 'audit_log.C003')

    return errors
