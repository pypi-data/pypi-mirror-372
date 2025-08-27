from datetime import (
    date,
    datetime,
)
from itertools import (
    permutations,
)

from django.core.exceptions import (
    ValidationError,
)
from django.test import (
    SimpleTestCase,
    TestCase,
)

from tests.testapp.models import (
    DateIntervalModel_1_1,
    DateIntervalModel_1_2,
    DateIntervalModel_1_3,
    DateIntervalModel_2_1,
    DateIntervalModel_2_2,
    DateTimeIntervalModel_1_1,
    DateTimeIntervalModel_1_2,
    DateTimeIntervalModel_1_3,
    DateTimeIntervalModel_2_1,
    DateTimeIntervalModel_2_2,
    ExtraIntervalModel,
)

from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)


class DateIntervalMixinTestCase(TestCase):
    """Тесты для примеси DateIntervalMixin."""

    def test_interval_model_meta(self):
        """Тесты правильности работы метакласса DateIntervalMeta."""
        # pylint: disable=protected-access
        data = (
            (DateIntervalModel_1_1, 'date_from', 'date_to'),
            (DateIntervalModel_1_2, 'qwe', 'rty'),
            (DateIntervalModel_1_3, 'asd', 'fgh'),
        )
        for model, field_from, field_to in data:
            model._meta.get_field(field_from)
            model._meta.get_field(field_to)

    def _test_objects(self, model, from1, to1, from2, to2, params, invalid):
        try:
            object1 = model(date_from=from1, date_to=to1, **params)
            object1.full_clean()
            object1.save()

            object2 = model(date_from=from2, date_to=to2, **params)
            if invalid:
                self.assertRaises(ValidationError, object2.full_clean)
            else:
                object2.full_clean()
                object2.save()
        finally:
            if 'object1' in locals() and object1.pk is not None:
                object1.delete()
            if 'object2' in locals() and object2.pk is not None:
                object2.delete()

    def test_intersections(self):
        """Тесты правильности проверки пересечений интервалов."""
        dates = (None, date(2000, 1, 1), date(2000, 2, 1), date(2000, 3, 1), date(2000, 4, 1), None)
        models_params = (
            (DateIntervalModel_2_1, dict(field='qwe')),
            (DateIntervalModel_2_2, dict(field1='qwe', field2='asd', field3='zxc')),
        )

        for from1, to1, from2, to2 in permutations(dates, 4):
            _from1 = from1 or date.min
            _to1 = to1 or date.max
            _from2 = from2 or date.min
            _to2 = to2 or date.max
            if _from1 > _to1 or _from2 > _to2:
                continue

            invalid = (_from1 <= _from2 <= _to1) or (_from2 <= _from1 <= _to2)
            for model, params in models_params:
                self._test_objects(model, from1, to1, from2, to2, params, invalid=invalid)

    def test_date_in_intervals_filter(self):
        """Тестирование метода get_date_in_intervals_filter()."""
        model = DateIntervalModel_1_1

        # Данные для моделей
        models_data = (
            (1, date(2015, 1, 1), date(2015, 1, 31)),
            (2, date(2015, 2, 1), date(2015, 2, 28)),
            (3, date(2015, 3, 1), date(2015, 3, 31)),
            (4, date(2015, 4, 1), date(2015, 4, 30)),
        )

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                date_from=date_from,
                date_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # date, exclude, ids
            (date(2015, 1, 10), False, [1]),
            (date(2015, 2, 10), False, [2]),
            (date(2015, 3, 10), False, [3]),
            (date(2015, 4, 10), False, [4]),
            (date(2015, 1, 10), True, [2, 3, 4]),
            (date(2015, 2, 10), True, [1, 3, 4]),
            (date(2015, 3, 10), True, [1, 2, 4]),
            (date(2015, 4, 10), True, [1, 2, 3]),
            (date(2015, 5, 10), False, []),
            (date(2015, 5, 10), True, [1, 2, 3, 4]),
        )

        # Проверка с датой внутри интервала
        for day, exclude, test_ids in test_data:
            q = model.get_date_in_intervals_filter(day)
            if exclude:
                q = ~q
            result_ids = model.objects.filter(q).values_list('pk', flat=True)

            self.assertEqual(set(test_ids), set(result_ids))

        # Проверка на границах интервалов
        for pk, date_from, date_to in models_data:
            for include_bounds in (True, False):
                for day in (date_from, date_to):
                    q = model.get_date_in_intervals_filter(
                        day=day,
                        include_lower_bound=include_bounds,
                        include_upper_bound=include_bounds,
                    )
                    result_ids = model.objects.filter(q, pk=pk).values_list('pk', flat=True)
                    self.assertEqual(len(result_ids), 1 if include_bounds else 0)
                    self.assertEqual(pk in result_ids, include_bounds)

    def test_intersection_daterange_filter(self):
        """Тестирование метода get_intersection_daterange_filter()."""
        model = DateIntervalModel_1_1

        # Данные для моделей
        models_data = ((1, date(2020, 1, 1), date(2020, 1, 31)),)

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                date_from=date_from,
                date_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # date_begin, date_end, exclude, ids
            # 2 проверки вне диапазона
            # за пределами слева
            (date(2019, 12, 31), date(2019, 12, 31), True, [1]),
            # за пределами справа
            (date(2020, 2, 1), date(2020, 2, 2), True, [1]),
            # проверка вхождения слева
            (date(2019, 12, 31), date(2020, 1, 1), False, [1]),
            # проверка вхождения справа
            (date(2020, 1, 31), date(2020, 2, 1), False, [1]),
            # 2 случая полного перекрытия диапазонов a в b или b в a
            (date(2019, 12, 31), date(2020, 2, 1), False, [1]),
            (date(2020, 1, 2), date(2020, 1, 30), False, [1]),
        )

        for date_begin, date_end, exclude, test_ids in test_data:
            query_filter = model.get_intersection_daterange_filter(date_begin, date_end)
            result = model.objects.filter(query_filter).first()

            if not exclude:
                self.assertIn(result.pk, test_ids)
            else:
                self.assertIsNone(result)

    def test_intersection_daterange_filter_with_null_field(self):
        """Тестирование метода get_intersection_daterange_filter() с null."""
        model = DateIntervalModel_1_1

        # Данные для моделей
        models_data = (
            (1, None, date(2020, 1, 31)),
            (2, date(2020, 1, 1), None),
        )

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                date_from=date_from,
                date_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # date_begin, date_end, ids
            # 2 проверки вне диапазона
            # за пределами слева
            (date(2019, 12, 31), date(2019, 12, 31), [1]),
            # за пределами справа
            (date(2020, 2, 1), date(2020, 2, 2), [2]),
            # проверка вхождения слева
            (date(2019, 12, 31), date(2020, 1, 1), [1, 2]),
            # проверка вхождения справа
            (date(2020, 1, 31), date(2020, 2, 1), [1, 2]),
            # 2 случая полного перекрытия диапазонов a в b или b в a
            (date(2019, 12, 31), date(2020, 2, 1), [1, 2]),
            (date(2020, 1, 2), date(2020, 1, 30), [1, 2]),
        )

        for date_begin, date_end, test_ids in test_data:
            query_filter = model.get_intersection_daterange_filter(date_begin, date_end)
            result_1 = model.objects.filter(query_filter).first()
            self.assertIn(result_1.pk, test_ids)

            result_2 = model.objects.filter(query_filter).exclude(pk=result_1.pk).first()

            if result_2:
                self.assertIn(result_2.pk, test_ids)


