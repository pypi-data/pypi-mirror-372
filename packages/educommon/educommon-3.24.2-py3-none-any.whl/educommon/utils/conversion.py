import itertools
import re
from typing import (
    Optional,
    Union,
)
from uuid import (
    UUID,
)

from _decimal import (
    Decimal,
)


def str_or_empty(value) -> str:
    """Возвращает строковое значение если оно истинно, иначе пустую строку."""
    return str(value) if value else ''


def str_without_control_chars(value: str) -> str:
    """Возвращает строку без управляющих символов."""
    return control_char_re.sub('', value) if value else ''


def uuid_or_none(value) -> Optional[UUID]:
    """Преобразует строку в UUID или возвращает None."""
    if value is None or isinstance(value, UUID):
        return value
    try:
        return UUID(value)
    except (AttributeError, ValueError):
        return None


def int_or_none(value: Union[int, str, None]) -> Optional[int]:
    """Преобразование значения к числу."""
    result = None

    if value:
        try:
            result = int(value)
        except (TypeError, ValueError):
            pass

    return result


def decimal_or_none(value: Union[int, str, None]) -> Optional[Decimal]:
    """Преобразование значения к десятичному числу."""
    result = None

    if value:
        try:
            result = Decimal(value)
        except (TypeError, ValueError):
            pass

    return result


def float_or_none(value: Union[int, str, None]) -> Optional[float]:
    """Преобразование значения к числу с плавающей точкой."""
    result = None

    if value:
        try:
            result = float(value)
        except (TypeError, ValueError):
            pass

    return result


control_chars = ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))))
control_char_re = re.compile(f'[{re.escape(control_chars)}]')
