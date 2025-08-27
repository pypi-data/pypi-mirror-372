"""Утилиты для работы с элементами управления (интерфейсами)."""
from __future__ import (
    annotations,
)

import inspect
import os
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    TYPE_CHECKING,
    Callable,
    Type,
)

from django.conf import (
    settings,
)
from django.db.models import (
    Q,
    TextField,
)
from m3 import (
    ApplicationLogicException,
)
from m3.actions.context import (
    ActionContext,
)
from m3_ext.ui import (
    all_components as ext,
)
from m3_ext.ui.base import (
    BaseExtComponent,
)
from m3_ext.ui.icons import (
    Icons,
)
from m3_ext.ui.panels.grids import (
    ExtObjectGrid,
)

from objectpack.filters import (
    CustomFilter,
    FilterByField as _FilterByField,
)
from objectpack.tools import (
    modify,
)
from objectpack.tree_object_pack.ui import (
    BaseObjectTree,
)
from objectpack.ui import (
    BaseEditWindow,
    _create_control_for_field,
    anchor100 as obj_anchor100,
    deny_blank as obj_deny_blank,
    make_combo_box,
)

from educommon import (
    ioc,
)
from educommon.utils.misc import (
    cached_property,
)


if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )

    from objectpack.filters import (
        FilterGroup,
    )


def anchor100(*elements):
    """Установка anchor='100%' для перечня компонент."""
    return list(obj_anchor100(element) for element in elements)


def deny_blank(*elements):
    """Установка allow_blank=False для перечня компонент."""
    return list(obj_deny_blank(element) for element in elements)


def make_button(title, icon_cls, event, client_id):
    """Создает кнопку, оповещающую компонент с client_id на событие event."""
    handler = f'function() {{Ext.getCmp("{client_id}").fireEvent("{event}");}}'

    return ext.ExtButton(text=title, icon_cls=icon_cls, handler=handler)


def formed(ctl, width=-1, label_width=100, **kwargs):
    """Возращает control в контейнере."""
    cont = ext.ExtContainer(layout='form')
    cont.items.append(ctl)
    ctl.anchor = '100%'
    if width > 0:
        cont.width = width
    else:
        cont.flex = -width
    cont.label_width = label_width
    cont.anchor = '100%'
    return modify(cont, **kwargs)


class ChoicesFilter(CustomFilter):
    """Колоночный фильтр с выпадающим списком."""

    def __init__(self, choices, *args, **kwargs):
        """Метод инициализации.

        Добавляем значения для выбора и тип компонента.
        """
        self._choices = choices
        kwargs['xtype'] = 'combo'

        super().__init__(*args, **kwargs)

    def get_script(self):
        """Генерация кода компонента."""
        if callable(self._choices):
            choices = self._choices()
        else:
            choices = self._choices
        control = make_combo_box(data=list(choices))
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        control.value = None
        return [control.render()]


class ColumnFilterWithDefaultValue(_FilterByField):
    def get_script(self):
        control = _create_control_for_field(self.field, **self._field_fabric_params)
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        # Закомментировано, чтобы проставлять значение по-умолчанию
        # control.value = None
        return [control.render()]


def reconfigure_grid_by_access(grid, can_add=False, can_edit=False, can_delete=False, can_view=True):
    """Перенастраивает грид в зависимости от прав доступа.

    :param grid: Перенастраиваемый грид.
    :type grid: m3_ext.ui.panels.grids.ExtObjectGrid

    :param bool can_add: Определяет доступность функции добавления объектов.
    :param bool can_edit: Определяет доступность функции изменения объектов.
    :param bool can_delete: Определяет доступность функции удаления объектов.
    :param bool can_view: Определяет доступность функции просмотра объектов.
        Используется только в случае недоступности функции изменения объектов.
    """
    assert isinstance(grid, ExtObjectGrid), type(grid)
    grid.read_only = False
    if not can_add:
        grid.url_new = None
    if not can_edit:
        if can_view:
            grid.top_bar.button_edit.text = 'Просмотр'
            grid.top_bar.button_edit.icon_cls = Icons.APPLICATION_VIEW_DETAIL

            grid.top_bar.items.remove(grid.top_bar.button_edit)
            grid.top_bar.items.insert(0, grid.top_bar.button_edit)
        else:
            grid.url_edit = None
    if not can_delete:
        grid.url_delete = None


