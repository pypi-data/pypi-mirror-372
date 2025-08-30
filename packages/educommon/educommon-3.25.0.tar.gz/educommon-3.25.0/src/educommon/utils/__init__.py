"""Вспомогательные средства."""


def is_ranges_intersected(range1, range2):
    """Возвращает True, если указанные интервалы значений пересекаются.

    Интервалы задаются в виде двухэлементных кортежей, первый элемент кортежа
    определяет начало интервала, а второй - конец интервала. None определяет
    открытый с соответствующей стороны интервал.

    Типы данных в интервалах должны поддерживать сравнение значений с помощью
    оператора <=.

    :rtype: bool
    """
    (from1, to1), (from2, to2) = range1, range2

    assert from1 is None or to1 is None or from1 <= to1, (from1, to1)
    assert from2 is None or to2 is None or from2 <= to2, (from2, to2)

    if from1 is None and to1 is None:
        result = True

    elif from1 is not None and to1 is None:
        result = to2 is None or from1 <= to2

    elif from1 is None and to1 is not None:
        result = from2 is None or from2 <= to1

    else:  # from1 is not None and to1 is not None
        if from2 is None and to2 is None:
            result = True

        elif from2 is not None and to2 is None:
            result = from2 <= to1

        elif from2 is None and to2 is not None:
            result = from1 <= to2

        else:  # from2 is not None and to2 is not None
            result = from2 <= to1 and from1 <= to2

    return result


class SingletonMeta(type):
    """Метакласс для классов-одиночек.

    Потомки класса с данным метаклассом также будут одиночками. Инициализация
    классов-одиночек (вызов метода ``__init__``) будет выполняться один раз
    при создании.

    .. code-block:: python

       class SingleClass:
           __metaclass__ = SingletonMeta
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)

        return cls.instance
