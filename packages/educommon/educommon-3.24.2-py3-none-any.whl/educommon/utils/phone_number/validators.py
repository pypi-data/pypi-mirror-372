from typing import (
    Union,
)

from django.core.exceptions import (
    ValidationError,
)

from educommon.utils.phone_number.phone_number import (
    PhoneNumber,
    to_python,
)


def validate_common_phone_number(phone_number: Union[str, PhoneNumber]):
    """Валидация номера телефона в общем формате."""
    phone_number = to_python(phone_number)

    if isinstance(phone_number, PhoneNumber) and not phone_number.is_valid:
        raise ValidationError(
            'Неверный формат! Примеры допустимых форматов: +XXX (XXX) XXX XX XX, 8 (XXXXX) X-XX-XX, XXX-XX-XX',
            code='invalid',
        )


def validate_e164_phone_number(phone_number: Union[str, PhoneNumber]):
    """Валидация номера телефона в международном формате."""
    phone_number = to_python(phone_number)

    if isinstance(phone_number, PhoneNumber) and not phone_number.is_valid or not phone_number.is_e164:
        raise ValidationError(
            'Неверный формат! Примеры допустимых форматов: +XXX (XXX) XXX XX XX, +7 (XXX) XXX-XX-XX, 8 (XXXXX) X-XX-XX',
            code='invalid',
        )


def validate_ru_phone_number(phone_number: Union[str, PhoneNumber]):
    """Валидация российского номера телефона в общем формате."""
    phone_number = to_python(phone_number)

    if isinstance(phone_number, PhoneNumber) and not phone_number.is_valid or not phone_number.is_russia:
        raise ValidationError(
            'Неверный формат! Примеры допустимых форматов: +7 (XXX) XXX-XX-XX, 8 (XXXXX) X-XX-XX, XXX-XX-XX',
            code='invalid',
        )


def validate_ru_e164_phone_number(phone_number: Union[str, PhoneNumber]):
    """Валидация российского номера телефона в международном формате."""
    phone_number = to_python(phone_number)

    if (
        isinstance(phone_number, PhoneNumber)
        and not phone_number.is_valid
        or not (phone_number.is_russia and phone_number.is_e164)
    ):
        raise ValidationError(
            'Неверный формат! Примеры допустимых форматов: +7 (XXX) XXX-XX-XX, 8 (XXXXX) X-XX-XX, (XXX) XXX-XX-XX',
            code='invalid',
        )


def validate_ru_mobile_phone_number(phone_number: Union[str, PhoneNumber]):
    """Валидация российского мобильного номера телефона."""
    phone_number = to_python(phone_number)

    if (
        isinstance(phone_number, PhoneNumber)
        and not phone_number.is_valid
        or not (
            phone_number.region_code and len(phone_number.region_code) == 3 and phone_number.region_code.startswith('9')
        )
    ):
        raise ValidationError(
            'Неверный формат! Примеры допустимых форматов: +7 (9XX) XXX-XX-XX, 7 (9XX) XXX XX XX, 89XXXXXXXXX',
            code='invalid',
        )
