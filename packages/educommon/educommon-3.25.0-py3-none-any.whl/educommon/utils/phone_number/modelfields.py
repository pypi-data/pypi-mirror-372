from django.db.models import (
    CharField,
)

from educommon.utils.phone_number.enums import (
    PhoneFieldType,
)
from educommon.utils.phone_number.phone_number import (
    PhoneNumber,
    to_python,
)
from educommon.utils.phone_number.validators import (
    validate_common_phone_number,
    validate_e164_phone_number,
    validate_ru_e164_phone_number,
    validate_ru_mobile_phone_number,
    validate_ru_phone_number,
)


PHONE_FIELD_TYPE_TO_VALIDATOR = {
    PhoneFieldType.COMMON: validate_common_phone_number,
    PhoneFieldType.E164: validate_e164_phone_number,
    PhoneFieldType.RU: validate_ru_phone_number,
    PhoneFieldType.RU_E164: validate_ru_e164_phone_number,
    PhoneFieldType.RU_MOBILE: validate_ru_mobile_phone_number,
}


class PhoneNumberDescriptor:
    """Дескриптор для поля с номером телефона инстанса модели.

    Возвращает PhoneNumber при доступе к полю телефона.

    Позволяет для поля задавать номер телефона как:
       instance.phone = PhoneNumber(...)
    либо
        instance.phone = '+7 (900) 555-55-55'
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)

        return value

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = to_python(value)


class PhoneField(CharField):
    """Поле с номером телефона."""

    attr_class = PhoneNumber
    descriptor_class = PhoneNumberDescriptor

    empty_values = [*CharField.empty_values, PhoneNumber('')]

    def __init__(self, *args, phone_type: PhoneFieldType = PhoneFieldType.COMMON, **kwargs):
        kwargs.setdefault('max_length', 31)
        super().__init__(*args, **kwargs)

        self.validators.append(PHONE_FIELD_TYPE_TO_VALIDATOR.get(phone_type, validate_common_phone_number))

    def to_python(self, value):
        """Преобразование входящего значения в ожидаемый тип Python."""
        return to_python(value)

    def from_db_value(self, value, expression, connection):
        """Преобразование значения полученного из БД."""
        return self.to_python(value)

    def get_prep_value(self, value):
        """Подготовка значения перед сохранением в БД."""
        if isinstance(value, PhoneNumber):
            value = value.cleaned
        elif value:
            value = to_python(value).cleaned

        return value or super().get_prep_value(value)
