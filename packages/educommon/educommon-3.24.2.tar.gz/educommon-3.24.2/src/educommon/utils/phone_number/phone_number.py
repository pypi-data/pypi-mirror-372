import re
from typing import (
    Any,
    Optional,
    Union,
)

from educommon.utils.phone_number.enums import (
    PhoneNumberType,
)


PHONE_REGEX = re.compile(
    r'^(?:'  # группа с кодом страны и кодом региона
    r'(\+[1-6,90]{1,3}|\+?7|\+?8)?-?\s*'  # опциональный код страны (+XXX, для России может быть +7, 7, 8)
    r'\(?(\d{3}(?:[-\s]?\d{0,2}(?=[)-.\s]))?)\)?[-.\s]*'  # оцпиональный код региона/города в необязательных скобках
    r')?'  # группа с кодом страны и кодом региона может отсутствовать
    r'(\d{1,2}[-.\s]*\d?)[-.\s]*(\d[-.\s]*\d)[-.\s]*(\d[-.\s]*\d)$'  # абонентский номер в формате XXX-XX-XX
    # первая группа может состоять от 1 до 3 цифр
)

# российский мобильный номер вида +7 (9XX) XXX-XX-XX
RU_MOBILE_PHONE_REGEX = re.compile(r'^(\+?7|8)?-?\s*\(?(9\d{2})\)?[-.\s]*(\d{3})[-.\s]*(\d{2})[-.\s]*(\d{2})$')

# местный номер в формате: XXX-XX-XX, XX-XX-XX, X-XX-XX
LOCAL_PHONE_REGEX = re.compile(r'^(\d{1,3})[-.\s]*(\d{2})[-.\s]*(\d{2})$')

RU_PHONE_CODE = '+7'


