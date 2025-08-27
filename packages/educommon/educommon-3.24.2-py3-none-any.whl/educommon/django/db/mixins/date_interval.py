from datetime import (
    date,
    datetime,
)

from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError,
)
from django.db import (
    models,
)
from django.db.models.query_utils import (
    Q,
)
from m3_django_compat import (
    Manager,
    ModelOptions,
)

from educommon import (
    Undefined,
)
from educommon.utils import (
    is_ranges_intersected,
)
from educommon.utils.date import (
    date_range_to_str,
)


class BaseIntervalMeta(models.base.ModelBase):
    """Базовый метакласс для примесей *IntervalMixin.

    Добавляет к создаваемой модели поля, содержащие границы интервала. Имена
    полей задаются в атрибуте interval_field_names.
    """

    # тип поля модели, определяется в потомке
    _interval_bound_field_type = None

    @classmethod
    def _mixin_stay(cls, bases):
        """Проверяет наличие Mixinа в переменных модуля.

        Должен быть переопределен в потомке."""
        raise NotImplementedError

    @staticmethod
    def __get_attr(name, attrs, bases, default=Undefined):
        """Возвращает значение атрибута с учетом родительских классов."""
        if name in attrs:
            result = attrs[name]
        else:
            for base in bases:
                if hasattr(base, name):
                    result = getattr(base, name)
                    break
            else:
                result = Undefined

        return result

    def __new__(cls, name, bases, attrs):
        if cls._mixin_stay(bases) and (
            # поля с границами интервала создаются только если модель не
            # абстрактная.
            'Meta' not in attrs or not hasattr(attrs['Meta'], 'abstract') or not attrs['Meta'].abstract
        ):
            interval_field_names = cls.__get_attr('interval_field_names', attrs, bases, cls.interval_field_names)

            # Добавление полей, хранящих границы интервала
            for field_name, verbose_name in zip(interval_field_names, ('Начало интервала', 'Конец интервала')):
                field = cls.__get_attr(field_name, attrs, bases)
                if field is Undefined:
                    attrs[field_name] = cls._interval_bound_field_type(
                        name=field_name,
                        blank=True,
                        null=True,
                        verbose_name=verbose_name,
                    )

        return super().__new__(cls, name, bases, attrs)


class DateIntervalMeta(BaseIntervalMeta):
    """Метакласс для примеси DateIntervalMixin.

    Добавляет к создаваемой модели поля дат, содержащие границы интервала.
    Имена полей задаются в атрибуте interval_field_names.
    """

    # тип полей модели, которые будет созданы
    _interval_bound_field_type = models.DateField
    # названия полей по умолчанию
    interval_field_names = ('date_from', 'date_to')

    @classmethod
    def _mixin_stay(cls, bases):
        """Проверяет наличие DateIntervalMixin в переменных модуля.

        :rtype bool
        """
        return 'DateIntervalMixin' in globals() and any(issubclass(base, DateIntervalMixin) for base in bases)


class DateTimeIntervalMeta(BaseIntervalMeta):
    """Метакласс для примеси DateTimeIntervalMixin.

    Добавляет к создаваемой модели поля дат со временем, содержащие
    границы интервала. Имена полей задаются в атрибуте interval_field_names.
    """

    # тип полей модели, которые будет созданы
    _interval_bound_field_type = models.DateTimeField
    # названия полей по умолчанию
    interval_field_names = ('datetime_from', 'datetime_to')

    @classmethod
    def _mixin_stay(cls, bases):
        """Проверяет наличие DateTimeIntervalMixin в переменных модуля.

        :rtype bool
        """
        return 'DateTimeIntervalMixin' in globals() and any(issubclass(base, DateTimeIntervalMixin) for base in bases)


