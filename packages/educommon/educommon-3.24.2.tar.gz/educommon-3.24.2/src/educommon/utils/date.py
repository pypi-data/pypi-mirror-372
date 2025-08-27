"""Вспомогательные средства для работы с датами."""

import datetime
from collections import (
    namedtuple,
)
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from dateutil import (
    rrule,
)
from dateutil.relativedelta import (
    relativedelta,
)
from django.conf import (
    settings,
)


# явно задаются имена дней, чтобы не возиться с настройками локали в питоне
MON_IDX = 0
TUE_IDX = 1
WED_IDX = 2
THU_IDX = 3
FRI_IDX = 4
SAT_IDX = 5
SUN_IDX = 6

WEEKDAYS = (
    (MON_IDX, 'Понедельник'),
    (TUE_IDX, 'Вторник'),
    (WED_IDX, 'Среда'),
    (THU_IDX, 'Четверг'),
    (FRI_IDX, 'Пятница'),
    (SAT_IDX, 'Суббота'),
    (SUN_IDX, 'Воскресенье'),
)
WEEKDAYS_DICT = dict(WEEKDAYS)


def date_range_to_str(date_from, date_to, can_be_one_day_long=False):
    """
    Возвращает строку формата "с дд.мм.гггг [по дд.мм.гггг]",
    или дд.мм.гггг, если даты совпадают.

    Если указана только одна из дат то будет только
    "с ..." или "по ...", но если can_be_one_day_long=True,
    результат будет "дд.мм.гггг", для той даты, что указана.

    (<2001.01.01>, <2001.01.01>)         -> "01.01.2001"
    (<2001.01.01>, <2002.02.02>)         -> "с 01.01.2001 по 02.02.2002"
    (<2001.01.01>, None        )         -> "с 01.01.2001"
    (None,         <2002.02.02>)         -> "по 02.02.2002"
    (<2001.01.01>, None,       , True)   -> "01.01.2001"
    (None,         <2002.02.02>, True)   -> "02.02.2002"
    """

    def fmt(date):
        return date.strftime('%d.%m.%Y') if date else ''

    def validate_year(date):
        return (date if 1900 < date.year < 2100 else None) if date else None

    result = ''
    date_from = validate_year(date_from)
    date_to = validate_year(date_to)
    if date_from and date_to:
        assert date_from <= date_to
        if date_from == date_to:
            result = fmt(date_from)
        else:
            result = f'с {fmt(date_from)} по {fmt(date_to)}'
    else:
        if can_be_one_day_long:
            result = fmt(date_from or date_to or None)
        elif date_from:
            result = f'с {fmt(date_from)}'
        elif date_to:
            result = f'по {fmt(date_to)}'
    return result


def iter_days_between(date_from, date_to, odd_weeks_only=False):
    """
    Генератор дат в промежутке между указанными (включая границы).

    :param datetime.date: date_from - дата с
    :param datetime.date: date_to - дата по
    :param boolean: odd_weeks_only - только четные недели отн-но начала года

    :rtype: generator
    """
    if date_from > date_to:
        raise ValueError('date_from must be lower or equal date_to!')

    for dt in rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to):
        if odd_weeks_only and dt.isocalendar()[1] % 2 != 0:
            # если требуются четные недели относительно начала года
            continue
        yield dt.date()


def get_week_start(date=None):
    """Возвращает дату первого дня недели (понедельника).

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :rtype: datetime.date
    """
    if date is None:
        date = datetime.date.today()

    result = date - datetime.timedelta(days=date.weekday())

    return result


def get_week_end(date=None):
    """Возвращает дату последнего дня недели (воскресенья).

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :rtype: datetime.date
    """
    if date is None:
        date = datetime.date.today()

    result = date + datetime.timedelta(days=SUN_IDX - date.weekday())

    return result


def get_week_dates(date=None):
    """Возвращает даты дней недели.

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date

    :rtype: dateutli.rrule.rrule
    """
    if date is None:
        date = datetime.date.today()

    monday = get_week_start(date)

    return (day.date() for day in rrule.rrule(rrule.DAILY, dtstart=monday, count=len(WEEKDAYS)))


