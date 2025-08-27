"""Инициализация приложения в M3."""

from educommon import (
    ioc,
)
from educommon.auth.rbac import (
    actions,
)


def register_actions():
    """Регистрация паков приложения в контроллере."""
    ioc.get('auth_controller').extend_packs(
        (
            actions.Pack(),
            actions.PartitionsPack(),
            actions.PermissionsPack(),
            actions.ResultPermissionsPack(),
        )
    )
