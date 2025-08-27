from educommon import (
    ioc,
)
from educommon.audit_log.error_log.actions import (
    PostgreSQLErrorPack,
)


def register_actions():
    """Регистрация паков и экшенов."""
    ioc.get('main_controller').packs.extend(
        (
            PostgreSQLErrorPack(),
        )
    )