def get_weekdays_for_date(date=None, weekday_names=None):
    """Возвращает названия и даты дней недели.

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :param weekday_names: Список или словарь наименований дней недели.
    :type weekday_names: dict, list

    :return: Кортеж из кортежей вида ('Название дня недели', дата).
    :rtype: tuple
    """
    weekday_names = weekday_names or WEEKDAYS_DICT

    return tuple((weekday_names[day.weekday()], day) for day in get_week_dates(date))


def get_today_min_datetime() -> datetime:
    """Возвращает дату/время начала текущих суток."""
    return datetime.datetime.combine(datetime.date.today(), datetime.time.min)


def get_today_max_datetime() -> datetime:
    """Возвращает дату/время окончания текущих суток."""
    return datetime.datetime.combine(datetime.date.today(), datetime.time.max)


def get_date_range_intersection(
    *date_ranges: Tuple[datetime.date, datetime.date],
) -> Union[Tuple[datetime.date, datetime.date], tuple]:
    """Возвращает минимальный внутренний диапазон дат из переданных диапазонов дат.

    В случае если диапазоны не пересекаются, возвращается пустой кортеж.
    """
    min_date = max((date_range[0] for date_range in date_ranges))
    max_date = min((date_range[1] for date_range in date_ranges))

    if min_date > max_date:
        date_range = ()
    else:
        date_range = min_date, max_date

    return date_range


def is_date_range_intersection(*date_ranges: Tuple[datetime.date, datetime.date]) -> bool:
    """Возвращает признак того, что диапазоны дат пересекаются."""
    intersection = get_date_range_intersection(*date_ranges)

    return True if intersection else False


def date_to_str(date_: Optional[Union[datetime.date, datetime.datetime]], fmt: str = settings.DATE_FORMAT) -> str:
    """Конвертирует дату в строку или возвращает '' если даты нет."""
    return date_.strftime(fmt) if date_ else ''


class Week(namedtuple('Week', ('year', 'week'))):
    """Работа с неделей."""

    @classmethod
    def withdate(cls, date):
        """Возвращает неделю, в которую входит дата."""
        return cls(*(date.isocalendar()[:2]))

    def day(self, number: int) -> datetime.date:
        """Возвращает дату дня недели.

        4 января должно попадать в первую неделю года и не важно на какой
        из дней недели приходится.
        Пример: если 4 января является воскресеньем, то это определенно 1-ая
        неделя года.
        """
        d = datetime.date(self.year, 1, 4)
        return d + datetime.timedelta(weeks=self.week - 1, days=-d.weekday() + number)

    def monday(self) -> datetime.date:
        """Дата понедельника."""
        return self.day(0)

    def sunday(self) -> datetime.date:
        """Дата воскресенья."""
        return self.day(6)

    def start_end_week(self) -> Tuple[datetime.date, datetime.date]:
        """Возвращает кортеж из даты начала и конца недели."""
        return self.day(0), self.day(6)

    def contains(self, day: datetime.date):
        """Проверяет попадание дня в текущую неделю."""
        return self.day(0) <= day < self.day(7)

    def year_week(self) -> Tuple[int, int]:
        """Возвращает кортеж (год, номер недели)."""
        return self.year, self.week

    def __repr__(self):  # noqa: D105
        return f'{self.__class__.__name__}({self.year}, {self.week})'


