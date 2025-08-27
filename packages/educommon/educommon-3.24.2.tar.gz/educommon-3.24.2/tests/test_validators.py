"""Unit-тесты для валидаторов простых полей модели Django."""

from unittest import (
    TestCase,
)

from django.core.exceptions import (
    ValidationError,
)

from educommon.django.db.validators.simple import (
    doc_type_validator,
    inn10_validator,
    inn12_validator,
    inn_validator,
    is_doc_type_valid,
    is_inn10_valid,
    is_inn12_valid,
    is_inn_valid,
    is_snils_valid,
    snils_validator,
    house_validator,
    is_house_number_valid,
)


class SnilsValidatorTestCase(TestCase):
    """Тесты для валидатора СНИЛС."""

    def test_valid_snils(self):
        """Проверка правильности обработки корректных СНИЛС."""
        valid_snils_list = (
            '000-000-111 00',  # < 001-001-998
            '111-223-555 88',  # sum < 100
            '211-223-655 00',  # sum == 100
            '211-223-656 00',  # sum == 101
            '231-223-655 15',  # sum > 101, mod < 100
            '871-223-654 00',  # sum > 101, mod == 100
        )

        for snils in valid_snils_list:
            snils_validator(snils)
            self.assertTrue(is_snils_valid(snils), snils)

    def test_invalid_snils(self):
        """Проверка правильности обработки некорректных СНИЛС."""
        valid_snils_list = (
            '00000011100',
            'daskjbn',
            '111-223-555 81',
            '211-223-655 01',
            '211-223-656 01',
            '231-223-655 11',
            '871-223-654 01',
        )

        for snils in valid_snils_list:
            self.assertRaises(ValidationError, snils_validator, snils)
            self.assertFalse(is_snils_valid(snils), snils)


class InnValidatorTestCase(TestCase):
    """Тесты для валидаторов ИНН."""

    def test_valid_inn(self):
        """Проверка правильности обработки корректных ИНН."""
        valid_inn_list = (
            '1655148257',  # БАРС Груп
            '7707083893',  # Сбербанк
            '7830002293',  # ИНН ЮЛ из Википедии
            '500100732259',  # ИНН ФЛ из Википедии
        )

        for inn in valid_inn_list:
            inn_validator(inn)
            self.assertTrue(is_inn_valid(inn))
            if len(inn) == 10:
                inn10_validator(inn)
                self.assertTrue(is_inn10_valid(inn))
            else:
                inn12_validator(inn)
                self.assertTrue(is_inn12_valid(inn))

    def test_invalid_snils(self):
        """Проверка правильности обработки некорректных ИНН."""
        invalid_inn_list = (
            '1655148256',
            '7707083892',
            '7830002292',
            '500100732258',
        )

        for inn in invalid_inn_list:
            self.assertRaises(ValidationError, inn_validator, inn)
            self.assertFalse(is_inn_valid(inn))
            if len(inn) == 10:
                self.assertRaises(ValidationError, inn10_validator, inn)
                self.assertFalse(is_inn10_valid(inn))
            else:
                self.assertRaises(ValidationError, inn_validator, inn)
                self.assertFalse(is_inn12_valid(inn))


class DocumentTypeValidatorTestCase(TestCase):
    """Тесты для валидатора тип документа."""

    def test_valid_snils(self):
        """Проверка правильности обработки корректных типов документа."""
        valid_doc_type_list = (
            'Свидетельство о рождении',
            'Паспорт гражданина РФ',
            'Другой документ, удостоверяющий личность',
            'Временное удостоверение личности гражданина РФ',
            'Паспорт иностранного гражданина',
            'Загранпаспорт гражданина РФ',
            'Военный билет',
            'Дипломатический паспорт гражданина Российской Федерации',
            'Паспорт гражданина СССР',
            'Паспорт Минморфлота',
            'Паспорт моряка',
            'Разрешение на временное проживание в Российской Федерации',
            'Свидетельство о рассмотрении ходатайства о признании беженцем на территории Российской Федерации',
            'Свидетельство о рождении, выданное уполномоченным органом иностранного государства',
            'Справка об освобождении из места лишения свободы',
            'Удостоверение личности лица, признанного беженцем',
            'Удостоверение личности офицера',
            'Удостоверение личности военнослужащего РФ',
            'Временное удостоверение, выданное взамен военного билета',
            'Удостоверение личности лица без гражданства в РФ',
            'Удостоверение личности отдельных категорий лиц, находящихся '
            'на территории РФ, подавших заявление о признании гражданами '
            'РФ или о приеме в гражданство РФ',
            'Удостоверение личности лица, ходатайствующего о признании беженцем на территории РФ',
            'Удостоверение личности лица, получившего временное убежище на территории РФ',
            'Вид на жительство в Российской Федерации',
            'Свидетельство о предоставлении временного убежища на территории Российской Федерации',
            'а',
            'абв',  # одно слово
            'абв абв',  # один пробел
            'абв, абв',  # запятая
            'абв абв абв',  # три слова
            'абв, абв, абв',  # три слова через запятую
            'АБВ',
            'АБВ АБВ',
            'АБВ, АБВ',
            'АБВ АБВ АБВ',
            'АБВ, АБВ, АБВ',
        )

        for doc_type in valid_doc_type_list:
            doc_type_validator(doc_type)
            self.assertTrue(is_doc_type_valid(doc_type), doc_type)

    def test_invalid_doc_type(self):
        """Проверка правильности обработки некорректных типов документа."""
        invalid_doc_type_list = (
            '00000011100',  # цифры
            'daskjbn',  # латиница нижний регистр
            'DASKJBN',  # латиница верхний регистр
            '!*%',  # недопустимые символы
            'абв  абв',  # два пробела
            ' абв абв',  # пробел в начале
            'абв абв абв ',  # пробел в конце
            'абв , абв',  # пробел до запятой
        )

        for doc_type in invalid_doc_type_list:
            self.assertRaises(ValidationError, doc_type_validator, doc_type)
            self.assertFalse(is_doc_type_valid(doc_type), doc_type)


class HouseValidatorTestCase(TestCase):
    """Тесты для валидатора номера дома."""

    def test_valid_house_number(self):
        """Проверка правильности обработки корректных номеров дома."""
        valid_house_numbers = (
            '123',
            '123а',
            'уч. 123а',
            'з/у 123а',
            'абв абв абв',
        )

        for house_number in valid_house_numbers:
            self.assertTrue(is_house_number_valid(house_number), house_number)

    def test_invalid_house_number(self):
        """Проверка правильности обработки некорректных номеров дома."""
        invalid_house_numbers = (
            '1234567890123',  # строка из 13 символов
            'daskjbn',  # латиница
            '!*%',  # недопустимые символы
            'абв  абв',  # два пробела
            ' абв абв',  # пробел в начале
            'абв абв абв ',  # пробел в конце
        )

        for house_number in invalid_house_numbers:
            self.assertRaises(ValidationError, house_validator, house_number)
            self.assertFalse(is_house_number_valid(house_number), house_number)