def reconfigure_object_tree_by_access(grid, can_add=False, can_edit=False, can_delete=False, can_view=True):
    """Перенастраивает древовидный грид в зависимости от прав доступа.

    :param grid: Перенастраиваемый грид.
    :type grid: objectpack.tree_object_pack.ui.BaseObjectTree

    :param bool can_add: Определяет доступность функции добавления объектов.
    :param bool can_edit: Определяет доступность функции изменения объектов.
    :param bool can_delete: Определяет доступность функции удаления объектов.
    :param bool can_view: Определяет доступность функции просмотра объектов.
        Используется только в случае недоступности функции изменения объектов.
    """
    assert isinstance(grid, BaseObjectTree), type(grid)

    if not can_add:
        grid.action_new = None
    if not can_edit:
        if can_view:
            grid.top_bar.button_edit.text = 'Просмотр'
            grid.top_bar.button_edit.icon_cls = Icons.APPLICATION_VIEW_DETAIL
        else:
            grid.action_edit = None
    if not can_delete:
        grid.action_delete = None


class FilterByField(_FilterByField):
    """FilterByField c возможностью расширения контрола фильтра.

    Дополнительно добавляет ActionContext, необходимый в случае если
    контролом является ExtDictSelectField.
    """

    def __init__(self, *args, **kwargs):
        self._control_creator = kwargs.pop('control_creator', None)
        parser = kwargs.pop('parser_map', None)
        if parser:
            self.parsers_map = list(self.parsers_map)
            self.parsers_map.append(parser)

        super().__init__(*args, **kwargs)

    def create_control(self):
        if self._control_creator is not None:
            return self._control_creator()

        return _create_control_for_field(self.field, **self._field_fabric_params)

    def get_control(self):
        control = self.create_control()
        control.action_context = ActionContext()
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        return control

    def get_script(self):
        return [self.get_control().render()]


class DatetimeFilterCreator:
    """Класс, создающий колоночный фильтр по интервалу для datetime поля.

    Поддерживает значения по умолчанию.
    """

    def __init__(
        self,
        model: Type[Model],
        field_name: str,
        get_from: Callable[[], None | date] = lambda: None,
        get_to: Callable[[], None | date] = lambda: None,
        min_value: Callable[[], None | date] = lambda: None,
        max_value: Callable[[], None | date] = lambda: None,
    ) -> None:
        """Фильтр по интервалу для datetime поля.

        Args:
            model: Модель для фильтра.
            field_name: Имя поля модели.
            get_from: Дата по умолчанию для фильтра "С".
            get_to: Дата по умолчанию для фильтра "По".
            min_value: Минимально возможная дата.
            max_value: Максимально возможная дата.

        Значения по умолчанию передаются в качестве callable, чтобы они
        вычислялись во время создания js. То есть, если в фильтре должна быть
        текущая дата, а пак с колонками был создан вчера, пользователь увидит
        в фильтре сегодняшнюю дату, а не вчерашнюю.
        """

        self.model = model
        self.field_name = field_name

        assert callable(get_from)
        assert callable(get_to)
        assert callable(min_value)
        assert callable(max_value)

        self.defaults = {
            'from': get_from,
            'to': get_to,
            'min': min_value if min_value() else lambda: date(1, 1, 1),
            'max': max_value,
        }

    @cached_property
    def filter(self) -> FilterGroup:
        """Фильтр для колонки.

        Returns:
            Группа колоночных фильтров для грида.
        """

        observer = ioc.get('observer')

        return FilterByField(
            self.model,
            model_register=observer,
            control_creator=lambda: ext.ExtDateField(
                value=self.defaults['from'](),
                min_value=self.defaults['min'](),
                max_value=self.defaults['max'](),
            ),
            field_name=self.field_name,
            lookup=lambda dt: Q(**{f'{self.field_name}__gte': datetime.combine(dt, time.min)}),
            tooltip='С',
        ) & FilterByField(
            self.model,
            model_register=observer,
            control_creator=lambda: ext.ExtDateField(
                value=self.defaults['to'](),
                min_value=self.defaults['min'](),
                max_value=self.defaults['max'](),
            ),
            field_name=self.field_name,
            lookup=lambda dt: Q(**{f'{self.field_name}__lte': datetime.combine(dt, time.max)}),
            tooltip='По',
        )

    @property
    def base_params(self) -> dict[str, str]:
        """Базовые параметры для store грида."""

        result = {}

        value = self.defaults['from']()
        if value is not None:
            result[self.filter._items[0]._uid] = str(value)

        value = self.defaults['to']()
        if value is not None:
            result[self.filter._items[1]._uid] = str(value)

        return result


