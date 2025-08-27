"""Дополнение колоночных фильтров."""

from django.db.models.expressions import (
    Q,
)
from m3.actions import (
    DeclarativeActionContext,
)
from m3.plugins import (
    ExtensionManager,
)
from m3_ext.ui import (
    all_components as ext,
)

from objectpack.filters import (
    ColumnFilterEngine as BaseFilterEngine,
    CustomFilter,
)
from objectpack.ui import (
    _create_control_for_field,
    make_combo_box,
)

from educommon.utils.ui import (
    ColumnFilterWithDefaultValue,
)


class ColumnFilterEngine(BaseFilterEngine):
    """Колоночные фильтры с возможностью расширения плагином."""

    def configure_grid(self, grid):
        """Метод конфигурации грида."""
        # расширение плагином
        if not ExtensionManager().execute('column_filter_engine.configure_grid', self, grid):
            super().configure_grid(grid)


class ModifiedChoicesFilter(CustomFilter):
    """Колоночный фильтр с выпадающим списком."""

    def __init__(self, choices, *args, **kwargs):
        """Метод инициализации.

        Добавляем значения для выбора и тип компонента.
        """
        self._choices = choices
        kwargs['xtype'] = 'combo'

        super().__init__(*args, **kwargs)

    def create_control(self):
        """Контрол."""
        if callable(self._choices):
            choices = self._choices()
        else:
            choices = self._choices

        return make_combo_box(data=list(choices))

    def get_control(self):
        """Настройка контрола."""
        control = self.create_control()
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        control.value = None

        return control

    def get_script(self):
        """Генерация кода компонента."""
        return [self.get_control().render()]


class BoolChoicesFilter(ModifiedChoicesFilter):
    """Колоночный фильтр с выпадающим списком значений булевого поля."""

    def __init__(self, field_name, *args, **kwargs):
        """Инициализация параметров."""
        choices = ((None, ''), (True, 'Да'), (False, 'Нет'))

        def lookup(v):
            """Формирование lookup для фильтра."""
            return Q(**{field_name: v}) if v is not None else Q()

        super().__init__(*args, choices=choices, parser='boolean', lookup=lookup, **kwargs)


class DateFilter(ColumnFilterWithDefaultValue):
    """Колоночный фильтр по датам."""

    def create_control(self):
        """Создание контрола."""
        return _create_control_for_field(self.field, **self._field_fabric_params)

    def get_control(self):
        """Настройка контрола."""
        control = self.create_control()
        control.value = self.default_value
        control._put_config_value('filterName', self._uid)
        control._put_config_value('tooltip', self._tooltip or control.label)
        control.name = self._uid
        control.allow_blank = True
        control.hide_clear_trigger = False
        return control

    def get_script(self):
        """Рендер контрола."""
        return [self.get_control().render()]


class DateFilterByAnnotatedField(DateFilter):
    """
    Колоночный фильтр по аннотируему полю даты.

    Фильтр по полю, которое отсутствует у модели и данные по которому
    собираются в кварисете через annotate.
    """

    def __init__(self, model, field_name, lookup=None, tooltip=None, default_value=None, **field_fabric_params):
        """Инициализация параметров."""
        field_name = field_name.replace('.', '__')
        self._model = model
        self._field_name = field_name
        self._tooltip = tooltip
        self._field_fabric_params = field_fabric_params
        self._default_value = default_value
        self._parser = DeclarativeActionContext._parsers['datetime']
        if lookup:
            # шаблонизация лукапа, если петтерн указан
            if not callable(lookup) and '%s' in lookup:
                lookup = lookup % field_name
        else:

            def lookup(x):
                return Q(**{field_name: x})

        self._lookup = lookup

    def create_control(self):
        """Создание контрола."""
        params = {'format': 'd.m.Y'}
        params.update(**self._field_fabric_params)

        return ext.ExtDateField(**params)
