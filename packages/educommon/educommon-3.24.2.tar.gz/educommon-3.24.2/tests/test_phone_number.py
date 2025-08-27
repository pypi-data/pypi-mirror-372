from typing import (
    NamedTuple,
)
from unittest import (
    TestCase,
)

from educommon.utils.phone_number.enums import (
    PhoneNumberType as ptype,
)
from educommon.utils.phone_number.phone_number import (
    PhoneNumber,
)


class RawPhone(NamedTuple):
    input_value: str
    expected_cleaned: str
    expected_str: str
    type: ptype
    is_valid: bool


class PhoneNumberTestCase(TestCase):
    """Набор тестов для PhoneNumber."""

    raw_phone_numbers = (
        RawPhone('+12 555 888 77 66', '+12(555)8887766', '+12 (555) 888-77-66', ptype.E164, True),
        RawPhone('+12 5558 88 77 66', '+12(5558)887766', '+12 (5558) 88-77-66', ptype.E164, True),
        RawPhone('+7 (900) 888-77-66', '+79008887766', '+7 (900) 888-77-66', ptype.RU_E164, True),
        RawPhone('(903) 555-77-66', '+79035557766', '+7 (903) 555-77-66', ptype.RU_E164, True),
        RawPhone('8-900-123-45-67', '+79001234567', '+7 (900) 123-45-67', ptype.RU_E164, True),
        RawPhone('8818 57 23 461', '+7(81857)23461', '+7 (81857) 2-34-61', ptype.RU_E164, True),
        RawPhone('(81853)4-64-32', '+7(81853)46432', '+7 (81853) 4-64-32', ptype.RU_E164, True),
        RawPhone('8 900 22 23 461', '+7(90022)23461', '+7 (90022) 2-34-61', ptype.RU_E164, True),
        RawPhone('8 900 222 34 61', '+79002223461', '+7 (900) 222-34-61', ptype.RU_E164, True),
        RawPhone('8 (900) 22 23 461', '+79002223461', '+7 (900) 222-34-61', ptype.RU_E164, True),
        RawPhone('8 (818-53) 4-64-32', '+7(81853)46432', '+7 (81853) 4-64-32', ptype.RU_E164, True),
        RawPhone('8 818-53 4-64-32', '+7(81853)46432', '+7 (81853) 4-64-32', ptype.RU_E164, True),
        RawPhone('8 (818 53) 4-64-32', '+7(81853)46432', '+7 (81853) 4-64-32', ptype.RU_E164, True),
        RawPhone('334-64-32', '3346432', '334-64-32', ptype.RU_LOCAL, True),
        RawPhone('333-2-333', '3332333', '333-23-33', ptype.RU_LOCAL, True),
        RawPhone('3 22 33', '32233', '3-22-33', ptype.RU_LOCAL, True),
        RawPhone('222-3-3-3-3', '2223333', '222-33-33', ptype.RU_LOCAL, True),
        RawPhone('382 222-3-3-3-3', '+73822223333', '+7 (382) 222-33-33', ptype.RU_E164, True),
        RawPhone('(8-818-53)4-22-12', '', '(8-818-53)4-22-12', ptype.UNKNOWN, False),
        RawPhone('+7 (81853) 888-77-66', '', '+7 (81853) 888-77-66', ptype.UNKNOWN, False),
        RawPhone('', '', '', ptype.UNKNOWN, False),
        RawPhone(None, '', '', ptype.UNKNOWN, False),
    )

    def test_parse_phone_number(self):
        for raw_phone_number in self.raw_phone_numbers:
            phone_number = PhoneNumber(raw_phone_number.input_value)

            self.assertIs(phone_number.is_valid, raw_phone_number.is_valid)
            self.assertEqual(phone_number.cleaned, raw_phone_number.expected_cleaned)
            self.assertEqual(str(phone_number), raw_phone_number.expected_str)
            self.assertEqual(phone_number.type, raw_phone_number.type)

    def test_formatted_phone_number(self):
        self.assertEqual(PhoneNumber('(903) 555-77-66').formatted, '+7 (903) 555-77-66')
        self.assertEqual(PhoneNumber('555 77 66').formatted, '555-77-66')
        self.assertEqual(PhoneNumber('555').formatted, '')

    def test_need_sanitize_phone_number(self):
        invalid_phone_number_str = '8 (900) 2-2-2 3-3 4-4'
        invalid_phone_number = PhoneNumber(invalid_phone_number_str)

        self.assertIs(invalid_phone_number.is_valid, False)

        valid_phone_number = PhoneNumber(invalid_phone_number_str, need_sanitize=True)

        self.assertIs(valid_phone_number.is_valid, True)
        self.assertEqual(valid_phone_number._sanitized, '8(900)2223344')
        self.assertEqual(valid_phone_number.cleaned, '+79002223344')

    def test_is_russia_phone_number(self):
        for raw_phone_number in self.raw_phone_numbers:
            phone_number = PhoneNumber(raw_phone_number.input_value)

            if raw_phone_number.type in {ptype.RU_E164, ptype.RU_LOCAL}:
                self.assertEqual(phone_number.is_russia, True)
            else:
                self.assertEqual(phone_number.is_russia, False)

    def test_concatenate_string_with_phone_number(self):
        phone_number = PhoneNumber('8 (234) 222-55-66')
        result = 'Phone number: ' + phone_number

        self.assertEqual(result, 'Phone number: +7 (234) 222-55-66')

        result = phone_number + ' phone'

        self.assertEqual(result, '+7 (234) 222-55-66 phone')

    def test_eq_phone_number(self):
        phone_number_1 = PhoneNumber('8 (234) 222-55-66')
        phone_number_2 = PhoneNumber('+7 (234) 222-55-66')

        self.assertEqual(phone_number_1, phone_number_2)
        self.assertEqual(phone_number_1, '+7 (234) 222-55-66')
        self.assertEqual(phone_number_1, '(234) 222 55 66')
        self.assertNotEqual(phone_number_1, '222-55-66')

    def test_bool_phone_number(self):
        valid_phone_number = PhoneNumber('8 (234) 222-55-66')
        invalid_phone_number = PhoneNumber('33')

        self.assertTrue(valid_phone_number)
        self.assertFalse(invalid_phone_number)

    def test_len_phone_number(self):
        valid_phone_number = PhoneNumber('8 (234) 222-55-66')
        invalid_phone_number = PhoneNumber('33')

        self.assertEqual(len(valid_phone_number), 12)
        self.assertFalse(len(invalid_phone_number), 0)
