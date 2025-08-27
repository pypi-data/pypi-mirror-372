"""Утилиты для ObjectGrid."""

import json

from m3.actions.urls import (
    get_url,
)
from m3_ext.ui import (
    all_components as ext,
)


def add_action_button(label, grid, action, icon_cls, index=None):
    """
    Добавление кнопки в тулбар ObjectGrid'а.

    label - Имя кнопки
    grid - ObjectGrid
    action - Action для кнопки
    icon_cls - Значек кнопки
    index - Позиция добавления кнопки. По-умолчанию справа.

    Примеры подключения и использования для ObjectPack'а:

    def create_list_window(self, *args, **kwargs):
        win = super(ObjectPack, self).create_list_window(*args, **kwargs)
        append_template_globals(win, 'ui-js/object-grid-buttons.js')
        return win

    def configure_grid(self, grid, *args, **kwargs):
        super(ObjectPack, self).configure_grid(grid, *args, **kwargs)
        add_action_button('Печать', grid, self.print_action, Icons.PRINTER)
    """
    action_url = get_url(action)
    button = ext.ExtButton(text=label, handler=_get_action_handler(action_url), icon_cls=icon_cls)
    if index is not None:
        grid.top_bar.items.insert(index, button)
    else:
        grid.top_bar.items.append(button)


def add_one_row_button(label, grid, action, icon_cls, dbl_clicked=False, index=None):
    """
    Добавление кнопки в тулбар и popup меню ObjectGrid'а.

    label - Имя кнопки
    grid - ObjectGrid
    action - Action для кнопки
    icon_cls - Значек кнопки
    dbl_clicked - Вызов действия по даблклику строк
    index - Позиция добавления кнопки. По-умолчанию справа.

    Примеры подключения и использования для ObjectPack'а:

    def create_list_window(self, *args, **kwargs):
        win = super(ObjectPack, self).create_list_window(*args, **kwargs)
        append_template_globals(win, 'ui-js/object-grid-buttons.js')
        return win

    def configure_grid(self, grid, *args, **kwargs):
        super(ObjectPack, self).configure_grid(grid, *args, **kwargs)
        grid.url_edit = None
        add_one_row_button('Просмотр', grid, self.edit_window_action,
                           Icons.APPLICATION_VIEW_DETAIL, dbl_clicked=True)
    """
    params = _get_one_row_params(label, action, icon_cls)
    button = ext.ExtButton(**params)
    if index is not None:
        grid.top_bar.items.insert(index, button)
    else:
        grid.top_bar.items.append(button)

    menuitem = ext.ExtContextMenuItem(**params)
    grid.context_menu_row.items.append(menuitem)

    if dbl_clicked:
        grid.dblclick_handler = button.handler
        grid.handler_dblclick = grid.dblclick_handler


def add_multi_row_button(label, grid, action, icon_cls, confirm_required=False, index=None):
    """
    Добавление кнопки в тулбар и popup меню ObjectGrid'а.

    label - Имя кнопки
    grid - ObjectGrid
    action - Action для кнопки
    icon_cls - Значек кнопки
    confirm_required - Запрашивать подтверждение действия.
    index - Позиция добавления кнопки. По-умолчанию справа.

    Примеры подключения и использования для ObjectPack'а:

    def create_list_window(self, *args, **kwargs):
        win = super(ObjectPack, self).create_list_window(*args, **kwargs)
        append_template_globals(win, 'ui-js/object-grid-buttons.js')
        return win

    def configure_grid(self, grid, *args, **kwargs):
        super(ObjectPack, self).configure_grid(grid, *args, **kwargs)
        add_multi_row_button(
            'Переотправить', grid, self.resend_action,
            'icon_send_message ' + Icons.ARROW_ROTATE_CLOCKWISE
        )
    """
    params = _get_multirow_params(label, action, icon_cls, confirm_required)
    button = ext.ExtButton(**params)
    if index is not None:
        grid.top_bar.items.insert(index, button)
    else:
        grid.top_bar.items.append(button)

    menuitem = ext.ExtContextMenuItem(**params)
    grid.context_menu_row.items.append(menuitem)