class PhoneNumber:
    """Телефонный номер.

    В качестве параметра принимает строку с номером телефона в различных форматах,
    производит разбор и валидацию номера, приводит его к единому формату.

    Поддерживаемые форматы:
      +XXX (XXX) XXX-XX-XX - в общем виде
      +7 (XXX) XXX-XX-XX - российский формат
      8 (XXX) XXX-XX-XX, (XXX-XX) X-XX-XX - российский формат городских номеров
      XXX-XX-XX, XX-XX-XX, X-XX-X - местные российские номера

    Свойство cleaned возвращает номер в очищенном виде для возможности сохранения в БД.
    Примеры входной строки и её преобразования в cleaned:
      +12 (555) 888-77-66 -> +12(555)8887766
      +7 (900) 555-44-33 -> +79005554433
      8 800 555-44-33 -> +78005554433
      (818) 222-11-00 -> +78182221100
      (818-53) 2-11-00 -> +7(81853)21100
      222 44 55 -> 2224455
      2-44-55 -> 24455

    Возвращаемое текстовое представление номера в формате:
    +XXX (XXX) XXX-XX-XX
    """

    def __init__(
        self,
        phone: Optional[str],
        *,
        need_sanitize: bool = False,
    ) -> None:
        """Инициализация.

        Args:
            need_sanitize: Признак необходимости дополнительной очистки номера перед выполнением парсинга
        """
        self.raw_phone = phone or ''
        self._need_sanitize = need_sanitize

        self._cleaned = ''

        self.country_code = ''
        self.region_code = ''
        self.subscriber_part_1 = ''
        self.subscriber_part_2 = ''
        self.subscriber_part_3 = ''

        self._is_parsed = False
        self._is_e164 = False

        self.parse()

    @staticmethod
    def _sanitize(value: str) -> str:
        """Очистка значения от незначащих символов."""
        return value.replace(' ', '').replace('-', '')

    @staticmethod
    def _only_digits(value: str) -> str:
        """Возвращает из строки только цифры."""
        return ''.join(ch for ch in value if ch.isdigit())

    @property
    def _sanitized(self) -> str:
        """Возвращает введенный номер в очищенном виде."""
        return self._sanitize(self.raw_phone)

    def parse(self):
        """Разбор номера."""
        if self._is_parsed or not self.raw_phone:
            return

        raw_phone = self._sanitized if self._need_sanitize else self.raw_phone.strip()
        regex_match = PHONE_REGEX.search(raw_phone)

        self._is_parsed = True

        if regex_match:
            self.subscriber_part_1 = self._only_digits(regex_match.group(3))
            self.subscriber_part_2 = self._only_digits(regex_match.group(4))
            self.subscriber_part_3 = self._only_digits(regex_match.group(5))

            self.region_code = regex_match.group(2)
            if self.region_code:
                self.region_code = self._sanitize(self.region_code)

            country_code = regex_match.group(1)

            if country_code in ('8', '7') or (not country_code and self.region_code):
                self.country_code = RU_PHONE_CODE
            else:
                self.country_code = country_code

            if self.country_code == RU_PHONE_CODE and (len(self.region_code) + len(self.subscriber_part_1)) != 6:
                # у российских номеров код региона и первый блок абонентского номера в сумме должны быть 6 цифр
                return

            if self.region_code:
                self._is_e164 = True

                if len(self.region_code) != 3 or len(self.country_code) > 2:
                    cleaned_template = '{0}({1}){2}{3}{4}'
                else:
                    cleaned_template = '{0}{1}{2}{3}{4}'

                self._cleaned = cleaned_template.format(
                    self.country_code,
                    self.region_code,
                    self.subscriber_part_1,
                    self.subscriber_part_2,
                    self.subscriber_part_3,
                )

            else:
                self._cleaned = '{0}{1}{2}'.format(
                    self.subscriber_part_1,
                    self.subscriber_part_2,
                    self.subscriber_part_3,
                )

    @property
    def type(self) -> PhoneNumberType:
        """Тип номера."""
        if self.is_valid:
            if self.country_code == RU_PHONE_CODE:
                return PhoneNumberType.RU_E164

            elif self.country_code:
                return PhoneNumberType.E164

            elif not self.country_code:
                return PhoneNumberType.RU_LOCAL

        return PhoneNumberType.UNKNOWN

    @property
    def is_valid(self) -> bool:
        """Признак корректности введенного номера."""
        return True if self._is_parsed and self._cleaned else False

    @property
    def is_e164(self):
        """Признак, что номер в международном формате."""
        return self._is_e164

    @property
    def is_russia(self) -> bool:
        """Признак, что номер российский."""
        return self._cleaned.startswith(RU_PHONE_CODE) or (self.is_valid and not self.region_code)

    @property
    def cleaned(self) -> str:
        """Очищенный номер.

        Используется для сохранения в БД.
        """
        return self._cleaned

    @property
    def formatted(self) -> str:
        """Отформатированный номер для отображения пользователю."""
        if not self.is_valid:
            return ''

        formatted_number = '{0}-{1}-{2}'.format(
            self.subscriber_part_1,
            self.subscriber_part_2,
            self.subscriber_part_3,
        )

        if self._is_e164:
            formatted_number = '{0} ({1}) {2}'.format(
                self.country_code,
                self.region_code,
                formatted_number,
            )

        return formatted_number

    def __str__(self) -> str:
        """Текстовое представление."""
        if self.is_valid:
            return self.formatted
        else:
            return self.raw_phone

    def __repr__(self) -> str:
        """Представление объекта."""
        if self.is_valid or not self.raw_phone:
            return '<{0}: {1}>'.format(type(self).__name__, str(self) or "''")

        else:
            return '<Invalid {0}: raw_phone="{1}">'.format(type(self).__name__, self.raw_phone)

    def __len__(self):
        return len(self.cleaned)

    def __bool__(self):
        return bool(self.cleaned)

    def __hash__(self):
        return hash(self.cleaned)

    def __eq__(self, other_phone) -> bool:
        if isinstance(other_phone, str):
            other_phone = PhoneNumber(other_phone)

        elif not isinstance(other_phone, PhoneNumber):
            return False

        self_str = self.formatted if self.is_valid else self.raw_phone
        other_str = other_phone.formatted if other_phone.is_valid else other_phone.raw_phone

        return self_str == other_str

    def __add__(self, other: str) -> str:
        """Конкатенация со строкой."""
        return str(self) + other

    def __radd__(self, other: str) -> str:
        """Конкатенация со строкой."""
        return other + str(self)


def to_python(value: Any) -> Union[PhoneNumber, str, None]:
    """Преобразование значения к объекту номера телефона."""
    if value in (None, ''):
        phone_number = value

    elif isinstance(value, str):
        phone_number = PhoneNumber(value)

    elif isinstance(value, PhoneNumber):
        phone_number = value

    else:
        raise TypeError(f'Невозможно преобразовать {type(value).__name__} к PhoneNumber.')

    return phone_number
