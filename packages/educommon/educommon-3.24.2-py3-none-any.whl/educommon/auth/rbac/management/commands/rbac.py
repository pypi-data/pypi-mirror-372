"""Management-команда для обслуживания системы авторизации."""

import os

from django.core.management import (
    CommandError,
)
from m3_django_compat import (
    BaseCommand,
)
from termcolor import (
    colored,
)

from educommon.auth.rbac.manager import (
    _get_actions,
    rbac,
)
from educommon.auth.rbac.models import (
    Permission,
)


class Command(BaseCommand):
    """Обслуживание системы авторизации."""

    use_argparse = False

    def _show_actions(self, *permissions, **options):
        """Вывод списка экшенов системы.

        :param permissions: Имена разрешений, для которых нужно вывести список
            экшенов.
        """
        if not permissions:
            permissions = sorted(rbac.permissions_by_name.keys())

        actions_by_permission = {name: [] for name in permissions}

        for action in _get_actions():
            if getattr(action, 'sub_permissions', None):
                for sub_perm in action.sub_permissions:
                    perm_code = action.get_perm_code(sub_perm)
                    if perm_code in actions_by_permission:
                        actions_by_permission[perm_code].append(action)
            else:
                perm_code = action.get_perm_code()
                if perm_code in actions_by_permission:
                    actions_by_permission[perm_code].append(action)

        for name in sorted(actions_by_permission):
            self.stdout.write(colored(name, 'blue') + '\n')
            actions = sorted(
                '{}.{}/{}'.format(
                    action.parent.__class__.__module__,
                    colored(action.parent.__class__.__name__, 'yellow'),
                    colored(action.__class__.__name__, 'green'),
                )
                for action in actions_by_permission[name]
            )
            for action in actions:
                self.stdout.write('   ' + action + '\n')

    def _show_permissions(self, status='all'):
        """Вывод разрешений.

        :param registered_only: определяет, какие разрешения нужно выводить:
            None - все, True - только зарегистрированные в системе, False - все
            разрешения, имеющиеся в БД.
        """
        db_perms = set(Permission.objects.values_list('name', flat=True))
        sys_perms = set(rbac.permissions_by_name.keys())

        if status == 'all':
            permissions = db_perms | sys_perms
        elif status == 'registered':
            permissions = db_perms
        elif status == 'not_registered':
            permissions = sys_perms
        else:
            raise CommandError('Unknown status: {}'.format(status))

        if not permissions:
            return

        max_width = max(len(permission) for permission in permissions)
        self.stdout.write('Permissions:\n')

        for permission in sorted(permissions):
            if permission not in db_perms and permission in sys_perms:
                status, color = '[NOT REGISTERED]', 'red'
            elif permission in db_perms and permission not in sys_perms:
                status, color = '[NOT IN SYSTEM ]', 'yellow'
            else:
                status, color = '[  REGISTERED  ]', 'green'

            line = f'  {status} {permission:<{max_width}}\n'
            self.stdout.write(colored(line, color))

    def _show(self, objects='permissions', *args, **options):
        """Отображение данных системы авторизации."""
        if objects == 'permissions':
            self._show_permissions(*args)
        elif objects == 'actions':
            self._show_actions(*args, **options)
        else:
            raise CommandError('Unknown objects type: {}'.format(objects))

    def _clean_permissions(self):
        """Удаление из БД незарегистрированных в системе разрешений."""
        permissions = Permission.objects.exclude(
            name__in=rbac.permissions_by_name,
        )

        if not permissions:
            return

        max_width = max(len(p.name) for p in permissions)

        for permission in permissions:
            permission.delete()
            line = f'{permission.name:<{max_width}}  [DELETED]\n'
            self.stdout.write(colored(line, 'red'))

    def _clean(self, objects='all', **options):
        """Удаление незарегистрированных правил и разрешений."""
        if objects == 'all':
            self._clean_permissions()
        elif objects == 'permissions':
            self._clean_permissions()
        else:
            raise CommandError('Unknown objects type: {}'.format(objects))

    def handle(self, action, *args, **options):
        """Обработка команды управления RBAC."""
        rbac.init(update_db=False)

        if not self.stdout.isatty():
            os.environ['ANSI_COLORS_DISABLED'] = '1'

        if action == 'show':
            self._show(*args, **options)
        elif action == 'clean':
            self._clean(*args, **options)
        # TODO: elif action == 'delete':
        else:
            raise CommandError('Unsupported action: {}'.format(action))
