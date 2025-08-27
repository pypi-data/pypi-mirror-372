from django.contrib.postgres.fields.array import (
    ArrayField,
)
from django.db import (
    models,
)
from mptt.models import (
    MPTTModel,
    TreeForeignKey,
)

from educommon.django.db.mixins.validation import (
    post_clean,
)
from educommon.django.db.models import (
    BaseModel,
)
from educommon.m3.extensions.listeners.delete_check.mixins import (
    CascadeDeleteMixin,
)
from educommon.report.constructor import (
    constants,
)
from educommon.report.constructor.registries import (
    registry,
)
from educommon.report.constructor.validators import (
    validate_data_source_name,
)
from educommon.utils.misc import (
    cached_property,
)
from objectpack.exceptions import (
    ValidationError,
)


class ReportTemplate(CascadeDeleteMixin, BaseModel):
    """Модель "Шаблон отчета"."""

    USER_DEFINED = constants.FORMAT_USER_DEFINED
    EXCEL_SIMPLE = constants.FORMAT_EXCEL_SIMPLE
    EXCEL_MERGED = constants.FORMAT_EXCEL_MERGED
    FORMAT_CHOICES = constants.FORMAT_CHOICES

    title = models.CharField(
        'Наименование шаблона отчета',
        max_length=1000,
        unique=True,
    )
    data_source_name = models.CharField(
        'Имя источника данных',
        max_length=500,
        validators=[validate_data_source_name],
    )
    format = models.PositiveSmallIntegerField(
        'Формат сборки',
        choices=FORMAT_CHOICES,
        default=USER_DEFINED,
    )
    include_available_units = models.BooleanField('Отображать данные по дочерним организациям', default=False)

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'

    def simple_clean(self, errors):
        # ---------------------------------------------------------------------
        # Проверка уникальности наименования шаблона отчета.
        if self.title:
            query = ReportTemplate.objects.filter(
                title__smart_iexact=self.title,
            )
            if self.pk:
                query = query.exclude(pk=self.pk)

            if query.exists():
                errors['title'].append('Шаблон отчета с подобным именем уже существует.')
        # ---------------------------------------------------------------------
        super().simple_clean(errors)

    @cached_property
    def data_source(self):
        if self.data_source_name not in registry:
            raise ValidationError(
                'В шаблоне отчета указан несуществующий источник данных ({}).'.format(self.data_source_name)
            )
        data_source = registry.get(self.data_source_name).get_data_source_descriptor()
        return data_source

    def __str__(self):
        return 'Шаблон отчета: {}'.format(self.title)


# -----------------------------------------------------------------------------


class ReportColumn(BaseModel):
    """Модель "Столбец отчета"."""

    # Направления сортировки.
    ASCENDING = constants.SORT_ASCENDING
    DESCENDING = constants.SORT_DESCENDING
    SORT_CHOICES = constants.SORT_CHOICES

    report_template = models.ForeignKey(
        ReportTemplate,
        verbose_name='Отчет',
        related_name='columns',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Имя столбца в источнике данных',
        max_length=300,
    )
    index = models.PositiveSmallIntegerField(
        'Порядковый номер',
    )
    visible = models.BooleanField(
        'Видимость колонки в отчете',
        default=True,
    )
    title = models.CharField(
        'Отображаемое имя',
        max_length=300,
        null=True,
        blank=True,
    )
    by_value = models.PositiveSmallIntegerField(
        'Промежуточный итог', choices=constants.BY_VALUE_CHOICES, blank=True, null=True
    )
    total = models.PositiveSmallIntegerField('Итог', choices=constants.TOTAL_CHOICES, blank=True, null=True)

    cascade_delete_for = (report_template,)

    class Meta:
        verbose_name = 'Столбец отчета'
        verbose_name_plural = 'Столбцы отчетов'
        unique_together = (('report_template', 'name'),)
        ordering = ('index',)

    def _clean_aggregator_type(self, errors):
        """Проверяет на соответствие типов итогов."""
        if not ((self.by_value == self.total) or (any(not bool(item) for item in (self.by_value, self.total)))):
            errors['by_value'].append('Тип для "Промежуточный итог" и "Итог" должен совпадать.')

    def _clean_aggregator_data_type(self, errors):
        """Проверяет тип данных для итогов."""
        # Определяем тип данных в колонке.
        data_source_descriptor = registry.get(self.report_template.data_source_name).get_data_source_descriptor()
        column_descriptor = data_source_descriptor.get_column_descriptor(self.name)
        is_num_data_type = column_descriptor.data_type == constants.CT_NUMBER
        # Определяем тип Промежуточного итога.
        is_sum_by_value = self.by_value and self.by_value == constants.BY_VALUE_SUM
        # Определяем тип Итога.
        is_total_sum = self.total and self.total == constants.TOTAL_SUM
        aggregator_info = (('by_value', is_sum_by_value), ('total', is_total_sum))
        for aggregator_type, is_sum in aggregator_info:
            if is_sum and not is_num_data_type:
                errors[aggregator_type].append(
                    'Подсчет суммы недопустим для колонки "{}".'.format(
                        column_descriptor.get_full_title(),
                    )
                )

    def simple_clean(self, errors):
        """Добавляет проверку для подсчета итогов."""
        self._clean_aggregator_type(errors)
        self._clean_aggregator_data_type(errors)

        super().simple_clean(errors)

    def __str__(self):
        return self.title


