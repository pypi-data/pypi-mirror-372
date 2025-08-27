from datetime import (
    date,
)

from django.contrib.contenttypes.models import (
    ContentType,
)

from educommon.auth.rbac.backends.base import (
    BackendBase,
)
from educommon.auth.rbac.models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)


def _get_user_roles(user):
    """Возвращает все роли пользователя, в т.ч. и вложенные.

    :param user: Пользователь, возвращаемый функцией
        ioc.get('get_current_user').

    :rtype: set
    """
    # Роли, назначенные непосредственно пользователю
    user_direct_roles = Role.objects.filter(
        pk__in=UserRole.objects.filter(
            UserRole.get_date_in_intervals_filter(date.today()),
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.id,
        ).values('role')
    )

    # Все роли пользователя с учетом подчиненных
    user_roles = set()
    for role in user_direct_roles:
        user_roles.add(role)
        user_roles.update(role.subroles)

    return user_roles


def _get_user_permissions_query(user, permissions=None):
    """Возвращает все доступные пользователю разрешения.

    :param user: Пользователь, возвращаемый функцией
        ioc.get('get_current_user').
    :param permissions: Имена разрешений, среди которых нужно искать
        разрешения, доступные пользователю.

    :rtype: QuerySet
    """
    user_roles = _get_user_roles(user)

    permission_ids = RolePermission.objects.filter(
        role__in=user_roles,
    )
    if permissions:
        permission_ids = permission_ids.filter(
            permission__name__in=permissions,
        )

    # Все разрешения пользователя
    result = Permission.objects.filter(
        pk__in=permission_ids.distinct('permission').values('permission'),
    )

    return result


class SimpleBackend(BackendBase):
    """Предоставляет прямой доступ к объектам RBAC.

    Доступ к объектам RBAC (разрешениям, ролям и их связям между собой)
    осуществляется через ORM. Кеширование не осуществляется, поэтому
    использование данного бэкенда может приводить к излишней нагрузке на СУБД.
    """

    def _get_user_permissions(self, user, permissions=None):
        """Возвращает имена всех доступных пользователю разрешений.

        :param user: Пользователь, возвращаемый функцией
            ioc.get('get_current_user').
        :param permissions: Имена разрешений, среди которых нужно искать
            разрешения, доступные пользователю.

        :rtype: generator
        """
        # pylint: disable=protected-access
        for name in _get_user_permissions_query(user, permissions).values_list('name', flat=True):
            yield name
            for name in self._manager.get_dependent_permissions(name):
                yield name

    def has_perm(self, user, perm_name):
        """Проверяет наличие у пользователя разрешения.

        :param user: Пользователь, возвращаемый функцией
            ioc.get('get_current_user').
        :param basestring perm_name: Имя разрешения.

        :rtype: bool
        """
        result = perm_name in self._get_user_permissions(user)
        return result

    def has_access(self, action, request):
        """Проверяет наличие у текущего пользователя разрешения.

        :param action: Экшн, к которому проверяется наличие доступа.
        :type action: m3.actions.Action

        :param request: HTTP-запрос.
        :type request: django.http.HttpRequest

        :rtype: bool
        """
        if not self._need_check_access(action):
            return True

        user = self._get_current_user(request)
        if user is None:
            return False

        # Имена разрешений экшена, доступность которых будем проверять
        action_permissions = self._get_action_permissions(action)

        # Разрешения экшена, доступные пользователю
        permissions = self._get_user_permissions(user, action_permissions)

        for permission_name in permissions:
            if self._check_permission(permission_name, action, request, user):
                return True

        return False
