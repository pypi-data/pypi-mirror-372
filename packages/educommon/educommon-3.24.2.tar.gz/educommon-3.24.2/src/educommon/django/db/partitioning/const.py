# Количество записей, попадающих в итератор курсора бд при запросе удаления таблиц
CURSOR_ITERSIZE = 10_000
# Количество записей, попадающих в итератор курсора бд при запросе разбиения таблиц.
INSERT_CURSOR_ITERSIZE = 100


# Стандартный список функций при инициализации партицирования
BASE_PARTITION_FUNCTIONS = (
    'getattr',
    'get_partition_name',
    'set_partition_constraint',
    'table_exists',
    'is_table_partitioned',
    'create_partition',
    'trigger_exists',
)

# Функции для работы триггеров партицированных таблиц
PARTITION_TRIGGERS_FUNCTIONS = BASE_PARTITION_FUNCTIONS + (
    'before_insert',
    'instead_of_insert',
    'before_update',
    'after_insert',
)
