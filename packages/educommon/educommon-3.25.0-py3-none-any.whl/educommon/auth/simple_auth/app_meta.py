from django.urls import (
    re_path,
)

from m3.actions import (
    ControllerCache,
)
from m3_ext.ui.app_ui import (
    GENERIC_USER,
    DesktopLoader,
    DesktopShortcut,
)
from objectpack.desktop import (
    uificate_the_controller,
)

from educommon import (
    ioc,
)
from educommon.auth.simple_auth.actions import (
    AuthPack,
)


auth_controller = ioc.get('auth_controller')


def register_actions():
    auth_controller.extend_packs((AuthPack(),))


def register_desktop_menu():
    """Добавляет в меню Пуск пункт "Выход"."""
    auth_pack = ControllerCache.find_pack(AuthPack)
    DesktopLoader.add(
        GENERIC_USER,
        DesktopLoader.TOOLBOX,
        DesktopShortcut(pack=auth_pack.logout_confirm_action, name='Выход', index=256, icon='logout'),
    )

    uificate_the_controller(auth_controller)


def register_urlpatterns():
    """Регистрация URL контроллера."""
    return [
        re_path(*auth_controller.urlpattern),
    ]
