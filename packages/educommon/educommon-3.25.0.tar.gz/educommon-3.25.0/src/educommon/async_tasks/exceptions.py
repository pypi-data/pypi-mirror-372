class TaskUniqueException(Exception):
    """Задача уже в очереди или выполняется."""


class TaskLockDataValidationError(Exception):
    """Параметры блокировки не прошли проверку."""
