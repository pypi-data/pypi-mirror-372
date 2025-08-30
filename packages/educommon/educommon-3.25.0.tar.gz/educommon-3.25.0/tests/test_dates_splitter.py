from datetime import (
    datetime,
)
from unittest import (
    TestCase,
)

from educommon.utils.date import (
    DatesSplitter,
)


class TestSplitter(TestCase):
    """Тесты для сплиттера."""

    def _split_day_ws_mode_1(self):
        """
        Тест разбития по дням по одному.

        27.12.2022 08:23:02 - 01.01.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 28, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 28, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 29, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 29, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 30, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 1, 1, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_day_ws_mode_2(self):
        """
        Тест разбития по дням по одному.

        27.12.2022 08:23:02 - 01.01.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2022, 12, 27, 22, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_day_ws_mode_3(self):
        """
        Тест разбития по дням по 4.

        27.12.2022 08:23:02 - 11.01.2023 22:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 3, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 4, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 7, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 8, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 11, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 1, 11, 22, 23, 2)
        self.splitter.split_by_quantity = 4
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_day_ws_mode(self):
        """Тест разбития по дням."""
        self.splitter = DatesSplitter(
            split_by='day',
            split_mode=DatesSplitter.WS_MODE,
        )
        self._split_day_ws_mode_1()
        self._split_day_ws_mode_2()
        self._split_day_ws_mode_3()

    def test_split_day_ww_mode(self):
        """Тест разбития по дням."""
        self.splitter = DatesSplitter(
            split_by='day',
            split_mode=DatesSplitter.WW_MODE,
        )
        self._split_day_ws_mode_1()
        self._split_day_ws_mode_2()
        self._split_day_ws_mode_3()

    def _split_week_ws_mode_1(self):
        """
        Тест разбития по неделям.

        29.08.2023 08:23:02 - 04.09.2023 09:23:02
        """
        real_result = [
            (datetime(2023, 8, 29, 0, 0, 0), datetime(2023, 9, 3, 23, 59, 59)),
            (datetime(2023, 9, 4, 0, 0, 0), datetime(2023, 9, 4, 23, 59, 59)),
        ]
        period_started_at = datetime(2023, 8, 29, 8, 23, 2)
        period_ended_at = datetime(2023, 9, 4, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ws_mode_2(self):
        """
        Тест разбития по неделям.

        29.08.2023 08:23:02 - 31.08.2023 09:23:02
        """
        real_result = [
            (datetime(2023, 8, 29, 0, 0, 0), datetime(2023, 8, 31, 23, 59, 59)),
        ]
        period_started_at = datetime(2023, 8, 29, 8, 23, 2)
        period_ended_at = datetime(2023, 8, 31, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ws_mode_3(self):
        """
        Тест разбития по неделям.

        29.08.2023 08:23:02 - 29.08.2023 09:23:02
        """
        real_result = [
            (datetime(2023, 8, 29, 0, 0, 0), datetime(2023, 8, 29, 23, 59, 59)),
        ]
        period_started_at = datetime(2023, 8, 29, 8, 23, 2)
        period_ended_at = datetime(2023, 8, 29, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ws_mode_4(self):
        """
        Тест разбития по неделям.

        06.08.2023 08:23:02 - 02.09.2023 09:23:02
        """
        real_result = [
            (
                datetime(2023, 8, 6, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 7, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 13, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 20, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 21, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 27, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 28, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 9, 2, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2023, 8, 6, 8, 23, 2)
        period_ended_at = datetime(2023, 9, 2, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ws_mode_5(self):
        """
        Тест разбития по неделям.

        27.12.2022 08:23:02 - 08.01.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 2, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 8, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 1, 8, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ws_mode_6(self):
        """
        Тест разбития по две недели.

        27.12.2022 08:23:02 - 08.02.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 8, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 9, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 22, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 23, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 5, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 2, 6, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 8, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 2, 8, 9, 23, 2)
        self.splitter.split_by_quantity = 2
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_week_ws_mode(self):
        """Тест разбития по неделям в режиме wed-to-sun."""
        self.splitter = DatesSplitter(
            split_by='week',
            split_mode=DatesSplitter.WS_MODE,
        )
        self._split_week_ws_mode_1()
        self._split_week_ws_mode_2()
        self._split_week_ws_mode_3()
        self._split_week_ws_mode_4()
        self._split_week_ws_mode_5()
        self._split_week_ws_mode_6()

    def _split_week_ww_mode_1(self):
        """
        Тест разбития по неделям.

        27.12.2022 08:23:02 - 08.01.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 2, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 3, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 8, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 1, 8, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ww_mode_2(self):
        """
        Тест разбития по неделям.

        06.08.2023 08:23:02 - 02.09.2023 09:23:02
        """
        real_result = [
            (
                datetime(2023, 8, 6, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 12, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 13, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 19, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 20, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 8, 26, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 8, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 9, 2, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2023, 8, 6, 8, 23, 2)
        period_ended_at = datetime(2023, 9, 2, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ww_mode_3(self):
        """
        Тест разбития по три недели.

        27.12.2022 08:23:02 - 08.02.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 27, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 16, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 17, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 2, 7, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 8, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 27, 8, 23, 2)
        period_ended_at = datetime(2023, 2, 8, 9, 23, 2)
        self.splitter.split_by_quantity = 3
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_week_ww_mode_4(self):
        """
        Тест разбития по три недели.

        26.12.2022 08:23:02 - 05.02.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 12, 26, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 16, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 5, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 12, 26, 8, 23, 2)
        period_ended_at = datetime(2023, 2, 5, 9, 23, 2)
        self.splitter.split_by_quantity = 3
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_week_ww_mode(self):
        """Тест разбития по неделям в режиме wed-to-wed."""
        self.splitter = DatesSplitter(
            split_by='week',
            split_mode=DatesSplitter.WW_MODE,
        )
        self._split_week_ww_mode_1()
        self._split_week_ww_mode_2()
        self._split_week_ww_mode_3()
        self._split_week_ww_mode_4()

    def _split_month_ws_mode_1(self):
        """
        Тест разбития по месяцам.

        11.11.2022 08:23:02 - 15.05.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 11, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 2, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 28, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 3, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 3, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 4, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 4, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 5, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2023, 5, 15, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ws_mode_2(self):
        """
        Тест разбития по месяцам.

        11.11.2022 08:23:02 - 30.11.2022 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 11, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2022, 11, 30, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ws_mode_3(self):
        """
        Тест разбития по месяцам.

        11.11.2022 08:23:02 - 01.12.2022 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 11, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 12, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 1, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2022, 12, 1, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ws_mode_4(self):
        """
        Тест разбития по два месяца.

        11.11.2022 08:23:02 - 15.05.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 2, 28, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 3, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 4, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 5, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2023, 5, 15, 9, 23, 2)
        self.splitter.split_by_quantity = 2
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ws_mode_5(self):
        """
        Тест разбития по 6 месяцев.

        11.11.2022 08:23:02 - 15.05.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 4, 30, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 5, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2023, 5, 15, 9, 23, 2)
        self.splitter.split_by_quantity = 6
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_month_ws_mode(self):
        """Тест разбития по месяцам в режиме wednesday-to-sunday."""
        self.splitter = DatesSplitter(
            split_by='month',
            split_mode=DatesSplitter.WS_MODE,
        )
        self._split_month_ws_mode_1()
        self._split_month_ws_mode_2()
        self._split_month_ws_mode_3()
        self._split_month_ws_mode_4()
        self._split_month_ws_mode_5()

    def _split_month_ww_mode_1(self):
        """
        Тест разбития по месяцам в режиме wednesday-to-wednesday.

        11.11.2022 08:23:02 - 01.12.2022 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 1, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2022, 12, 1, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ww_mode_2(self):
        """
        Тест разбития по 2 месяца.

        11.11.2022 08:23:02 - 15.05.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 1, 10, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 3, 10, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 3, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 10, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 5, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2023, 5, 15, 9, 23, 2)
        self.splitter.split_by_quantity = 2
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_month_ww_mode_3(self):
        """
        Тест разбития по 6 месяцев.

        11.11.2022 08:23:02 - 15.05.2023 09:23:02
        """
        real_result = [
            (
                datetime(2022, 11, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 10, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 5, 11, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 5, 15, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2022, 11, 11, 8, 23, 2)
        period_ended_at = datetime(2023, 5, 15, 9, 23, 2)
        self.splitter.split_by_quantity = 6
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_month_ww_mode(self):
        """Тест разбития по месяцам в режиме wednesday-to-wednesday."""
        self.splitter = DatesSplitter(
            split_by='month',
            split_mode=DatesSplitter.WW_MODE,
        )
        self._split_month_ww_mode_1()
        self._split_month_ww_mode_2()
        self._split_month_ww_mode_3()

    def _split_year_ws_mode_1(self):
        """
        Тест разбития по годам.

        14.01.2016 08:23:02 - 06.06.2023 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2016, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2017, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2017, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2018, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2018, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2019, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2019, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2020, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2020, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2021, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2021, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2023, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 6, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 14, 8, 23, 2)
        period_ended_at = datetime(2023, 6, 6, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_year_ws_mode_2(self):
        """
        Тест разбития по годам.

        14.01.2016 08:23:02 - 06.12.2016 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2016, 12, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 14, 8, 23, 2)
        period_ended_at = datetime(2016, 12, 6, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_year_ws_mode_3(self):
        """
        Тест разбития по годам.

        01.01.2016 08:23:02 - 31.12.2017 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2016, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2017, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2017, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 1, 8, 23, 2)
        period_ended_at = datetime(2017, 12, 31, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_year_ws_mode_4(self):
        """
        Тест разбития по 2 года.

        14.01.2016 08:23:02 - 06.06.2023 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2017, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2018, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2019, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2020, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2021, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 6, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 14, 8, 23, 2)
        period_ended_at = datetime(2023, 6, 6, 9, 23, 2)
        self.splitter.split_by_quantity = 2
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_year_ws_mode(self):
        """Тест разбития по годам в режиме wed-to-sun."""
        self.splitter = DatesSplitter(
            split_by='year',
            split_mode=DatesSplitter.WS_MODE,
        )
        self._split_year_ws_mode_1()
        self._split_year_ws_mode_2()
        self._split_year_ws_mode_3()
        self._split_year_ws_mode_4()

    def _split_year_ww_mode_1(self):
        """
        Тест разбития по годам.

        01.01.2016 08:23:02 - 31.12.2017 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2016, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2017, 1, 1, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2017, 12, 31, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 1, 8, 23, 2)
        period_ended_at = datetime(2017, 12, 31, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_year_ww_mode_2(self):
        """
        Тест разбития по годам.

        14.01.2016 08:23:02 - 06.12.2016 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2016, 12, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 14, 8, 23, 2)
        period_ended_at = datetime(2016, 12, 6, 9, 23, 2)
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def _split_year_ww_mode_3(self):
        """
        Тест разбития по 2 года.

        14.01.2016 08:23:02 - 06.06.2023 09:23:02
        """
        real_result = [
            (
                datetime(2016, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2018, 1, 13, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2018, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2020, 1, 13, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2020, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2022, 1, 13, **DatesSplitter.DEFAULT_TIME_END),
            ),
            (
                datetime(2022, 1, 14, **DatesSplitter.DEFAULT_TIME_START),
                datetime(2023, 6, 6, **DatesSplitter.DEFAULT_TIME_END),
            ),
        ]
        period_started_at = datetime(2016, 1, 14, 8, 23, 2)
        period_ended_at = datetime(2023, 6, 6, 9, 23, 2)
        self.splitter.split_by_quantity = 2
        spliter_result = self.splitter.split(period_started_at, period_ended_at)
        self.assertEqual(spliter_result, real_result)

    def test_split_year_ww_mode(self):
        """Тест разбития по годам в режиме wed-to-wed."""
        self.splitter = DatesSplitter(
            split_by='year',
            split_mode=DatesSplitter.WW_MODE,
        )
        self._split_year_ww_mode_1()
        self._split_year_ww_mode_2()
        self._split_year_ww_mode_3()
