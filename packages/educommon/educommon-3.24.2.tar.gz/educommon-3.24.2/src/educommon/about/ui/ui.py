from django.template.loader import (
    render_to_string,
)
from m3_ext.ui.containers.grids import (
    ExtGrid,
)
from m3_ext.ui.misc.store import (
    ExtDataStore,
)

from objectpack.ui import (
    ObjectGridTab,
    TabbedWindow,
    WindowTab,
)

from educommon.m3 import (
    get_pack,
)
from educommon.utils.ui import (
    local_template,
    make_button,
)


class CommonTab(WindowTab):
    """Вкладка с общей информацией о системе."""

    title = 'Общие сведения'

    def do_layout(self, win, tab):
        super(CommonTab, self).do_layout(win, tab)

        self.tab = win.common_tab = tab

    def set_params(self, win, params):
        super(CommonTab, self).set_params(win, params)

        self.tab.height = 200
        self.tab.padding = 0
        self.tab.border = 0

        self.tab.html = render_to_string(
            local_template('common-tab.html'),
            params['data'],
        )


class PackagesTab(ObjectGridTab):
    """Вкладка со списком пакетов, установленных в системе."""

    title = 'Версии ПО'

    template = local_template('packages-tab.js')
    clipboard_template = local_template('clipboard.js')

    def get_pack(self):
        return get_pack(__package__ + '.actions.PackagesPack')

    def init_components(self, win):
        super(PackagesTab, self).init_components(win)

        self.grid__version_info = ExtGrid()
        self.grid__version_info.add_column(
            header='Программное обеспечение',
            data_index='name',
        )
        self.grid__version_info.add_column(
            header='Версия',
            data_index='version',
        )

        self.grid.title = 'Версии пакетов Python'
        self.grid.header = True

        self.button__copy = make_button(
            title='Скопировать в буфер обмена (pip freeze)',
            icon_cls='copy',
            event='copy',
            client_id=self.grid.client_id,
        )

    def do_layout(self, win, tab):
        super(PackagesTab, self).do_layout(win, tab)

        self.tab = win.packages_tab = tab
        tab.grid = self.grid

        self.tab.items[:] = (
            self.grid__version_info,
            self.grid,
            self.button__copy,
        )

    def set_params(self, win, params):
        super(PackagesTab, self).set_params(win, params)

        self.tab.padding = 0
        self.tab.border = 0
        self.tab.layout = 'vbox'
        self.tab.layout_config = {'align': 'stretch'}

        self.grid.flex = 1
        self.grid__version_info.store = ExtDataStore(params['version_info'])
        self.grid.top_bar.items[:] = []


class PostgreSQLExtensionsTab(ObjectGridTab):
    """Вкладка со списком расширений PostgreSQL."""

    title = 'Расширения БД'
    template = local_template('postgresql-extensions-tab.js')

    def get_pack(self):
        return get_pack(__package__ + '.actions.PostgreSQLExtensionsPack')

    def do_layout(self, win, tab):
        super(PostgreSQLExtensionsTab, self).do_layout(win, tab)
        tab.grid = self.grid

    def set_params(self, win, params):
        super(PostgreSQLExtensionsTab, self).set_params(win, params)
        self.grid.top_bar.items[:] = []


class AboutWindow(TabbedWindow):
    """Окно 'Информация о системе'."""

    tabs = (
        CommonTab,
        PackagesTab,
        PostgreSQLExtensionsTab,
    )

    # соответствие названия права в параметрах окна и вкладки
    tab_right_map = {
        'can_view_common_tab': CommonTab,
        'can_view_packages_tab': PackagesTab,
        'can_view_postgresql_ext_tab': PostgreSQLExtensionsTab,
    }

    def reconfigure_tabs(self, params):
        """Настройка вкладок, согласно правам."""
        available_tab_titles = list()
        for right, tab in self.tab_right_map.items():
            if params.get(right, False):
                available_tab_titles.append(tab.title)

        # удаление вкладок
        self.tabs[:] = (tab for tab in self.tabs if tab.title in available_tab_titles)
        # удаление контейнеров вкладок
        self._tab_container.items[:] = (
            item for item in self._tab_container.items if item.title in available_tab_titles
        )

    def set_params(self, params):
        self.reconfigure_tabs(params)

        # Отложенная загрузка данных в гридах
        self.lazy_grids = dict()

        super(AboutWindow, self).set_params(params)

        self.title = 'О системе'
        self.width, self.height = 500, 500
        self.resizable = False

        if len(self._tab_container.items) > 1:
            for tab in self._tab_container.items:
                if hasattr(tab, 'grid'):
                    self.lazy_grids.setdefault(tab.client_id, []).append(tab.grid.client_id)
                    tab.grid.store.auto_load = False

        self.template_globals = local_template('about-window.js')