class DateTimeIntervalMixinTestCase(TestCase):
    """Тесты для примеси DateTimeIntervalMixin."""

    def test_interval_model_meta(self):
        """Тесты правильности работы метакласса DateTimeIntervalMeta."""
        # pylint: disable=protected-access
        data = (
            (DateTimeIntervalModel_1_1, 'datetime_from', 'datetime_to'),
            (DateTimeIntervalModel_1_2, 'qwe', 'rty'),
            (DateTimeIntervalModel_1_3, 'asd', 'fgh'),
        )
        for model, field_from, field_to in data:
            model._meta.get_field(field_from)
            model._meta.get_field(field_to)

    def _test_objects(self, model, from1, to1, from2, to2, params, invalid):
        try:
            object1 = model(datetime_from=from1, datetime_to=to1, **params)
            object1.full_clean()
            object1.save()

            object2 = model(datetime_from=from2, datetime_to=to2, **params)
            if invalid:
                self.assertRaises(ValidationError, object2.full_clean)
            else:
                object2.full_clean()
                object2.save()
        finally:
            if 'object1' in locals() and object1.pk is not None:
                object1.delete()
            if 'object2' in locals() and object2.pk is not None:
                object2.delete()

    def test_intersections(self):
        """Тесты правильности проверки пересечений интервалов."""
        dates = (
            None,
            datetime(2000, 1, 1, 10, 9, 15),
            datetime(2000, 2, 1, 10, 9, 15),
            datetime(2000, 3, 1, 10, 9, 15),
            datetime(2000, 4, 1, 10, 9, 15),
            datetime(2000, 4, 1, 10, 9, 15),
            datetime(2000, 4, 1, 10, 10, 15),
            None,
        )
        models_params = (
            (DateTimeIntervalModel_2_1, dict(field='qwe')),
            (DateTimeIntervalModel_2_2, dict(field1='qwe', field2='asd', field3='zxc')),
        )

        for from1, to1, from2, to2 in permutations(dates, 4):
            _from1 = from1 or datetime.min
            _to1 = to1 or datetime.max
            _from2 = from2 or datetime.min
            _to2 = to2 or datetime.max
            if _from1 > _to1 or _from2 > _to2:
                continue

            invalid = (_from1 <= _from2 <= _to1) or (_from2 <= _from1 <= _to2)
            for model, params in models_params:
                self._test_objects(model, from1, to1, from2, to2, params, invalid=invalid)

    def test_date_in_intervals_filter(self):
        """Тестирование метода get_date_in_intervals_filter()."""
        model = DateTimeIntervalModel_1_1

        # Данные для моделей
        models_data = (
            (1, datetime(2015, 1, 1), datetime(2015, 1, 31)),
            (2, datetime(2015, 2, 1), datetime(2015, 2, 28)),
            (3, datetime(2015, 3, 1), datetime(2015, 3, 31)),
            (4, datetime(2015, 4, 1), datetime(2015, 4, 30)),
            (5, datetime(2015, 4, 1, 3, 15), datetime(2015, 4, 1, 3, 25)),
            (6, datetime(2015, 4, 1, 4, 3), datetime(2015, 4, 1, 4, 15)),
        )

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                datetime_from=date_from,
                datetime_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # datetime, exclude, ids
            (datetime(2015, 1, 10), False, [1]),
            (datetime(2015, 2, 10), False, [2]),
            (datetime(2015, 3, 10), False, [3]),
            (datetime(2015, 4, 10), False, [4]),
            (datetime(2015, 1, 10), True, [2, 3, 4, 5, 6]),
            (datetime(2015, 2, 10), True, [1, 3, 4, 5, 6]),
            (datetime(2015, 3, 10), True, [1, 2, 4, 5, 6]),
            (datetime(2015, 4, 10), True, [1, 2, 3, 5, 6]),
            (datetime(2015, 5, 10), False, []),
            (datetime(2015, 5, 10), True, [1, 2, 3, 4, 5, 6]),
            (datetime(2015, 4, 1, 3, 20), False, [4, 5]),
            (datetime(2015, 4, 1, 4, 10), False, [4, 6]),
        )

        # Проверка с датой внутри интервала
        for dt, exclude, test_ids in test_data:
            q = model.get_date_in_intervals_filter(dt)
            if exclude:
                q = ~q
            result_ids = model.objects.filter(q).values_list('pk', flat=True)

            self.assertEqual(set(test_ids), set(result_ids))

        # Проверка на границах интервалов
        for pk, datetime_from, datetime_to in models_data:
            for include_bounds in (True, False):
                for day in (datetime_from, datetime_to):
                    q = model.get_date_in_intervals_filter(
                        day=day,
                        include_lower_bound=include_bounds,
                        include_upper_bound=include_bounds,
                    )
                    result_ids = model.objects.filter(q, pk=pk).values_list('pk', flat=True)
                    self.assertEqual(len(result_ids), 1 if include_bounds else 0)
                    self.assertEqual(pk in result_ids, include_bounds)

    def test_intersection_daterange_filter(self):
        """Тестирование метода get_intersection_daterange_filter()."""
        model = DateTimeIntervalModel_1_1

        # Данные для моделей
        models_data = ((1, datetime(2020, 1, 1, 15, 48, 21), datetime(2020, 1, 31, 16)),)

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                datetime_from=date_from,
                datetime_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # date_begin,
            # date_end,
            # exclude,
            # ids
            # 2 проверки вне диапазона
            # за пределами слева
            (datetime(2020, 1, 1, 14), datetime(2020, 1, 1, 15), True, [1]),
            # за пределами справа
            (datetime(2020, 1, 31, 16, 1), datetime(2020, 1, 31, 17), True, [1]),
            # проверка вхождения слева
            (datetime(2020, 1, 1, 15), datetime(2020, 1, 1, 15, 48, 21), False, [1]),
            # проверка вхождения справа
            (datetime(2020, 1, 31, 16), datetime(2020, 1, 31, 17), False, [1]),
            # 2 случая полного перекрытия диапазонов a в b или b в a
            (datetime(2020, 1, 1, 15), datetime(2020, 1, 31, 17), False, [1]),
            (datetime(2020, 1, 1, 15, 50), datetime(2020, 1, 31, 15, 59), False, [1]),
        )

        for date_begin, date_end, exclude, test_ids in test_data:
            query_filter = model.get_intersection_daterange_filter(date_begin, date_end)
            result = model.objects.filter(query_filter).first()

            if not exclude:
                self.assertIn(result.pk, test_ids)
            else:
                self.assertIsNone(result)

    def test_intersection_daterange_filter_with_null_field(self):
        """Тестирование метода get_intersection_daterange_filter() с null."""
        model = DateTimeIntervalModel_1_1

        # Данные для моделей
        models_data = (
            (1, None, datetime(2020, 1, 31, 16)),
            (2, datetime(2020, 1, 1, 15, 48, 21), None),
        )

        # Создание моделей с тестовыми данными
        for pk, date_from, date_to in models_data:
            record = model(
                pk=pk,
                datetime_from=date_from,
                datetime_to=date_to,
            )
            record.full_clean()
            record.save()

        test_data = (
            # date_begin,
            # date_end,
            # ids
            # 2 проверки вне диапазона
            # за пределами слева
            (datetime(2020, 1, 1, 14), datetime(2020, 1, 1, 15), [1]),
            # за пределами справа
            (datetime(2020, 1, 31, 16, 1), datetime(2020, 1, 31, 17), [2]),
            # проверка вхождения слева
            (datetime(2020, 1, 1, 15), datetime(2020, 1, 1, 15, 48, 21), [1, 2]),
            # проверка вхождения справа
            (datetime(2020, 1, 31, 16), datetime(2020, 1, 31, 17), [1, 2]),
            # 2 случая полного перекрытия диапазонов a в b или b в a
            (datetime(2020, 1, 1, 15), datetime(2020, 1, 31, 17), [1, 2]),
            (datetime(2020, 1, 1, 15, 50), datetime(2020, 1, 31, 15, 59), [1, 2]),
        )

        for date_begin, date_end, test_ids in test_data:
            query_filter = model.get_intersection_daterange_filter(date_begin, date_end)
            result_1 = model.objects.filter(query_filter).first()
            self.assertIn(result_1.pk, test_ids)

            result_2 = model.objects.filter(query_filter).exclude(pk=result_1.pk).first()

            if result_2:
                self.assertIn(result_2.pk, test_ids)


class ExtraIntervalTestCase(SimpleTestCase):
    """Проверка корректности создания базовых классов."""

    def test(self):
        self.assertEqual(ExtraIntervalModel.interval_field_names, ('start_date', 'end_date'))
        self.assertEqual(ExtraIntervalModel.no_intersections_for, ('name',))

        with self.assertRaises(FieldDoesNotExist):
            ExtraIntervalModel._meta.get_field('date_from')
            ExtraIntervalModel._meta.get_field('date_to')

        start_date_field, end_date_field, name_field = map(
            ExtraIntervalModel._meta.get_field, ('start_date', 'end_date', 'name')
        )

        self.assertFalse(start_date_field.null)
        self.assertFalse(start_date_field.blank)
        self.assertTrue(end_date_field.null)
        self.assertTrue(end_date_field.blank)

        self.assertEqual(start_date_field.verbose_name, 'Дата начала')
        self.assertEqual(end_date_field.verbose_name, 'Дата окончания')

        self.assertTrue(start_date_field.default, date.today)
        with self.assertRaises(AssertionError):
            self.assertIs(end_date_field.default, None)

        self.assertEqual(name_field.verbose_name, 'Наименование')
