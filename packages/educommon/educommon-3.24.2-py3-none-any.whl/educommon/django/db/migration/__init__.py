import datetime
from functools import (
    partial,
)
from operator import (
    sub,
)


def date_difference_as_callable(diff, date_fn=datetime.date.today, operator_=sub):
    """Функция, возвращающая callable-объект, не принимающий аргументов и
    возвращающий дату.
    Используется для валидации дат, когда нужно проверить не точную дату, а
    изменяющееся значение (например, что дата не позднее сегодняшнего дня).
    Используется в паре с валидатором
    educommon.django.db.validators.simple.date_range_validator
    :param diff:
    :type diff: datetime.timedelta
    :param date_fn:
    :type date_fn: Callable[[], datetime.date]
    :param operator_:
    :type: Union[operator.add, operator.sub]
    :return:
    :rtype: Callable[[], datetime.date]
    """
    return partial(_get_time_difference_from_callable, operator_=operator_, date_fn=date_fn, diff=diff)


def _get_time_difference_from_callable(operator_, date_fn, diff):
    """Вспомогательная функция для сериализации валидатора при генерации
    файла-миграции. Нужен для того, чтобы при генерации миграции функция
    date_fn не разворачивалась в точное значение, а оставалась функцией.
    В `models.py` в качестве границы нужно использовать
    `date_difference_as_callable`, а не данную функцию.
    :param operator_:
    :param date_fn:
    :param diff:
    :return:
    :rtype: datetime.date
    """
    return operator_(date_fn(), diff)