# -----------------------------------------------------------------------------


class ReportFilterGroup(MPTTModel, BaseModel):
    """Группа фильтров.

    Фильтры объединяются в группы с помощью логических операторов "И" и "ИЛИ".
    При этом группы фильтров также могут быть объединены в группы. В итоге
    получается древовидная структура, представляющая собой подобие
    синтаксического дерева. Модели ``ReportFilterGroup`` и ``ReportFilter``
    используются для формирования таких деревьев.
    """

    # В связи с временными ограничениями на разработку функционала в окне
    # редактирования шаблона отображается "плоский" список фильтров, а не
    # древовидная иерархия. В связи с этим, несмотря на наличие возможности
    # хранить в БД сложно организованные фильтры, в интерфейсе такой
    # возможности не предусматрено. В случае, если у пользователей в будущем
    # возникнет потребность в создании более сложных фильтров, понадобится
    # переработка только интерфейсной части (окна редактирования шаблона).

    OPERATOR_AND = 1
    OPERATOR_OR = 2
    OPERATOR_CHOICES = (
        (OPERATOR_AND, 'И'),
        (OPERATOR_OR, 'ИЛИ'),
    )

    report_template = models.ForeignKey(
        ReportTemplate,
        verbose_name='Отчет',
        related_name='filter_groups',
        on_delete=models.CASCADE,
    )
    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        verbose_name='Родительская группа',
        related_name='nested_groups',
        on_delete=models.CASCADE,
    )
    operator = models.PositiveSmallIntegerField(
        'Логический оператор',
        help_text='Логический оператор, объединяющий фильтры в группе',
        choices=OPERATOR_CHOICES,
    )

    cascade_delete_for = (report_template,)

    class Meta:
        verbose_name = 'Группа фильтров'
        verbose_name_plural = 'Группы фильтров'

    def __str__(self):
        return self.get_operator_display()

    @staticmethod
    def check_filter(instance, errors, **kwargs):
        """Проверка фильтров в контексте группы фильтров.

            1. Группа фильтра и столбца фильтра должны быть в одном и том же
               шаблоне.

        Вызывается через сигнал ``post_clean`` для объектов модели
        ``ReportFilter``.

        :param instance: Проверяемый период обучения.
        :type instance: :class:`~extedu.core.models.period.Period`

        :param errors: Словарь с сообщениями об ошибках валидации.
        :type errors: :class:`defaultdict`
        """
        report_filter = instance

        if (
            not report_filter.pk
            or not report_filter.group_id
            or not report_filter.column_id
            or not report_filter.group.report_template_id
        ):
            return

        column = report_filter.column
        group = report_filter.group
        # ---------------------------------------------------------------------
        # Колонка фильтра должна быть в том же шаблоне, что и группа.

        if column.report_template_id != group.report_template_id:
            errors['column'].append(
                'Шаблон, к которому относится столбец фильтра "{}" '
                'отличается от шаблона, к которому относится группа фильтров.'.format(column.name)
            )
        # ---------------------------------------------------------------------

    def simple_clean(self, errors):
        super().simple_clean(errors)
        # ---------------------------------------------------------------------
        # Все столбцы в фильтрах группы должны быть в том же шаблоне, что и
        # данная группа.

        if (
            self.pk
            and self.report_template_id
            and self.filters.exclude(
                column__report_template=self.report_template_id,
            ).exists()
        ):
            errors['report_template'].append('В данной группе есть фильтры, ссылающиеся на столбцы из другого шаблона.')
        # ---------------------------------------------------------------------
        # Шаблоны данной группы и родительской должны совпадать.

        if (
            self.pk
            and self.report_template_id
            and self.parent
            and self.parent.report_template_id
            and self.report_template_id != self.parent.report_template_id
        ):
            errors['parent'].append(
                'Шаблон данной группы фильтров ("{}") отличается от шаблона родительской группы ("{}").'.format(
                    self.report_template.title,
                    self.parent.report_template.title,
                )
            )


