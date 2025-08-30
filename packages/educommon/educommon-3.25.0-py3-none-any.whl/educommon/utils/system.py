import platform
from importlib import (
    import_module,
)
from inspect import (
    currentframe,
)

import distro


def is_in_migration_command():
    """Возвращает True, если код выполняется в рамках миграций Django.

    :rtype: bool
    """
    from django.core.management import (
        ManagementUtility,
    )

    def is_in_command(command):
        frame = currentframe()
        while frame:
            if 'self' in frame.f_locals:
                self_object = frame.f_locals['self']
                if isinstance(self_object, command):
                    return True

                elif isinstance(self_object, ManagementUtility):
                    # Срабатывает при использовании функции в AppConfig
                    if 'subcommand' in frame.f_locals:
                        subcommand = frame.f_locals['subcommand']
                        return subcommand == 'migrate' or subcommand == 'reinstall_audit_log'

            frame = frame.f_back

    modules = (
        'django.core.management.commands.migrate',
        'django.core.management.commands.makemigrations',
        'django.core.management.commands.sqlmigrate',
        'django.core.management.commands.showmigrations',
        'educommon.audit_log.management.commands.reinstall_audit_log',
    )

    for module_name in modules:
        if is_in_command(import_module(module_name).Command):
            return True

    return False


def get_postgresql_version(connection):
    """Возвращает версию PostgreSQL.

    :param connection: :class:`django.db.DefaultConnectionProxy`
    :rtype: tuple
    """
    with connection.cursor() as cursor:
        if cursor.db.vendor != 'postgresql':
            raise RuntimeError(f'Only PostgreSQL RDBMS supported, not {cursor.db.vendor}')

        return (
            cursor.db.pg_version // 10000,
            cursor.db.pg_version % 10000 // 100,
            cursor.db.pg_version % 100,
        )


def get_os_version():
    """Возвращает строку с описанием дистрибутива (релиза) и версии ОС."""
    result = 'Unknown'
    system = platform.system()

    if system == 'Linux':
        name, version, codename = distro.linux_distribution()
        result = '{} {}'.format(name, version)
        if codename:
            result = '{} ({})'.format(result, codename)

    elif system == 'Windows':
        release, version, sp, _ = platform.win32_ver()
        result = '{} {}'.format(release, version)
        if sp:
            result = '{}, SP {}'.format(result, sp)

    elif system == 'Darwin':
        release, version, arch = platform.mac_ver()
        result = 'MacOS {} ({})'.format(release, arch)

    return result
