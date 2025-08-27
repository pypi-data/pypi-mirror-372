from pygost.gost34112012256 import (
    GOST34112012256,
)
from pygost.gost34112012512 import (
    GOST34112012512,
)

from educommon.utils.enums import (
    HashGostFunctionVersion,
)


class HashData:
    """Хэширует данные."""

    ALGORITHMS = {
        HashGostFunctionVersion.GOST12_256: GOST34112012256,
        HashGostFunctionVersion.GOST12_512: GOST34112012512,
    }

    def __init__(self, hash_algorithm: str, delimiter: str = ''):
        try:
            self.hash_function = self.ALGORITHMS[hash_algorithm]
        except KeyError:
            raise ValueError(f'Алгоритм "{hash_algorithm}" не поддерживается.')

        self.delimiter = delimiter

    def _get_hash(self, *args: str) -> str:
        """Возвращает HASH для строки сформированной из переданных данных.

        :param args: хэшируемые данные
        :return: хэш
        """
        text = self.delimiter.join(args).strip()
        hasher = self.hash_function(text.encode())

        return hasher.hexdigest()

    def get_hash(self, *args: str) -> str:
        """
        Интерфейс хэширования строки.

        Возвращает хэш-строку.
        """
        return self._get_hash(*args)

    def get_upper_hash(self, *args: str) -> str:
        """
        Интерфейс хэширования строки.

        Возвращает хэш-строку в верхнем регистре.
        """
        return self._get_hash(*args).upper()