def _get_one_row_params(label, action, icon_cls):
    action_url = get_url(action)
    return dict(
        text=label,
        icon_cls=icon_cls,
        handler=_get_one_row_handler(label, action_url),
    )


def _get_multirow_params(label, action, icon_cls, confirm_required):
    action_url = get_url(action)
    return dict(
        text=label,
        icon_cls=icon_cls,
        handler=_get_multi_row_handler(label, action_url, confirm_required),
    )


def _get_action_handler(url):
    return f"""
        function() {{
            onObjGridAction(objGrid, '{url}');
        }}
    """


def _get_one_row_handler(action_name, url):
    return f"""
        function() {{
            onObjGridOneRecordAction(objGrid, '{action_name}', '{url}');
        }}
    """


def _get_multi_row_handler(action_name, url, confirm_required):
    return f"""
        function() {{
            onObjGridMultiRecordAction(objGrid, '{action_name}', '{url}', {int(bool(confirm_required))});
        }}
    """


def column_style_renderer(styles_map, default_style=''):
    """Изменение стиля в колонке.

    :param styles_map: словарь карты стилей по значению в колонке
    :param default_style: стиль по-умолчанию
    """
    styles_map = json.dumps(styles_map)

    return f"""
    function (value, metaData, record, rowIndex, colIndex, store) {{
        var styles_map = Ext.util.JSON.decode('{styles_map}');
        metaData.style += styles_map[value] || '{default_style}';
        return value;
    }}
    """


def set_grid_initial(grid, initializers):
    """Установка инициализирующих грид функций.

    :param grid: грид.
    :param initializers: список инициализирующих грид функций

    Пример:

    def configure_grid(self, grid, *args, **kwargs):
        super(ObjectPack, self).configure_grid(
            grid, *args, **kwargs)
        set_grid_initial(grid, (
            styling_grid_rows(
                'result_status_code', ResultStatus.styles,
                'grid-row-yellow-background'
            ),
        ))
    """
    grid_initializers = ''.join(initializers)
    grid._listeners['added'] = f"""
        function() {{
            var grid = Ext.getCmp('{grid.client_id}');
            {grid_initializers}
        }}
    """


def styling_grid_rows(data_index, styles_map, default_style=''):
    """Стилизация строк грида по значению в колонке.

    :param data_index: имя колонки
    :param styles_map: словарь карты стилей по значению в колонке
    :param default_style: стиль по-умолчанию
    """
    styles_map = json.dumps(styles_map)

    return f"""
        var styles_map = Ext.util.JSON.decode('{styles_map}');
        grid.getView().getRowClass = function(record, rowIndex, rp, ds) {{
            return styles_map[
                record.json.{data_index}
            ] || '{default_style}';
        }};
    """


def add_tooltip_to_grid_rows(delegate: str, column_with_text: str) -> str:
    """Добавление всплывающей подсказки для строк грида.

    :param delegate: css-класс строк к которым добавляется подсказка
    :param column_with_text: наименование колонки содержащей текст подсказки
    """
    return f"""
        var view = grid.getView();
        var store = grid.getStore();
        grid.on('render', function(grid) {{
            grid.tooltip = new Ext.ToolTip({{
                target: view.mainBody,
                delegate: '{delegate}',
                listeners: {{
                    show: function updateTipBody(tooltip) {{
                        var rowIndex = view.findRowIndex(tooltip.triggerElement);
                        var text = store.getAt(rowIndex).data['{column_with_text}'];
                        tooltip.update(text);
                    }}
                }}
            }});
        }});
    """


def boolean_column_renderer():
    """
    Возвращает JS-рендерер для булевых колонок грида
    """
    return 'function(v){return (!!v ? "Да" : "Нет")}'
