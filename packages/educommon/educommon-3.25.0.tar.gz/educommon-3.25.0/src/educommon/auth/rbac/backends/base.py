from abc import (
    ABCMeta,
    abstractmethod,
)

from educommon import (
    ioc,
)


class BackendBase(metaclass=ABCMeta):
    """Базовый класс для бэкендов RBAC."""

    def __init__(self, manager):
        self._manager = manager

    def _need_check_access(self, action):
        """Возвращает True, если ``action`` предполагает проверку доступа.

        :rtype: bool
        """
        return action.parent.need_check_permission or action.need_check_permission

    def _get_current_user(self, request):
        """Возвращает текущего пользователя.

        :rtype: bool
        """
        return ioc.get('get_current_user')(request)

    def _get_action_permissions(self, action):
        """Возвращает имена разрешений экшена.

        :rtype: tuple
        """
        if action.sub_permissions:
            result = tuple(action.get_perm_code(sub_perm) for sub_perm in action.sub_permissions)
        else:
            result = (action.get_perm_code(),)

        return result

    def _check_permission(self, permission_name, action, request, user):
        """Проверяет возможность предоставления доступа.

        Если для указанного разрешения определены правила, то выполняет их
        проверку.

        :rtype: bool
        """
        if permission_name in self._manager.permission_rules:
            for handler in self._manager.permission_rules[permission_name]:
                if handler(action, request, user):
                    result = True
                    break
            else:
                result = None
        else:
            # Для разрешения не определено правил, значит достаточно
            # только наличия у пользователя разрешения как такового.
            result = True

        return result

    @abstractmethod
    def has_perm(self, user, perm_name):
        """Проверяет наличие у пользователя разрешения.

        :param user: Пользователь, возвращаемый функцией
            ioc.get('get_current_user').
        :param basestring perm_name: Имя разрешения.

        :rtype: bool
        """

    @abstractmethod
    def has_access(self, action, request):
        """Проверяет наличие у текущего пользователя разрешения.

        :param action: Экшн, к которому проверяется наличие доступа.
        :type action: m3.actions.Action

        :param request: HTTP-запрос.
        :type request: django.http.HttpRequest

        :rtype: bool
        """
