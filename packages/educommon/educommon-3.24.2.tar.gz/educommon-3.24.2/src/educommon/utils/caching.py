import collections
import inspect

from django.core.cache import (
    cache,
)


def lru_cache(**kwargs):
    """Замена декоратора lru_cache для Python до версии 3.2.

    Если lru_cache не может быть импортирован, то функция будет вызываться
    как обычно.

    :param kwargs: Параметры, которые нужно передать в lru_cache
    """
    try:
        from functools import (
            lru_cache,
        )
    except ImportError:
        return lambda function: function
    else:
        return lru_cache(**kwargs)


class NotExist:
    """Аналог None для контекстов, где None не подходит."""


def cached_function(cache_time, cache_prefix, names_kwargs=None):
    """
    Кэширует результат функции на указанное время
    для указанного набора параметров функции.

    В вызове целевой функции проверяемые здесь аргументы
    должны быть именованными.

    :param cache_prefix: - общее условное наименование набора кэшируемых функций
    :param cache_time: - время кэширования в секундах
    :param names_kwargs: - кортеж имен именованных аргументов.
                           не поддерживаются mutable.
    """
    assert isinstance(cache_prefix, str)
    assert isinstance(cache_time, int)
    assert names_kwargs is None or isinstance(names_kwargs, tuple)
    assert all(isinstance(k, collections.Hashable) for k in names_kwargs)

    names_kwargs = names_kwargs or ()

    def decorator(fn):
        return CacheWrapper(fn, cache_time, cache_prefix, names_kwargs)

    return decorator


class CacheWrapper:
    """Возвращает кэшированное значение обернутой функции self.fn."""

    def __init__(self, fn, cache_time, cache_prefix, names_kwargs):
        self.fn = fn
        self.cache_time = cache_time
        self.cache_prefix = cache_prefix
        self.names_kwargs = sorted(names_kwargs)

    def __call__(self, *a, **kw):
        """
        Возврат значения из кэша или вызов обернутой функции.

        Определяет ключ кэша, сопоставляя сигнатуру функции и передаваемые
        аргументы.
        """
        callargs = inspect.getcallargs(self.fn, *a, **kw)
        cache_key = self.get_cache_key(**callargs)
        res = cache.get(cache_key, NotExist)
        if res is NotExist:
            res = self.fn(*a, **kw)
            cache.set(cache_key, res, self.cache_time)
        return res

    def get_cache_key(self, **callargs):
        """
        Возвращает ключ кэша для значений self.names_kwargs из callargs.

        :param callargs: Словарь, ключи которого содержат self.names_kwargs
        :type callargs: dict
        """
        kwarg_vals = tuple(callargs[k] for k in self.names_kwargs)
        hash_kwargs = hash(kwarg_vals)
        cache_key = '_'.join((self.cache_prefix, self.fn.__name__, str(hash_kwargs)))
        return cache_key

    def update_cache(self, value, **kw):
        """
        Обновляет кэш значением value по ключу, вычисленному из **kw.

        В отличие от self.__call__ необходимо явно передать в kw все значения
        из self.names_kwargs.

        :param kw: Словарь, ключи которого содержат self.names_kwargs
        :type kw: dict
        """
        cache.set(self.get_cache_key(**kw), value, self.cache_time)

    def __repr__(self):  # noqa D105
        return '{} for "{}"'.format(self.__class__.__name__, repr(self.fn))
