# -----------------------------------------------------------------------------
# Операторы фильтров.

(
    LE,
    LT,
    EQ,
    GT,
    GE,
    IS_NULL,
    CONTAINS,
    STARTS_WITH,
    ENDS_WITH,
    BETWEEN,
    IN,
) = range(1, 12)

OPERATOR_CHOICES = (
    (LE, 'Меньше или равно'),
    (LT, 'Меньше'),
    (EQ, 'Равно'),
    (GT, 'Больше'),
    (GE, 'Больше или равно'),
    (IS_NULL, 'Пусто'),
    (CONTAINS, 'Содержит'),
    (STARTS_WITH, 'Начинается с'),
    (ENDS_WITH, 'Заканчивается на'),
    (BETWEEN, 'Между'),
    (IN, 'Равно одному из'),
)
# -----------------------------------------------------------------------------
# Направления сортировки.

DIRECTION_ASC = 1
DIRECTION_DESC = 2
DIRECTION_CHOICES = (
    (DIRECTION_ASC, 'По возрастанию'),
    (DIRECTION_DESC, 'По убыванию'),
)
# -----------------------------------------------------------------------------
# Типы данных в столбцах.

CT_OTHER = 'other'
CT_CHOICES = 'choices'
CT_NUMBER = 'number'
CT_BOOLEAN = 'boolean'
CT_NULL_BOOLEAN = 'null_boolean'
CT_TEXT = 'text'
CT_DATE = 'date'
CT_TIME = 'time'
CT_DATETIME = 'datetime'
CT_DIRECT_RELATION = 'direct_relation'
CT_REVERSE_RELATION = 'reverse_relation'
# -----------------------------------------------------------------------------

# Допустимые операторы для каждого из типов данных.
VALID_OPERATORS = {
    CT_OTHER: (),
    CT_CHOICES: (EQ, IS_NULL, IN),
    CT_NUMBER: (LE, LT, EQ, GT, GE, IS_NULL, BETWEEN, IN),
    CT_BOOLEAN: (EQ,),
    CT_NULL_BOOLEAN: (EQ, IS_NULL),
    CT_TEXT: (EQ, IS_NULL, CONTAINS, STARTS_WITH, ENDS_WITH, IN),
    CT_DATE: (LE, LT, EQ, GT, GE, IS_NULL, BETWEEN, IN),
    CT_TIME: (LE, LT, EQ, GT, GE, IS_NULL, BETWEEN, IN),
    CT_DATETIME: (LE, LT, EQ, GT, GE, IS_NULL, BETWEEN, IN),
    CT_DIRECT_RELATION: (IS_NULL,),
    CT_REVERSE_RELATION: (IS_NULL,),
}
# -----------------------------------------------------------------------------
# Формат отчёта.

FORMAT_USER_DEFINED = 0
FORMAT_EXCEL_SIMPLE = 1
FORMAT_EXCEL_MERGED = 2
FORMAT_CHOICES = (
    (FORMAT_USER_DEFINED, 'Спрашивать перед сборкой'),
    (FORMAT_EXCEL_SIMPLE, 'Excel (без объединения ячеек)'),
    (FORMAT_EXCEL_MERGED, 'Excel (с объединением ячеек)'),
)
# -----------------------------------------------------------------------------
# Направления сортировки.

SORT_ASCENDING = 1
SORT_DESCENDING = 2
SORT_CHOICES = (
    (SORT_ASCENDING, 'По возрастанию'),
    (SORT_DESCENDING, 'По убыванию'),
)

TRUE = 'Да'
FALSE = 'Нет'
# -----------------------------------------------------------------------------
# Промежуточные итоги.

BY_VALUE_COUNT = 1
BY_VALUE_SUM = 2
BY_VALUE_CHOICES = (
    (BY_VALUE_COUNT, 'Количество'),
    (BY_VALUE_SUM, 'Сумма'),
)
# -----------------------------------------------------------------------------
# Итоги.

TOTAL_COUNT = 1
TOTAL_SUM = 2
TOTAL_UNIQUE_COUNT = 3
TOTAL_CHOICES = (
    (TOTAL_COUNT, 'Количество'),
    (TOTAL_SUM, 'Сумма'),
    (TOTAL_UNIQUE_COUNT, 'Количество уникальных'),
)