# -----------------------------------------------------------------------------


class ReportFilter(BaseModel):
    """Модель "Параметр фильтрации данных отчета"."""

    group = models.ForeignKey(
        ReportFilterGroup,
        verbose_name='Группа фильтров',
        related_name='filters',
        on_delete=models.CASCADE,
    )
    column = models.ForeignKey(
        ReportColumn,
        verbose_name='Столбец',
        related_name='filters',
        on_delete=models.CASCADE,
    )
    index = models.PositiveSmallIntegerField(
        'Порядковый номер',
    )
    operator = models.PositiveSmallIntegerField(
        'Оператор сравнения',
        choices=constants.OPERATOR_CHOICES,
    )
    exclude = models.BooleanField(
        'Исключать записи, удовлетворяющие условию',
        default=False,
    )
    case_sensitive = models.BooleanField('Учет регистра', null=True)
    values = ArrayField(
        models.TextField(
            'Значение',
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
    )
    comment = models.TextField(
        'Описание фильтра',
        blank=True,
        null=True,
    )

    cascade_delete_for = (group, column)

    def __str__(self):
        """Возвращает строку вида:
        `Поле "<название_поля>" [не ]<оператор:меньше или равно|меньше|...>
        "<значение>", <без учета|с учетом> регистра`
        :return:
        """
        template = 'Поле "{col}"{invert__op:10}{operator} "{value}", {case} регистра'
        invert__op = ' не ' if self.exclude else ' '
        case = 'с учетом' if self.case_sensitive else 'без учета'
        return template.format(
            col=self.column,
            invert__op=invert__op,
            operator=self.get_operator_display().lower(),
            value=', '.join(self.values),
            case=case,
        )

    class Meta:
        verbose_name = 'Фильтр'
        verbose_name_plural = 'Фильтры'
        unique_together = (('column', 'index'),)
        ordering = ('index',)

    def simple_clean(self, errors):
        super().simple_clean(errors)
        # ---------------------------------------------------------------------
        # Значение должно быть указано для всех операторов, кроме IS_NULL.

        if self.operator == constants.IS_NULL:
            self.values = None

        elif self.operator == constants.BETWEEN and (not self.values or len(self.values) != 2):
            errors['values'].append(
                'Для оператора "{}" должно быть указано два значения.'.format(self.get_operator_display())
            )

        elif self.operator not in (
            constants.IN,
            constants.BETWEEN,
        ) and (not self.values or len(self.values) > 1):
            errors['values'].append('Должно быть указано только одно значение.')

        elif not self.values:
            errors['values'].append('Не указано значение для сравнения.')
        # ---------------------------------------------------------------------

        if self.group and self.column and self.group.report_template_id != self.column.report_template_id:
            errors['column'].append('Группа и колонка принадлежат разным шаблонам.')
        # ---------------------------------------------------------------------

        data_source_descriptor = registry.get(self.group.report_template.data_source_name).get_data_source_descriptor()
        column_descriptor = data_source_descriptor.get_column_descriptor(self.column.name)
        data_type = column_descriptor.data_type
        valid_operators = constants.VALID_OPERATORS[data_type]
        if self.operator and self.operator not in valid_operators:
            errors['operator'].append(
                'Оператор "{}" недопустим для колонки "{}".'.format(
                    self.get_operator_display(),
                    column_descriptor.get_full_title(),
                )
            )


# -----------------------------------------------------------------------------


class ReportSorting(BaseModel):
    """Модель "Параметр сортировки данных отчета"."""

    column = models.OneToOneField(
        ReportColumn,
        verbose_name='Колонка',
        related_name='sorting',
        on_delete=models.CASCADE,
    )
    direction = models.PositiveSmallIntegerField(
        'Направление сортировки',
        choices=constants.DIRECTION_CHOICES,
    )
    index = models.PositiveSmallIntegerField(
        'Порядковый номер',
    )

    class Meta:
        verbose_name = 'Сортировка'
        verbose_name_plural = 'Сортировка'
        ordering = ('index',)

    def __str__(self):
        return '{col} ({direction})'.format(col=self.column, direction=self.get_direction_display().lower())


# -----------------------------------------------------------------------------


post_clean.connect(ReportFilterGroup.check_filter, ReportFilter, dispatch_uid='ReportFilterGroup.check_filter')
