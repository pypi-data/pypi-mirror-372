from m3.actions import (
    AbstractPermissionChecker,
    Action,
    ActionPack,
)

from educommon.auth.rbac.manager import (
    rbac,
)


class PermissionChecker(AbstractPermissionChecker):
    """Класс, проверяющий наличие необходимых у пользователя прав.

    Наличие прав у пользователя определяется в зависимости от ролей,
    назначенных пользователю.

    Использование данного permission checker'а предполагает, что у каждого пака
    и у каждого экшена системы определены атрибуты perm_code. При этом,
    perm_code пака определяет раздел перечня разрешений, например: employee,
    pupil, unit и т.д. Атрибут perm_code у экшена определяет вид действия:
    view, add, edit, delete, report и т.д. Также в экшенах возможно определение
    подвидов действий, например: all, own и т.д.
    """

    def has_action_permission(self, request, action, subpermission=None):
        """Проверяет права доступа пользователя к экшену.

        :param request: Http-запрос.
        :type request: django.http.Request

        :param action: Экшн, наличие прав на выполнение которого проверяется.
        :type action: m3_core.actions.Action

        :rtype: bool
        """
        result = rbac.has_access(action, request)
        return result

    def has_pack_permission(self, request, pack, permission):
        # Не используется
        raise NotImplementedError()

    @staticmethod
    def get_perm_code(action_or_pack, subpermission=None):
        """Возвращает код разрешения для пака или экшена."""
        if isinstance(action_or_pack, ActionPack):
            pack, action = action_or_pack, None
        elif isinstance(action_or_pack, Action):
            pack, action = action_or_pack.parent, action_or_pack
        else:
            raise TypeError(type(action_or_pack))

        pack_perm_code = getattr(pack, 'perm_code', False)
        if not pack_perm_code:
            pack_perm_code = '/'.join((pack.__class__.__module__, pack.__class__.__name__))

        if action is None:
            action_perm_code = 'default'
        else:
            action_perm_code = getattr(action, 'perm_code', False)
            if not action_perm_code:
                action_perm_code = action.__class__.__name__

        if subpermission:
            result = '/'.join((pack_perm_code, subpermission))
        else:
            result = '/'.join((pack_perm_code, action_perm_code))

        return result
