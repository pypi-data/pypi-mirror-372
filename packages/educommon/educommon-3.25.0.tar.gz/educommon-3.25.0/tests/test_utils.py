"""Unit-тесты для вспомогательных средств из educommon.utils."""

import sys
from datetime import (
    date,
    datetime,
)
from itertools import (
    permutations,
)
from unittest import (
    TestCase,
)

from educommon.utils import (
    is_ranges_intersected,
)
from educommon.utils.misc import (
    get_nested_attr,
)


class UtilsTestCase(TestCase):
    """Набор тестов для функций из educommon.utils."""

    def test_is_ranges_intersected(self):
        int_values = (
            -sys.maxsize - 1,  # minint
            sys.maxsize,
            (
                None,
                1,
                2,
                3,
                4,
                None,
            ),
        )
        date_values = (
            date.min,
            date.max,
            (
                None,
                date(2000, 1, 1),
                date(2000, 2, 1),
                date(2000, 3, 1),
                date(2000, 4, 1),
                None,
            ),
        )

        for min_value, max_value, values in (int_values, date_values):
            for from1, to1, from2, to2 in permutations(values, 4):
                # Проверка на пересечение вручную
                _from1 = from1 or min_value
                _to1 = to1 or max_value
                _from2 = from2 or min_value
                _to2 = to2 or max_value
                if _from1 > _to1 or _from2 > _to2:
                    continue
                is_intersected = (_from1 <= _from2 <= _to1) or (_from2 <= _from1 <= _to2)

                # Сравнение результата ручной проверки с результатом функции
                range1, range2 = (from1, to1), (from2, to2)
                function_result = is_ranges_intersected(range1, range2)
                self.assertEqual(function_result, is_intersected)

    def test_get_nested_attr(self):
        """Тестирование функции get_nested_attr."""
        obj = datetime(2015, 1, 1, 0, 0, 0)

        self.assertEqual(get_nested_attr(obj, 'date().year'), 2015)
        self.assertIs(get_nested_attr(obj, 'date().year.__class__'), int)
