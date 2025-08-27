from m3_ext.ui import (
    all_components as ext,
    render_component,
)
from m3_ext.ui.containers.grids import (
    ExtGridGroupingView,
)
from m3_ext.ui.misc import (
    store as ext_store,
)
from m3_ext.ui.misc.store import (
    ExtJsonWriter,
)

from objectpack.ui import (
    BaseEditWindow as OPBaseEditWindow,
    BaseListWindow as OPBaseListWindow,
    BaseMultiSelectWindow as OPBaseMultiSelectWindow,
    BaseSelectWindow as OPBaseSelectWindow,
    BaseWindow,
    ColumnsConstructor,
    ComboBoxWithStore,
    ModelEditWindow as OPModelEditWindow,
    TabbedEditWindow as OPTabbedEditWindow,
)

from educommon.utils.ui import (
    local_template,
    reconfigure_grid_by_access,
    switch_window_in_read_only_mode,
)


class GridPanel(ext.ExtPanel):
    """Панель, имеющая grid_url, по которому получает грид и вставляет в себя."""

    grid_url = None
    template = 'grid-panel.js'
    grid_class = ext.ExtObjectGrid

    def __init__(self, *args, **kwargs):
        # в инитах затирается темплейт
        t = self.template

        super().__init__(*args, **kwargs)

        self.template = t

    @staticmethod
    def _create_grid(pack, columns, grid_cls, group_by=None, force_fit=False, **kwargs):
        """Метод возвращает грид.

        :param grid_cls: класс грида
        :type grid_cls: ExtObjectGrid
        :param str group_by: темплейт для группирования
        """
        grid = grid_cls(
            region='north', force_fit=force_fit, auto_scroll=True, auto_width=False, cls='word-wrap-grid', **kwargs
        )
        grid.flex = 1
        grid.sm = ext.ExtGridCellSelModel()
        grid.allow_paging = False

        # создание колонок
        cc = ColumnsConstructor()

        # если грид с группирующими строками
        if group_by:
            grid.store = ext_store.ExtGroupingStore(
                url=grid.get_store().url, total_property='total', root='rows', auto_load=True
            )
            grid.store.reader = ext_store.ExtJsonReader(total_property='total', root='rows')
            grid.view = ExtGridGroupingView(group_text_template=group_by, force_fit=grid.force_fit)

            def configure_reader(col):
                grid.store.reader.set_fields(col['data_index'])
        else:

            def configure_reader(col):
                return None

        def populate(root, columns):
            for c in columns:
                sub_cols = c.pop('columns', None)
                params = {}
                params.update(c)
                params['header'] = str(params.pop('header', ''))
                # TODO - сомнительная проверка
                if sub_cols is not None:
                    if sub_cols:
                        new_root = cc.BandedCol(**params)
                        root.add(new_root)
                        populate(new_root, sub_cols)
                else:
                    configure_reader(c)
                    root.add(cc.Col(**params))

        populate(cc, columns)
        cc.configure_grid(grid)

        # атрибуты грида
        grid.row_id_name = pack.row_id_name
        grid.column_param_name = pack.column_param_name
        grid.editor = True
        grid.store.writer = ExtJsonWriter(write_all_fields=False)
        grid.url_data = pack.get_rows_url()

        # список исключений для make_read_only
        grid._mro_exclude_list = []

        return grid

    @classmethod
    def configure_grid(cls, grid, params):
        """Конфигурирование грида."""

        pack = params['pack']
        # обычное поведение
        grid.sm = ext.ExtGridCellSelModel()
        grid.row_id_name = pack.row_id_name
        grid.url_data = pack.get_rows_url()
        # кнопка "Обновить" не участвует в блокировке грида при make_read_only
        grid._mro_exclude_list.append(grid.top_bar.button_refresh)

        return grid

    @classmethod
    def create_grid(cls, pack, columns, **kwargs):
        grid = cls._create_grid(pack, columns, cls.grid_class, **kwargs)

        return grid

    def pre_render(self):
        assert self.grid_url, 'grid url must be defined in gridpanel!'
        self._put_config_value('grid_url', self.grid_url)

    def render(self):
        self.pre_render()

        self.cmp_code = super().render()

        return render_component(self)


