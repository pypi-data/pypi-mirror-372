from educommon import (
    ioc,
)
from educommon.contingent.actions import (
    OkoguPack,
    OKSMPack,
)


def register_actions():
    """Регистрация паков."""
    ioc.get('main_controller').extend_packs((OkoguPack(), OKSMPack()))
