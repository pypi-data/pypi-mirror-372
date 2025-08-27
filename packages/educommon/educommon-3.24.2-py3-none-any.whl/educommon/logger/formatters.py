from m3_db_utils.logger import (
    ConsoleSQLFormatter,
    FileSQLFormatter,
)


class WebEduConsoleSQLFormatter(ConsoleSQLFormatter):
    """
    Форматтер для логирования sql-запросов в консоль.
    """


class WebEduFileSQLFormatter(FileSQLFormatter):
    """
    Форматтер для логирования sql-запросов в файл.
    """