class FilterPanel(ext.ExtPanel):
    """Панель, умеющая fireevent'ить об изменении контрола, входящего в список filters."""

    def __init__(self, *args, **kwargs):
        super(FilterPanel, self).__init__(*args, **kwargs)

        self.filters = []

    def configure_redirect(self, control, event):
        """Связывает текущую панель с контролом control посредством fireevent'а event."""
        self._listeners['changed'] = f"""
        function(params) {{
            Ext.getCmp('{control.client_id}').fireEvent('{event}', params);
        }}
        """

    def configure_events(self):
        """Дополнение рендера fireevent'ом изменения значения контролов, входящих в список filters панели."""
        for control in self.filters:
            # определяется что за контрол и приделываются разные events
            if isinstance(control, ComboBoxWithStore):
                control.events = [
                    ('select', 'makeSimpleHandler'),
                ]
                """
                ..code::

                    control.events = ('custom_event', '(function(ctl, name){
                        custom handler })')
                """
            if isinstance(control, ext.ExtDictSelectField):
                control.events = [('change', 'makeSimpleHandler')]
            if isinstance(control, ext.ExtDateField):
                control.events = [('select', 'makeSimpleHandler')]

    def render(self):
        self.configure_events()
        self.pre_render()

        self.cmp_code = super(FilterPanel, self).render()

        # где-то в инитах затирается темплейт, опишем еще раз
        self.template = 'filter-panel.js'

        return render_component(self)


class BaseGridWindow(BaseWindow):
    """Базовое окно с фильтрующей панелью и панелью с гридом.

    Клиент получает панель с гридом с сервера при изменении
    полей фильтрации на фильтрующей панели.
    """

    grid_panel_cls = GridPanel  # панель грида

    def _init_grid_panel(self):
        """Панель для грида."""
        self.grid_panel = self.grid_panel_cls(
            region='center', layout='hbox', flex=1, layout_config={'align': 'stretch'}
        )

    def _init_filter_panel(self):
        """Панель с фильтрами."""
        self.filter_cnt = FilterPanel(
            body_cls='x-window-mc',
            padding='5px 7px',
            border=False,
            body_border=False,
            region='north',
            layout='column',
            height=35,
        )

    def _init_components(self):
        super()._init_components()

        self._init_grid_panel()
        self._init_filter_panel()
        # связываются две панели
        self.filter_cnt.configure_redirect(self.grid_panel, 'reloadgrid')
        # добавление фильтрующем панели в список исключения из read_only
        self._mro_exclude_list.append(self.filter_cnt)

    def _do_layout(self):
        super()._do_layout()

        self.layout = 'border'
        self.maximizable = self.maximized = True
        self.minimizable = True
        self.width, self.min_width = 870, 870
        self.height = 600
        self.grid_panel.layout_config['align'] = 'stretch'

        # добавление фильтрующих полей в фильтрующую панель
        assert self.filter_cnt.filters, 'Необходимо добавить элементы в список фильтров (self.filter_cnt.filters)!'

        self.items.extend([self.filter_cnt, self.grid_panel])

    def set_params(self, params):
        super().set_params(params)

        self.template_globals = 'base-grid-window.js'

        self.pack = params['grid_pack']

        # урл получения грида для панели с гридом
        self.grid_panel.grid_url = self.pack.get_grid_action_url()

        # атрибуты окна, например для cell select
        self.column_name = self.pack.column_param_name
        self.column_prefix = self.pack.column_param_name

        # заголовок окна
        self.title = self.pack.title