class FilterByDateStr(_FilterByField):
    """Фильтр позволяет работать с датой в формате d.m.Y, m.Y, Y."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs['date_str'] = True

        super().__init__(*args, **kwargs)
        
        self._lookup = self._lookup if self._lookup.endswith('__icontains') else f'{self._lookup}__icontains'

    def get_q(self, params: dict) -> Q:
        """Метод возвращает Q-объект, построенный на основе данных словаря.

        Args:
            params: Словарь с лукапами.
        Returns:
            Q-объект, построенный на основе данных словаря.
        """

        if self._uid in params:
            value = '-'.join(params[self._uid].split('.')[::-1])

            return Q(**{self._lookup: value})

        return Q()


def switch_window_in_read_only_mode(window):
    """Переводит окно редактирования в режим "Только для чтения".

    Удаляет кнопку "Сохранить", на кнопке "Отмена" меняет текст на "Закрыть".

    :param window: Окно редактирования.
    :type window: :class:`objectpack.ui.BaseEditWindow`
    """
    assert isinstance(window, BaseEditWindow), type(window)

    if window.title.endswith(': Редактирование'):
        window.title = window.title[: -len('Редактирование')] + 'Просмотр'

    window.buttons.remove(window.save_btn)
    window.cancel_btn.text = 'Закрыть'


def local_template(file_name):
    """Возвращает абсолютный путь к файлу относительно модуля.

    Основное предназначение -- формирование значений полей ``template`` и
    ``template_globals`` окон, вкладок и других компонент пользовательского
    интерфейса в тех случаях, когда файл шаблона размещен в той же папке, что
    и модуль с компонентом.

    :param str file_name: Имя файла.

    :rtype: str
    """
    frame = inspect.currentframe().f_back

    root_package_name = frame.f_globals['__name__'].rsplit('.', 2)[0]
    module = __import__(root_package_name)

    TEMPLATE_DIRS = set(path for config in settings.TEMPLATES for path in config.get('DIRS', ()))

    assert any(os.path.dirname(path) in TEMPLATE_DIRS for path in module.__path__), (
        '{} package path must be in TEMPLATES config.'.format(module.__path__),
        TEMPLATE_DIRS,
    )

    # Путь к модулю вызывающей функции
    module_path = os.path.abspath(os.path.dirname(frame.f_globals['__file__']))

    for path in TEMPLATE_DIRS:
        if module_path.startswith(path):
            module_path = module_path[len(path) + 1 :]
            break

    return os.path.join(module_path, file_name)


class FilterByTextField(FilterByField):
    """Фильтр для поля TextField, с ExtStringField в качестве контрола.

    Возвращает контрол однострочного текстового поля
    вместо многострочного (ExtTextArea),
    который используется по умолчанию для TextField.
    """

    def create_control(self):
        # Работаем только с TextField
        assert isinstance(self.field, TextField)

        return ext.ExtStringField(max_length=self.field.max_length, **self._field_fabric_params)


def append_template_globals(comp, template):
    """
    Добавляет шаблон к BaseExtComponent.template_globals.

    В template_globals допускается использование как строки, так и кортежа
    со списком. Метод введен для возможности простого добавления нового
    шаблона к уже существующим без заглядывания в реализацию базовых
    классов для определения, какого типа ожидается template_globals.

    :param comp: Компонент, которому нужно добавить шаблон для рендеринга
    :type comp: BaseExtComponent
    :param template: Имя файла шаблона
    :type template: str or unicode
    """
    if not isinstance(comp, BaseExtComponent):
        raise ApplicationLogicException('Component has no attribute template_globals')
    if isinstance(comp.template_globals, str):
        # если template_globals - пустая строка, просто заменяем ее
        if len(comp.template_globals) == 0:
            comp.template_globals = template
        # иначе создаем кортеж из старого значения и добавляемого
        else:
            comp.template_globals = (comp.template_globals, template)
    elif isinstance(comp.template_globals, tuple):
        comp.template_globals += (template,)
    elif isinstance(comp.template_globals, list):
        comp.template_globals.append(template)
    else:
        raise ApplicationLogicException('Unknown type of template_globals')
