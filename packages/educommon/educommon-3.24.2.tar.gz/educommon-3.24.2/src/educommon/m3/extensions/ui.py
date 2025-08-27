"""Расширение поведения интерфейсов."""

from m3_ext.ui import (
    all_components as ext,
)

from objectpack.ui import (
    model_fields_to_controls,
)


class BaseEditWinExtender:
    """Базовый объект для расширения окон редактирования.

    ``_extend_edit_win`` - добавление и размещение контролов
    ``bind_to_object`` - заполнение объекта данными из полей формы
    ``bind_from_object`` - заполнение полей формы из объекта
    """

    # основная модель, которая редактируется в окне (расширяемая модель)
    model = None
    # список имен полей доп.модели (которой расширяется основная модель model)
    model_fields = None
    # реестр моделей-паков (обычно observer)
    # не обязательно, если не будет использоваться ``model_fields_to_controls``
    model_register = None

    def __init__(self, win):
        # ожидается окно
        self._win = win
        self._extend_edit_win()

    def _extend_edit_win(self):
        """Расширение формы окна.

        ..code::

            for fld in self.model_fields_to_controls(self.model_fields):
                self._win.form.items.append(fld)
        """
        raise NotImplementedError()

    def model_fields_to_controls(self, fields):
        """Шорткат для генерации контролов."""
        assert self.model, 'No model defined in Extender!'
        return model_fields_to_controls(self.model, self._win, field_list=fields, model_register=self.model_register)

    # -------------------------------------------------------------------------
    # Биндинг из формы в объект

    @classmethod
    def set_value(cls, instance, field_names, value):
        """Установка значения поля (полей).

        :param instance: инстанс модели, которая расширяет основную ``model``
        :param list field_names: список связаных полей (либо одно поле)
        :raise: DoesNotExist если предварительно не инстанцировали зависимые
        сущности (для случая связанных полей).
        """
        if len(field_names) == 1:
            # связанных полей нет
            setattr(instance, field_names[0], value)
        else:
            # есть связанные поля, достаются связанные сущности
            # связанные сущности должны быть получены
            nested = getattr(instance, field_names[0])
            cls.set_value(nested, field_names[1:], value)

    @classmethod
    def bind_to_object(cls, instance, context):
        """Заполнение полей ``model_fields`` модели instance по полям формы.

        :param instance: инстанс модели, которая расширяет основную ``model``
        :param context: контекст
        :type context: m3.actions.context.DeclarativeActionContext
        """
        assert cls.model_fields is not None, 'No model_fields defined in Extender'

        for field_name in cls.model_fields:
            try:
                value = getattr(context, field_name)
            except AttributeError:
                value = None

            field_names = field_name.split('.')
            cls.set_value(instance, field_names, value)

    # -------------------------------------------------------------------------
    # Биндинг из объекта в форму

    def bind_from_object(self, instance):
        """Заполнение полей ``model_fields`` формы по полям модели instance.

        :param instance: инстанс модели, которая расширяет основную ``model``
        """
        assert self.model_fields is not None, 'No model_fields defined in Extender'
        for name in self.model_fields:
            field = self._win.find_by_name(name)
            field_names = field.name.split('.')
            value = self._get_value(instance, field_names)
            if value:
                self._set_value_to_field(field, value)

    def _get_value(self, instance, field_names):
        """Получение значение поля (полей).

        :param instance: инстанс модели, которая расширяет основную ``model``
        :param list field_names: список связаных полей (либо одно поле)
        :raise: DoesNotExist если предварительно не инстанцировали зависимые
        сущности (для случая связанных полей)
        """
        if len(field_names) == 1:
            # связанных полей нет
            return getattr(instance, field_names[0], None)
        else:
            # есть связанные поля, достаются связанные сущности
            nested = getattr(instance, field_names[0], None)
            return self._get_value(nested, field_names[1:])

    @staticmethod
    def _set_value_to_field(field, value):
        """Установка значения в поле.

        :param field: наследник BaseExtField
        :param value: значение для установки в поле
        """
        field.value = value
        if isinstance(field, ext.ExtDictSelectField):
            pack = getattr(field, 'pack', None)
            if pack:
                if isinstance(field, ext.ExtMultiSelectField):
                    field.value = pack.model.get_serialized_values(value)
                else:
                    field.default_text = pack.get_display_text(value, field.display_field)
        elif isinstance(field, ext.ExtCheckBox):
            field.checked = bool(value)

    def set_params(self, params):
        """Установка параметров компонентам.

        Выполняется по завершению создания компонент, размещению на форме и
        после биндинга значений в форму.

        ..code::

            self._win.field__some.make_read_only(access_off=params['instance'].date > datetime.date.today())
        """
        pass
