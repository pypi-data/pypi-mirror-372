from collections import (
    defaultdict,
)
from functools import (
    lru_cache,
    wraps,
)
from inspect import (
    isclass,
)
from types import (
    FunctionType,
    MethodType,
)

from django.apps import (
    apps,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)

from educommon.utils import (
    SingletonMeta,
)


__all__ = ['extender_for']


class _ExtenderRegistry(metaclass=SingletonMeta):
    """Реестр расширителей классов.

    Обеспечивает работу декораторов
    :func:`~educommon.utils.plugins.extender_for` и
    :func:`~educommon.utils.plugins.extendable`.

    .. warning::

       Не предназначен для использования напрямую.
    """

    def __init__(self):
        self._extenders = defaultdict(list)

    def _get_extender_priority(self, extender):
        result = getattr(extender, 'priority', 0)
        if not isinstance(result, int):
            result = 0
        return result

    def add_extender(self, extendable_class, extender_class):
        """Добавление расширителя для класса.

        :param type extendable_class: Расширяемый класс.
        :param type extender_class: Расширяющий класс.
        """
        assert isclass(extendable_class), extendable_class
        assert isclass(extender_class), extender_class

        extenders = self._extenders[extendable_class]
        priority = self._get_extender_priority(extender_class)
        for i, ext in enumerate(extenders):
            if priority > self._get_extender_priority(ext):
                extenders.insert(i, extender_class)
                break
        else:
            extenders.append(extender_class)

    def get_extenders(self, extendable_class):
        """Возвращает генератор классов-расширителей для указанного класса.

        :param type extendable_class: Расширяемый класс.

        :rtype: generator
        """
        for extender_class in self._extenders[extendable_class]:
            yield extender_class


_extender_registry = _ExtenderRegistry()


def _function_types():
    """Возвращает типы функций и методов, доступных для расширения."""
    from m3_django_compat import (
        MethodDescriptorType,
        MethodWrapperType,
        WrapperDescriptorType,
    )

    return (FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType, MethodDescriptorType)


_function_types = lru_cache(maxsize=1)(_function_types)


def extender_for(*extendables):
    """Помечает класс, как расширитель для указанных классов.

    Имена расширяемых методов должны быть указаны в ``extends_methods``. Эти
    методы будут обернуты декоратором. Расширение staticmethod и classmethod
    не поддерживается.
    :func:`~educommon.utils.plugins.extendable`.

    Расширение функциональности классов работает следующим образом:

        1. Сначала вызывается метод расширяемого класса.
        2. Затем в порядке приоритета вызываются одноименные методы у
           классов-расширителей (если они есть в классе-расширителе). В первом
           аргументе передаётся экземпляр расширяемого класса (``self``),
           результат работы расширяемого метода или предыдущего расширителя, а
           также аргументы расширяемого метода.
        3. Результат работы последнего расширителя класса возвращается в
           качестве результата расширяемого метода.

    .. code-block:: python
       :caption: Пример использования

       @extender_for(ListWindow, AddWindow, EditWindow):
       class WindowExtender:

           extends_methods = ('set_params',)

           @staticmethod
           def set_params(window, result, params):
               window.width, window.height = 1000, 1000
               return result
    """
    assert all(isclass(extendable) for extendable in extendables)

    def decorator(extender):
        assert isclass(extender), extender
        assert extender.extends_methods
        assert all(
            isinstance(getattr(extendable, method_name), _function_types())
            for extendable in extendables
            for method_name in extender.extends_methods
        )

        for extendable_class in extendables:
            _extender_registry.add_extender(extendable_class, extender)

            for method_name in extender.extends_methods:
                method = getattr(extendable_class, method_name)
                if not getattr(method, '__extended__', None):
                    method = _extendable(method)
                    setattr(extendable_class, method_name, method)

        return extender

    return decorator


def _extendable(func):
    """Помечает метод класса как расширяемый.

    Методы, помеченные этим декоратором могут быть расширены в классах,
    помеченных декоратором :func:`~educommon.utils.plugins.extender_for`.

    О том, как работает расширение классов, написано в описании
    :func:`~educommon.utils.plugins.extender_for`.

    .. code-block:: python
       :caption: Пример использования

       class EditWindow(BaseEditWindow):
           @extendable
           def set_params(self, params): ...
    """
    assert isinstance(func, _function_types()), func

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        from m3_django_compat import (
            WrapperDescriptorType,
        )

        unbound_types = (
            FunctionType,
            WrapperDescriptorType,
        )

        assert all((isinstance(func, unbound_types), not isclass(self))), 'Нельзя расширить staticmethod и classmethod'

        result = func(self, *args, **kwargs)

        if isinstance(func, MethodType):
            method_name = func.__func__.__name__
        else:
            method_name = func.__name__

        extendable_class = self if isclass(self) else self.__class__

        for extender in _extender_registry.get_extenders(extendable_class):
            if method_name in extender.extends_methods:
                extender_method = getattr(extender, method_name, None)
                if callable(extender_method):
                    result = extender_method(self, result, *args, **kwargs)

        return result

    wrapper.__extended__ = True

    return wrapper


def get_plugin_apps():
    """Возвращает подключенные плагины.

    :rtype: generator of django.apps.config.AppConfig
    """
    return (
        app_config
        for app_config in apps.get_app_configs()
        if (
            hasattr(app_config.module, 'plugin_meta')
            and hasattr(app_config.module.plugin_meta, 'connect_plugin')
            and callable(app_config.module.plugin_meta.connect_plugin)
        )
    )


def init_plugin(package, settings=None, config=None):
    """Инициализация плагина.

    Для инициализации плагина импортируется модуль ``plugin_meta`` из пакета,
    указанного в :arg:`package`. Затем из этого пакета вызывается функция
    ``plugin_connect``.

    :param str package: имя пакета с плагином.
    :param dict settings: переменные модуля settings системы.
    :param dict config: параметры плагина, указанные в файле конфигурации.

    :raises django.core.exceptions.ImproperlyConfigured: если указанный пакет
        не является плагином (не импортируется, либо не содержит модуля
        plugin_meta``, либо в этом модуле нет функции ``connect_plugin``).
    """
    try:
        meta_module = __import__(
            '.'.join((package, 'plugin_meta')),  # module name
            {},  # globals
            {},  # locals
            ['connect_plugin'],  # from list
            0,  # absolute import
        )
    except ImportError:
        raise ImproperlyConfigured('{} is not plugin application.'.format(package))

    meta_module.__package__ = package

    if not hasattr(meta_module, 'connect_plugin') or not callable(meta_module.connect_plugin):
        raise ImproperlyConfigured(
            '{} is not a plugin application (module {} has not connect_plugin function)'.format(package, meta_module)
        )
    meta_module.connect_plugin(settings, config or {})
