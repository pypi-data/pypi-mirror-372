"""Подсистема логирования изменений в БД.

В PostgreSQL должна быть поддержка hstore. В Ubuntu требуется
установленный пакет postgresql-contrib.

До подключения логирования от суперпользователя необходимо
выполнить SQL команды.

В основной БД:
    CREATE EXTENSION IF NOT EXISTS postgres_fdw;
    CREATE EXTENSION IF NOT EXISTS hstore;

    GRANT USAGE ON FOREIGN DATA WRAPPER postgres_fdw TO PUBLIC;

В сервисной БД:
    CREATE EXTENSION IF NOT EXISTS hstore;

Подключение к проекту:
    Settings:
    - В DATABASE_ROUTERS добавить полный путь к AuditLogRouter;
    - В MIDDLEWARE_CLASSES вставить полный путь к `AuditLogMiddleware`
      после `django.contrib.sessions.middleware.SessionMiddleware`,
      `django.contrib.auth.middleware.AuthenticationMiddleware`.
      Желательно, чтобы `AuditLogMiddleware` подключалось как можно раньше,
      т.к. для всех измененных объектов до подключения этого Middleware
      невозможно будет установить пользователя и ip.
    - Поключить приложение `audit_log` в INSTALLED_APPS.

При старте проекта необходимо вызвать как можно раньше функцию:
    `extedu.audit_log.utils.configure().
Эта функция изменяет параметры подключения к сервисной БД.
Ей необходимо подключение к БД.

В качестве одного из вариантов можно использовать сигнал connection_created:

    >>> @receiver(connection_created)
    >>> def configure_audit_log(connection, **kwargs):
    >>>    if connection.alias == 'default':
    >>>        from educommon.audit_log.utils import configure
    >>>        configure()
    >>>        connection_created.disconnect(configure_audit_log)

Текст для отображения колонки "Объект" в окне просмотра журнала изменений
берется как результат вызова одного из трех методов модели в следующем порядке:
    - log_display()
    - display()
    - __str__()
Для каждой модели проекта желательно добавить/изменить один из данных методов.
"""

import django


assert django.VERSION >= (1, 9), 'django version must be >= 1.9'

if django.VERSION < (3, 2):
    default_app_config = __name__ + '.apps.AppConfig'
