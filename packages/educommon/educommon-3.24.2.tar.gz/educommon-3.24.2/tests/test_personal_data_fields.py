import datetime

from django.core.validators import (
    ValidationError,
)
from django.test.utils import (
    TestCase,
)

from tests.testapp import (
    models as test_models,
)

from objectpack import (
    IMaskRegexField,
)


class TestPersonalDataFields(TestCase):
    def test_names(self):
        model = test_models.FullNamesModel

        # Фамилия, Имя, Отчество
        valid_names = (
            ('Майор', 'Майор', 'Майор'),
            ('Майор', 'Майор', 'Майор Майор'),
            ('Major', 'Major', 'Major'),
            ('Major', 'Major', None),
            ('Майор', 'Майор-Major', None),
            (
                'Майор-Major',
                'Майор-Major',
                'Майор-Major',
            ),
            (
                'Майор Major',
                'Майор Major',
                'Майор Major',
            ),
        )
        invalid_names = (
            ('Major!', 'Major!', None),
            ('Major"', 'Major"', None),
            ('Major№', 'Major№', None),
            ('Major;', 'Major;', None),
            ('Major%', 'Major%', None),
            ('Major?', 'Major?', None),
            ('Major(', 'Major(', None),
            ('Major)', 'Major)', None),
            ('Major*', 'Major*', None),
            ('Major_', 'Major_', None),
            ('Major+', 'Major+', None),
            ('Major!', 'Major!', None),
            ('Major  Major', 'Major  Major', None),
            ('Major--Major', 'Major--Major', None),
        )

        self._test_valid_invalid(model, valid_names, invalid_names)
        self._test_linear_regex(model, valid_names)

    def test_snils(self):
        model = test_models.SNILSModel

        # СНИЛС
        valid_snilses = (('123-123-456 01',),)
        invalid_snilses = (
            ('12312345601',),  # нет разделителей
            ('123-123-456 02',),  # неверная контрольная сумма
            ('d23-123-456 02',),  # неверный символ
            ('123-d23-456 02',),  # неверный символ
            ('123-123-d56 02',),  # неверный символ
            ('123-123-456 d2',),  # неверный символ
        )
        self._test_valid_invalid(model, valid_snilses, invalid_snilses)
        self._test_linear_regex(model, valid_snilses)

    def test_birth_date(self):
        model = test_models.BirthDatesModel

        # огр.снизу, огр.сверху, дата рождения
        valid_dates = (
            (
                datetime.date(2015, 1, 1),
                datetime.date(2017, 1, 1),
                datetime.date(2016, 1, 1),
            ),
        )
        invalid_dates = (
            (
                datetime.date(2015, 1, 1),
                datetime.date(2017, 1, 1),
                datetime.date(1916, 12, 31),
            ),
            (
                datetime.date(2015, 1, 1),
                datetime.date(2017, 1, 1),
                datetime.date.today(),
            ),
            (
                datetime.date(2015, 1, 1),
                datetime.date(2017, 1, 1),
                datetime.date(2300, 1, 1),
            ),
        )

        self._test_valid_invalid(model, valid_dates, invalid_dates)

    def test_documents_with_series_and_number(self):
        model = test_models.DocumentsSeriesNumberModel

        # Серия документа, Номер документа, Серия паспорта, Номер паспорта
        valid_documents = (('123abc', '456def', '0110', '102030'),)
        invalid_documents = (
            ('a' * 11, '456def', '0110', '102030'),
            ('a', '4' * 21, '0110', '102030'),
            ('a', '456def', '01101', '102030'),
            ('a', '456def', '0', '102030'),
            ('a', '456def', '0110', '1020301'),
            ('a', '456def', '0110', '1'),
            ('a', '456def', 'd110', '102030'),
            ('a', '456def', '0110', 'd02030'),
        )

        self._test_valid_invalid(model, valid_documents, invalid_documents)
        self._test_linear_regex(model, valid_documents)

    def test_ogranization_documents(self):
        model = test_models.OrganizationDocumentsModel

        # ИНН, КПП, ОГРН
        valid_values = (('1655251590', '165501001', '1121690063923'),)
        invalid_values = (
            ('500100732200', '16550100d', '11216900639a'),
            ('500100732200', '16550100', '112169006393'),
        )
        self._test_valid_invalid(model, valid_values, invalid_values)
        self._test_linear_regex(model, valid_values)

    def _test_valid_invalid(self, model, valid_values, invalid_values):
        """Проверяет, что определенные значения могут быть добавлены в модель,
        а определенные - напротив, вызовут ValidationError
        :param model: модель, в которую добавляются значения
        :param valid_values: значения, которые должны проходить все проверки
        :type valid_values: Tuple[Tuple[Any]]
        :param invalid_values: значения, которые должны давать ValidationError
        :type invalid_values: Tuple[Tuple[Any]]
        :return:
        """
        for id_, values in enumerate(valid_values, 1):
            record = model(id_, *values)
            record.full_clean()
            record.save()

        for id_, values in enumerate(invalid_values, len(valid_values) + 1):
            with self.assertRaises(ValidationError):
                record = model(id_, *values)
                record.full_clean()
                record.save()

    def _test_linear_regex(self, model, valid_values):
        """Тестирует, что валидное значение будет введено от начала до конца
        без ошибок (симулируя ввод пользователя)
        :return:
        """
        # [1:] - чтобы исключить id
        fields_and_values = zip(model._meta.fields[1:], *valid_values)

        for field, *values in (f_and_v for f_and_v in fields_and_values if isinstance(f_and_v[0], IMaskRegexField)):
            for value in (v for v in values if v is not None):
                for entered_value in self._simulate_input(value):
                    self.assertRegex(entered_value, field.mask_re)

    @staticmethod
    def _simulate_input(value):
        """Симулирует линейный ввод значения в текстовое поле
        :param value: значение, которое в итоге должно быть введено в поле
        :type value: str
        :return: генератор, отдающий посимвольный ввод значения
        """
        for e in range(len(value)):
            yield value[:e]
