"""Кастомные поля моделей Django"""

from datetime import (
    datetime,
    timedelta,
)

from django.core import (
    validators,
)
from django.db.models import (
    fields,
)

from objectpack import (
    IMaskRegexField,
)

from educommon.django.db.migration import (
    date_difference_as_callable,
)
from educommon.django.db.validators import (
    simple,
)
from educommon.utils.misc import (
    cached_property,
)
from educommon.utils.phone_number.modelfields import (
    PhoneField,
)


__all__ = [
    'SingleErrorDecimalField',
    'FIOField',
    'RangedDateField',
    'LastNameField',
    'FirstNameField',
    'MiddleNameField',
    'SNILSField',
    'BirthDateField',
    'DocumentSeriesField',
    'DocumentNumberField',
    'PassportSeriesField',
    'PassportNumberField',
    'INNField',
    'KPPField',
    'OGRNField',
    'PhoneField',
]


class SingleErrorDecimalField(fields.DecimalField):
    """
    Кастомный класс поля Decimal.

    Переопределяется метод validators для подключения
    SingleErrorDecimalValidator который приводит сообщение об ошибке к единому
    стилю не разделя ошибки по переполнению целой + дробной части и отдельно
    целой.
    """

    @cached_property
    def validators(self):
        """Переопрелеление стандартного валидатора Decimal.

        :return: Список валидаторов.
        """
        validators = super(SingleErrorDecimalField, self).validators

        validators.pop()
        validators.append(simple.SingleErrorDecimalValidator(self.max_digits, self.decimal_places))

        return validators


class FIOField(fields.CharField, IMaskRegexField):
    """Поле для ввода ФИО с маской и валидацией.

    Разрешены только буквы, пробелы и дефисы.
    """

    _mask_re = r'^[а-яА-ЯёЁa-zA-Z\s-]*$'

    default_validators = [simple.FIOValidator()]


class RangedDateField(fields.DateField):
    """Поле, реализующее валидаторы по умолчанию для границ периода"""

    def __init__(self, minimum_date=datetime(1, 1, 1).date(), maximum_date=None, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(simple.date_range_validator(minimum=minimum_date, maximum=maximum_date))


class LastNameField(FIOField):
    """Расширение поля ФИО для фамилии"""

    def __init__(self, verbose_name='Фамилия', max_length=30, **kwargs):
        super().__init__(verbose_name=verbose_name, max_length=max_length, **kwargs)


class FirstNameField(FIOField):
    """Расширение поля ФИО для имени"""

    def __init__(self, verbose_name='Имя', max_length=30, **kwargs):
        super().__init__(verbose_name=verbose_name, max_length=max_length, **kwargs)


class MiddleNameField(FIOField):
    """Расширение поля ФИО для отчества"""

    def __init__(self, verbose_name='Отчество', null=True, blank=True, max_length=30, **kwargs):
        super().__init__(verbose_name=verbose_name, null=null, blank=blank, max_length=max_length, **kwargs)


class SNILSField(fields.CharField, IMaskRegexField):
    """Поле модели для ввода СНИЛС с маской и валидацией."""

    _mask_re = r'^[-\s\d]{0,14}$'

    default_validators = [simple.SNILSValidator()]

    def __init__(self, verbose_name='СНИЛС', **kwargs):
        kwargs.setdefault('max_length', 14)

        super().__init__(verbose_name=verbose_name, **kwargs)


class BirthDateField(RangedDateField):
    """Поле даты рождения с ограничением по минимальной и максимальной дате."""

    def __init__(
        self,
        minimum_date=datetime(1, 1, 1).date(),
        maximum_date=date_difference_as_callable(timedelta(days=1)),
        verbose_name='Дата рождения',
        **kwargs,
    ):
        super().__init__(minimum_date=minimum_date, maximum_date=maximum_date, verbose_name=verbose_name, **kwargs)


class DocumentSeriesField(fields.CharField, IMaskRegexField):
    """Поле серии документа с маской и соответствующим валидатором."""

    _mask_re = r'^[a-zA-Zа-яА-ЯёЁ\d\s|\-|\.|\,|\\|\/]*$'

    default_validators = [simple.DocumentSeriesValidator()]

    def __init__(self, verbose_name='Серия документа', **kwargs):
        super().__init__(verbose_name=verbose_name, **kwargs)


class DocumentNumberField(fields.CharField, IMaskRegexField):
    """Поле номера документа с маской и соответствующим валидатором."""

    _mask_re = r'^[a-zA-Zа-яА-ЯёЁ\d\s|\-|\.|\,|\\|\/]*$'

    default_validators = [simple.DocumentNumberValidator()]

    def __init__(self, verbose_name='Номер документа', **kwargs):
        super().__init__(verbose_name=verbose_name, **kwargs)


class PassportSeriesField(DocumentSeriesField):
    """Поле серии паспорта с числовой маской и ограничением по длине."""

    _mask_re = r'^\d{0,4}$'

    default_validators = [simple.PassportSeriesValidator()]

    def __init__(self, verbose_name='Серия паспорта', **kwargs):
        kwargs.setdefault('max_length', 4)

        super().__init__(verbose_name=verbose_name, **kwargs)


class PassportNumberField(DocumentNumberField):
    """Поле номера паспорта с числовой маской и ограничением по длине."""

    _mask_re = r'^\d{0,6}$'

    default_validators = [simple.PassportNumberValidator()]

    def __init__(self, verbose_name='Номер паспорта', **kwargs):
        kwargs.setdefault('max_length', 6)

        super().__init__(verbose_name=verbose_name, **kwargs)


class INNField(fields.CharField, IMaskRegexField):
    """Поле ИНН с маской и встроенной валидацией."""

    _mask_re = r'^\d{0,12}$'

    default_validators = [simple.inn_validator]

    def __init__(self, verbose_name='ИНН', **kwargs):
        kwargs.setdefault('max_length', 12)

        super().__init__(verbose_name=verbose_name, **kwargs)


class KPPField(fields.CharField, IMaskRegexField):
    """Поле КПП с маской, без дублирования ошибок превышения длины."""

    _mask_re = r'^\d{0,9}$'

    default_validators = [simple.kpp_validator]

    def __init__(self, verbose_name='КПП', **kwargs):
        kwargs.setdefault('max_length', 9)

        super().__init__(verbose_name=verbose_name, **kwargs)

        # из за стандартного валидатора дублируются сообщения об ошибке
        # привышения длинны поля
        try:
            self.validators.remove(validators.MaxLengthValidator(self.max_length))
        except ValueError:
            pass


class OGRNField(fields.CharField, IMaskRegexField):
    """Поле ОГРН с маской и встроенной валидацией."""

    _mask_re = r'^\d{0,15}$'

    default_validators = [simple.ogrn_validator]

    def __init__(self, verbose_name='ОГРН', **kwargs):
        kwargs.setdefault('max_length', 15)

        super().__init__(verbose_name=verbose_name, **kwargs)
