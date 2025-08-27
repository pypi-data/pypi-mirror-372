from educommon import (
    ioc,
)
from educommon.report.constructor.editor.actions import (
    Pack,
)


def register_actions():
    ioc.get('main_controller').packs.extend((Pack(),))