class BaseIntervalMixin(models.Model):
    """Базовый класс для примесей к моделям, добавляющих интервал дат.

    Содержит два поля: date_from (дата начала интервала) и date_to (дата
    окончания интервала). Значение None этих полей указывает на то, что
    временной интервал не ограничен с соответствующей стороны.
    """

    no_intersections_for = None
    """Список имен полей, по которым осуществляется поиск пересечений.

    Если в модели есть другие записи с такой же комбинацией значений указанных
    полей и пересекающимся интервалом, то экземпляр данной модели не пройдет
    валидацию данных.

    Если значением атрибута является None, проверка на пересечение не
    выполняется. Пустой список указывает на необходимость поиска пересечений
    со всеми записями модели.
    """

    _pg_type = None
    """Тип данных в PostgreSQL, задается в потомке.

    Используется для проверки пересечения диапазонов.
    """

    @classmethod
    def get_current_date(cls):
        """Возвращает текущую дату.

        :rtype: datetime.datetime or datetime.date
        """
        raise NotImplementedError

    @classmethod
    def get_date_in_intervals_filter(cls, day=None, lookup=None, include_lower_bound=True, include_upper_bound=True):
        """Возвращает фильтр для выборки записей по указанной дате.

        Условия фильтра включают записи, в интервал которых входит
        указанная дата.

        :params day: Дата, определяющая условия фильтра.
        :type day: datetime.datetime

        :param lookup: Список полей
        :type lookup: iterable

        :param bool include_lower_bound: Флаг, указывающий на необходимость
            учитывать нижнюю границу интервала. Значение ``False`` указывает
            на то, что при попадании значения :arg:`day` на нижнюю границу
            интервала такая запись не будет включена в выборку.

        :param bool include_upper_bound: Флаг, указывающий на необходимость
            учитывать верхнюю границу интервала. Значение ``False`` указывает
            на то, что при попадании значения :arg:`day` на верхнюю границу
            интервала такая запись не будет включена в выборку.

        :rtype: django.db.models.query_utils.Q
        """
        if day is None:
            day = cls.get_current_date()

        from_name, to_name = cls.interval_field_names
        if lookup is not None:
            from_lookup = '__'.join(list(lookup) + [from_name])
            to_lookup = '__'.join(list(lookup) + [to_name])
        else:
            from_lookup, to_lookup = from_name, to_name

        opts = ModelOptions(cls)

        suffix = 'e' if include_lower_bound else ''
        from_filter = Q(**{from_lookup + '__lt' + suffix: day})
        if opts.get_field(from_name).null:
            # В модели допускается не указывать начало интервала
            from_filter |= Q(**{from_lookup + '__isnull': True})

        suffix = 'e' if include_upper_bound else ''
        to_filter = Q(**{to_lookup + '__gt' + suffix: day})
        if opts.get_field(to_name).null:
            # В модели допускается не указывать конец интервала
            to_filter |= Q(**{to_lookup + '__isnull': True})

        result = from_filter & to_filter

        return result

    @classmethod
    def get_model_options(cls):
        return ModelOptions(cls)

    @classmethod
    def get_intersection_daterange_filter(
        cls, date_begin=None, date_end=None, lookup=None, include_lower_bound=True, include_upper_bound=True
    ):
        """Метод возвращает фильтр для выборки записей, попадающих в интервал.

        Для проверки пересечения двух интервалов a и b необходимо и
        достаточно выполнения двух условий:
        a.start <= b.end AND a.end >= b.start

        Пусть будут даны два интервала a и b, у которых соответственно задано
        начало и конец: a.start/a.end и b.start/b.end и считаем, что
        интервалы заданы от некого начала до некого конца, включая этот конец.

        Самое простое - это написать условие для не пересекающихся интервалов.

        Непересечение, это когда начало одного интервала больше конца другого
        интервала, или конец одного интервала меньше начала другого:
        a.start > b.end OR a.end < b.start
        Соответственно, пересечение - это отрицание того, что мы получили -
        т.е. если для интервалов выполняется
        NOT(a.start > b.end OR a.end < b.start).
        Теперь раскрываем по правилам логики скобки (свойство де Моргана) и
        получаем:
        a.start <= b.end AND a.end >= b.start

        Проверка вхождения даты в интервал с помощью
        get_date_in_intervals_filter для этих целей не годится. Это дает
        неверный результат.

        .. code-block:: python
            :caption: Пример использования
            query = model.objects.filter(model.get_intersection_daterange_filter(date_begin, date_end))

        :params date_begin: Дата начала интервала.
        :type date_begin: datetime.datetime

        :params date_end: Дата окончания интервала.
        :type date_end: datetime.datetime

        :param lookup: Список полей, объединенных '__'
        :type lookup: str

        :param bool include_lower_bound: Флаг, указывающий на необходимость
            учитывать нижнюю границу интервала. Значение ``False`` указывает
            на то, что при попадании значения :arg:`day` на нижнюю границу
            интервала такая запись не будет включена в выборку.

        :param bool include_upper_bound: Флаг, указывающий на необходимость
            учитывать верхнюю границу интервала. Значение ``False`` указывает
            на то, что при попадании значения :arg:`day` на верхнюю границу
            интервала такая запись не будет включена в выборку.

        :rtype: django.db.models.query_utils.Q
        """

        if date_begin is None:
            date_begin = cls.get_current_date()

        if date_end is None:
            date_end = cls.get_current_date()

        # Предполагается, что в интервалах дат дата окончания находится
        # справа по оси времени от даты начала или равна. Если будет наоборот,
        # то результат может оказаться не верным
        assert date_end >= date_begin, 'Дата окончания должна быть больше или равна дате начала'

        from_name, to_name = cls.interval_field_names
        if lookup is not None:
            from_lookup = '__'.join([lookup, from_name])
            to_lookup = '__'.join([lookup, to_name])
        else:
            from_lookup, to_lookup = from_name, to_name

        opts = cls.get_model_options()

        suffix = 'e' if include_lower_bound else ''
        from_filter = Q(**{from_lookup + '__lt' + suffix: date_end})
        if opts.get_field(from_name).null:
            # В модели допускается не указывать начало интервала
            from_filter |= Q(**{from_lookup + '__isnull': True})

        suffix = 'e' if include_upper_bound else ''
        to_filter = Q(**{to_lookup + '__gt' + suffix: date_begin})
        if opts.get_field(to_name).null:
            # В модели допускается не указывать конец интервала
            to_filter |= Q(**{to_lookup + '__isnull': True})

        result = from_filter & to_filter

        return result

    def is_date_in_interval(self, day):
        """Возвращает True, если указанная дата входит в интервал.

        :type day: datetime.date or datetime.datetime

        :rtype: bool
        """
        assert isinstance(day, (date, datetime)), type(day)
        date_from, date_to = self.interval_range
        result = (
            date_from is None
            and date_to is None
            or date_from is None
            and date_to is not None
            and day <= date_to
            or date_from is not None
            and date_to is None
            and day >= date_from
            or date_from is not None
            and date_to is not None
            and date_from <= day <= date_to
        )

        return result

    def is_intersected_with(self, date_from, date_to):
        """Проверка пересечения с указанным интервалом.

        :param date_from: Начало интервала, с которым проверяется пересечение.
        :type date_from: datetime.date or None or datetime.datetime

        :param date_to: Конец интервала, с которым проверяется пересечение.
        :type date_to: datetime.date or None or datetime.datetime

        :rtype: bool
        """
        assert isinstance(date_from, (date, type(None), datetime))
        assert isinstance(date_to, (date, type(None), datetime))

        return is_ranges_intersected(self.interval_range, (date_from, date_to))

    @property
    def interval_range(self):
        """Возвращает дату начала интервала и дату окончания интервала.

        :rtype: tuple
        """
        date_from_name, date_to_name = self.interval_field_names

        date_from = getattr(self, date_from_name)
        date_to = getattr(self, date_to_name)

        result = (date_from, date_to)

        return result

    @property
    def interval_range_str(self):
        date_from, date_to = self.interval_range
        result = date_range_to_str(date_from, date_to)
        return result

    def interval_dates_error_message(self):
        """Возвращает сообщение о неправильных границах интервала.

        :rtype: str
        """
        opts = ModelOptions(self)

        date_from_name, date_to_name = self.interval_field_names
        result = 'Значение "{}" должно быть раньше, чем "{}"'.format(
            opts.get_field(date_from_name).verbose_name.capitalize(),
            opts.get_field(date_to_name).verbose_name.lower(),
        )

        return result

    def interval_intersected_error_message(self, others=None):
        """Возвращает сообщение о пересечении интервалов.

        :param others: Записи, с интервалами которых пересекается интервал
            данной записи.

        :rtype: str
        """
        return 'Интервал пересекается с другими записями'

    @property
    def previous_interval(self):
        """Предыдущий интервал или None."""
        date_from_name, date_to_name = self.interval_field_names

        date_from = getattr(self, date_from_name)

        prev_intervals = self.__class__.objects.filter(**{'{}__lt'.format(date_to_name): date_from}).order_by(
            '-{}'.format(date_to_name)
        )

        return prev_intervals[0] if prev_intervals else None

    def get_intersected_query(self):
        """Запрос на выборку записей с пересекающимися интервалами.

        :rtype: django.db.models.query.QuerySet
        """
        if self.no_intersections_for is None:
            return self.__class__.objects.none()

        query = self.__class__.objects.all()

        if self.pk:
            query = query.exclude(pk=self.pk)

        if self.no_intersections_for:
            options = getattr(self, '_meta')
            conditions = {}
            for field in map(options.get_field, self.no_intersections_for):
                if isinstance(field, models.ForeignKey):
                    conditions[field.attname] = getattr(self, field.attname)
                else:
                    conditions[field.name] = getattr(self, field.name)
            query = query.filter(**conditions)

        # Для проверки пересечения диапазонов используется тип данных
        # PostgreSQL заданные в _pg_type
        from_field, to_field = self.interval_field_names
        condition = 'not isempty({} * {})'.format(
            "{}(%s, %s, '[]')".format(self._pg_type),
            "{}({}, {}, '[]')".format(self._pg_type, from_field, to_field),
        )
        query = query.extra(where=[condition], params=self.interval_range)

        return query

    @property
    def next_interval(self):
        """Следующий интервал или None."""
        date_from_name, date_to_name = self.interval_field_names

        date_to = getattr(self, date_to_name)

        next_intervals = self.__class__.objects.filter(**{'{}__gt'.format(date_from_name): date_to}).order_by(
            date_from_name
        )

        return next_intervals[0] if next_intervals else None

    def clean(self):
        """Валидация данных об интервале."""
        errors = {}

        try:
            super().clean()
        except ValidationError as error:
            errors = error.update_error_dict(errors)

        date_from, date_to = self.interval_range

        # Дата начала интервала должна быть раньше даты окончания
        if date_from is not None and date_to is not None and date_from > date_to:
            errors.setdefault(NON_FIELD_ERRORS, []).append(self.interval_dates_error_message())
        else:
            # Проверка пересения интервалов
            others = self.get_intersected_query()
            if others:
                errors.setdefault(NON_FIELD_ERRORS, []).append(self.interval_intersected_error_message(others))

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True