class DatesSplitter:
    """
    Класс, который разбивает заданный промежуток дат на дни, недели, месяцы или года.

    Разбивает период по дням, неделям, месяцам и годам (параметр split_by: SPLIT_BY_DAY, SPLIT_BY_WEEK, SPLIT_BY_MONTH, SPLIT_BY_YEAR).
    Может работать в двух режимах (параметр split_mode): WS_MODE (wednesday-to-sunday) и WW_MODE (wednesday-to-wednesday);
    Такие названия даны, чтобы лучше понимать их смысл:
    1. WS_MODE (wednesday-to-sunday). Например, задан период от среды текущей недели до субботы следующей недели и режим разбивки по Неделям (week).
        Вернется результат:
        [
            (среда, воскресение),
            (понедельник, суббота),
        ]
    2. WW_MODE (wednesday-to-wednesday). Например, если задан такой же период и режим, что и в первом примере, то вернется:
        [
            (среда, вторник),
            (среда, суббота),
        ]

    Аналогично происходит работа и для разбивки по месяцам и годам, за исключением разбивки по дням (там логика одинаковая для обоих режимов).

    Чтобы разбить период по N недель, месяцев или лет, также нужно задать параметр split_by_quantity (по умолчанию 1).
    """

    DEFAULT_TIME_START = dict(hour=0, minute=0, second=0)
    DEFAULT_TIME_END = dict(hour=23, minute=59, second=59)

    SPLIT_BY_DAY = 'day'
    SPLIT_BY_WEEK = 'week'
    SPLIT_BY_MONTH = 'month'
    SPLIT_BY_YEAR = 'year'

    # Режим wednesday-to-wednesday (см. документацию класса)
    WW_MODE = 'ww'
    # Режим wednesday-to-sunday (см. документацию класса)
    WS_MODE = 'ws'

    def __init__(
        self,
        split_by: str,
        split_mode: str = WW_MODE,
        split_by_quantity: int = 1,
    ):
        """Инициализация."""
        self.split_by = split_by
        self.split_mode = split_mode
        self.split_by_quantity = split_by_quantity

    @classmethod
    def get_modes(cls) -> tuple:
        """Возвращает режимы работы сплиттера."""
        return cls.WW_MODE, cls.WS_MODE

    @classmethod
    def get_split_by_modes(cls) -> tuple:
        """Возвращает варианты разбиения периода."""
        return cls.SPLIT_BY_DAY, cls.SPLIT_BY_WEEK, cls.SPLIT_BY_MONTH, cls.SPLIT_BY_YEAR

    def calculate_dates_range(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
        start_date: datetime.datetime,
        relativedelta_param: Dict[str, int],
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Вычисляет промежутки дат между заданными датами по указанным правилам."""
        result = []
        idx = 0
        current = start_date

        while current < period_ended_at:
            if idx > 0:
                previous_day = current - relativedelta(seconds=1)
                result.extend([previous_day, current])
            else:
                result.append(current)

            current += relativedelta(**relativedelta_param)
            idx += 1

        if self.split_mode == self.WS_MODE:
            result[0] = period_started_at

        result.append(period_ended_at)

        return list(zip(result[0::2], result[1::2]))

    def _split_by_day(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Разделяет заданный промежуток по дням в режиме wednesday-to-sunday."""
        return self.calculate_dates_range(
            period_started_at=period_started_at,
            period_ended_at=period_ended_at,
            start_date=period_started_at,
            relativedelta_param=dict(days=self.split_by_quantity),
        )

    def _split_by_week(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Разделяет заданный промежуток по неделям."""
        # Дата начала недели в зависимости от режима работы сплиттера:
        start_date_map = {
            self.WS_MODE: period_started_at - relativedelta(days=period_started_at.weekday()),
            self.WW_MODE: period_started_at,
        }
        return self.calculate_dates_range(
            period_started_at=period_started_at,
            period_ended_at=period_ended_at,
            start_date=start_date_map[self.split_mode],
            relativedelta_param=dict(weeks=self.split_by_quantity),
        )

    def _split_by_month(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Разделяет заданный промежуток по месяцам в режиме wednesday-to-sunday."""
        # Дата начала периода в зависимости от режима работы сплиттера:
        start_date_map = {
            self.WS_MODE: period_started_at.replace(day=1),
            self.WW_MODE: period_started_at,
        }
        return self.calculate_dates_range(
            period_started_at=period_started_at,
            period_ended_at=period_ended_at,
            start_date=start_date_map[self.split_mode],
            relativedelta_param=dict(months=self.split_by_quantity),
        )

    def _split_by_year(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """Разделяет заданный промежуток по годам в режиме wednesday-to-sunday."""
        # Дата начала периода в зависимости от режима работы сплиттера:
        start_date_map = {
            self.WS_MODE: period_started_at.replace(day=1),
            self.WW_MODE: period_started_at,
        }
        return self.calculate_dates_range(
            period_started_at=period_started_at,
            period_ended_at=period_ended_at,
            start_date=start_date_map[self.split_mode],
            relativedelta_param=dict(years=self.split_by_quantity),
        )

    def split(
        self,
        period_started_at: datetime.datetime,
        period_ended_at: datetime.datetime,
        make_default_time=True,
    ) -> List[datetime.datetime]:
        """Главный метод."""
        if make_default_time:
            period_started_at = period_started_at.replace(**self.DEFAULT_TIME_START)
            period_ended_at = period_ended_at.replace(**self.DEFAULT_TIME_END)

        split_function = getattr(self, f'_split_by_{self.split_by}')

        return split_function(period_started_at, period_ended_at)