class RelatedErrorWindow(BaseWindow):
    """Окно с ошибкой.

    Показывается, если невозможно удаление записи из-за наличия ссылок
    на удаляемый объект.
    """

    def _init_components(self):
        super()._init_components()

        self.title = 'Внимание!'
        self.layout = 'fit'
        self.panel = ext.ExtPanel(auto_scroll=True)
        self.items.append(self.panel)

    def set_params(self, params):
        super().set_params(params)

        assert 'html' in params
        self.panel.html = params['html']


class _ListWindowMixin:
    """Класс-примесь к окнам на базе objectpack.ui.BaseListWindow.

    В отличии от BaseListWindow с read_only оставляет в гриде возможность
    просмотра по даблклику на строку, а также переделывает кнопку `изменить`
    в кнопку `просмотр`.
    """

    def __init__(self):
        super().__init__()

        self._mro_exclude_list.extend((self.grid,))

    def _init_components(self):
        super()._init_components()

        self._mro_exclude_list.remove(self.grid.top_bar.button_refresh)

    def set_params(self, params):
        super().set_params(params)

        if params.get('read_only'):
            reconfigure_grid_by_access(self.grid)


class BaseListWindow(_ListWindowMixin, OPBaseListWindow):
    """Окно с гридом с возможностью просмотра в режиме read_only.

    В отличии от :class:`~objectpack.ui.BaseListWindow` с ``read_only``
    оставляет в гриде возможность просмотра по даблклику на строку, а также
    меняет текст кнопки "Изменить" на "Просмотр".
    """


class _SelectWindowMixin(_ListWindowMixin):
    """Класс-примесь для окон выбора объектов."""

    def set_params(self, params):
        super().set_params(params)

        reconfigure_grid_by_access(self.grid, can_view=False)


class BaseSelectWindow(_SelectWindowMixin, OPBaseSelectWindow):
    """Окно выбора из списка объектов.

    В отличии от :class:`~objectpack.ui.BaseSelectWindow` оставляет в гриде
    возможность просмотра по даблклику на строку, а также меняет текст кнопки
    "Изменить"  на "Просмотр".
    """


class BaseMultiSelectWindow(_SelectWindowMixin, OPBaseMultiSelectWindow):
    """Окно множественного выбора из списка объектов.

    В отличии от :class:`~objectpack.ui.BaseMultiSelectWindow` оставляет в
    гриде возможность просмотра по даблклику на строку, а также меняет текст
    кнопки "Изменить"  на "Просмотр".
    """

    def set_params(self, params):
        super().set_params(params)

        self.grid.allow_paging = False
        self.multiselect_page_fix = local_template('templates/multiselect-page-fix.js')
        self.template_globals = local_template('templates/multiSelectWindow.js')


class EditWindowMixin:
    """Класс-примесь к окнам редактирования.

    Дополняет окно следующим функционалом:

        - скрывает кнопку "Сохранить" в режиме только для чтения;
        - кнопку "Отмена" переименовывает в "Закрыть".
    """

    def set_params(self, params):
        super().set_params(params)

        if params.get('read_only'):
            # TODO: Выпилить эту функцию, а ее код перенести сюда
            switch_window_in_read_only_mode(self)


class BaseEditWindow(EditWindowMixin, OPBaseEditWindow):
    """Базовый класс окон просмотра/редактирования.

    Отличия от :class:``objectpack.ui.BaseEditWindow`` описаны в
    :class:`educommon.objectpack.ui.EditWindowMixin`.
    """


class ModelEditWindow(EditWindowMixin, OPModelEditWindow):
    """Базовый класс для окон просмотра/редактирования объекта модели.

    Отличия от :class:``objectpack.ui.ModelEditWindow`` описаны в
    :class:`educommon.objectpack.ui.EditWindowMixin`.
    """


class TabbedEditWindow(EditWindowMixin, OPTabbedEditWindow):
    """Базовый класс для окон просмотра/редактирования с вкладками.

    Отличия от :class:``objectpack.ui.TabbedEditWindow`` описаны в
    :class:`educommon.objectpack.ui.EditWindowMixin`.
    """