class DateIntervalMixin(BaseIntervalMixin, metaclass=DateIntervalMeta):
    """Примесь к моделям, добавляющяя интервал дат.

    Содержит два поля: date_from (дата начала интервала) и date_to (дата
    окончания интервала). Значение None этих полей указывает на то, что
    временной интервал не ограничен с соответствующей стороны.
    """

    _pg_type = 'daterange'
    """Тип данных в PostgreSQL для сравнения дат.

    Используется для проверки пересечения диапазонов.
    """

    interval_field_names = ('date_from', 'date_to')
    """Имена полей, хранящих границы интервала.

    При необходимости переименования полей нужно переопределить данный атрибут
    в потомке.

    .. code::
       class TestModel(DateIntervalMixin, BaseModel):
           interval_field_names = ('start', 'end')
    """

    @classmethod
    def get_current_date(cls):
        """Возвращает текущую дату.

        :rtype: datetime.date
        """
        return date.today()

    class Meta:
        abstract = True


class DateTimeIntervalMixin(BaseIntervalMixin, metaclass=DateTimeIntervalMeta):
    """Примесь к моделям, добавляющия интервал дат со временем.

    Содержит два поля: date_from (дата начала интервала) и date_to (дата
    окончания интервала). Значение None этих полей указывает на то, что
    временной интервал не ограничен с соответствующей стороны.
    """

    _pg_type = 'tstzrange'
    """Тип данных в PostgreSQL для сравнения дат со временем.

    Используется для проверки пересечения диапазонов.
    """

    interval_field_names = ('datetime_from', 'datetime_to')
    """Имена полей, хранящих границы интервала.

    При необходимости переименования полей нужно переопределить данный атрибут
    в потомке.

    .. code::
       class TestModel(DateTimeIntervalMixin, BaseModel):
           interval_field_names = ('start', 'end')
    """

    @classmethod
    def get_current_date(cls):
        """Возвращает текущую дату со временем.

        :rtype: datetime.datetime
        """
        return datetime.now()

    class Meta:
        abstract = True


class ActualObjectsManager(Manager):
    """Менеджер для интервальной модели.

    Отфильтровывает все объекты, в интервал которых входит текущая дата.
    """

    def contribute_to_class(self, model, name):
        assert issubclass(model, BaseIntervalMixin), type(model)

        super().contribute_to_class(model, name)

    def get_queryset(self):
        return super().get_queryset().filter(self.model.get_date_in_intervals_filter())
