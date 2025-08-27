from enum import (
    Enum,
)


class PhoneFieldType(Enum):
    """Тип номера телефона для поля модели."""

    COMMON = 'COMMON'
    E164 = 'E164'
    RU = 'RU'
    RU_E164 = 'RU_E164'
    RU_LOCAL = 'RU_LOCAL'
    RU_MOBILE = 'RU_MOBILE'

    values = {
        COMMON: 'Общий формат телефона',
        E164: 'Международный формат телефона',
        RU: 'Общий формат российского номера',
        RU_E164: 'Российский номер в международном формате',
        RU_LOCAL: 'Российский городской номер',
        RU_MOBILE: 'Российский мобильный номер',
    }

    @classmethod
    def get_choices(cls):
        return list(cls.values.items())


class PhoneNumberType(Enum):
    """Тип формата номера телефона."""

    E164 = 'E164'
    RU_E164 = 'RU_E164'
    RU_LOCAL = 'RU_LOCAL'
    UNKNOWN = 'UNKNOWN'

    values = {
        E164: 'Международный формат телефона',
        RU_E164: 'Российский номер в международном формате',
        RU_LOCAL: 'Российский городской номер',
        UNKNOWN: 'Неизвестный формат',
    }

    @classmethod
    def get_choices(cls):
        return list(cls.values.items())
