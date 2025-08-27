"""Шаблон для построения отчётной системы.

Представляет собой набор абстрактных базовых и вспомогательных классов для
различных элементов отчётной подсистемы: провайдера данных, построителя отчёта
и собственно отчёта.
"""

from abc import (
    ABCMeta,
    abstractmethod,
)
from collections import (
    Mapping,
)


class AbstractDataProvider(metaclass=ABCMeta):
    """Абстрактный класс провайдера данных.

    Данный класс является базовым для всех классов, реализующих функционал
    провайдера данных. Идеология провайдера данных следующая:
        - провайдер обеспечивает доступ к данным через свойства
          (которые могут быть кешированы через декоратор @cached_property),
        - все кастомные артибуты класса, которые могут быть вызваны извне,
          при обращению к экземпляру провайдера для извлечения данных - не
          должны иметь входных параметров и желательно, должны быть объявлены
          как свойства. Кастомные атрибуты (в т.ч. методы с параметрами)
          "для внутреннего использования" должны быть приватными.
        - все необходимые исходные данные для извлечения данных, настройки
          представления и пр. - должны задаваться не в конструкторе провайдера,
          а в методе init, через словарь именованных аргументов **params,
        - провайдер должен иметь возможность вызываться отдельно, вне
          веб-интерфейса, например из Manage-команды или через Django-shell
        - провайдер не должен позволять изменять свои данные иным способом,
          кроме как последовательным вызовом методов init() и load_data().
    """

    # Имя провайдера, используемое в композитном провайдере
    provider_name = None

    def init(self, **params):
        """Инициализация провайдера.

        Используется вместо конструктора.
        """

    def load_data(self):
        """Загрузка данных.

        Данный метод может быть описан и использоваться для подготовки
        данных или реализации каких-либо необходимых общих расчётов.
        Метод не должен иметь никаких входных параметров.
        """

    @property
    def name(self):
        """Имя провайдера для применения в композитном провайдере."""
        if self.provider_name is not None:
            return self.provider_name
        else:
            return self.__class__.__name__


class CompositeDataProvider(AbstractDataProvider):
    """Композитный провайдер данных.

    Используется для объединения нескольких провайдеров в один.
    """

    def __init__(self, provider_classes):
        """Конструктор композитного провайдера.

        Здесь инстанцируются все подпровайдеры.

        :param provider_classes: список классов провайдеров
        """
        # словарь экземпляров провайдеров
        self.providers = {}

        for provider_class in provider_classes:
            if isinstance(provider_class, CompositeDataProvider):
                # пришёл инстанс композитного провайдера, такое может быть
                self.providers[provider_class.name] = provider_class
            else:
                # пришёл просто класс провайдера
                _provider = provider_class()
                self.providers[_provider.name] = _provider

    def init(self, **params):
        """Здесь инициализируются все подпровайдеры."""
        for provider in self.providers.values():
            if hasattr(provider, 'init'):
                provider.init(**params)

    def load_data(self):
        """Загрузка данных во всех подпровайдерах."""
        for provider in self.providers.values():
            if hasattr(provider, 'load_data'):
                provider.load_data()


class DependentCompositeProvider(AbstractDataProvider):
    """
    Композитный провайдер с описанием подпровайдеров, порядка их загрузки.

    'Прокидывает' данные между подпровайдерами в процессе загрузки данных
    """

    providers_order = None
    """
    Описание провайдеров в порядке их загрузки.
    Следует использовать "_" перед коротким именем провайдера,
    чтобы эти аттрибуты не уходили в адаптер

    ..code::

        providers_order = (
            ('_provider_name', ProviderClass),
            ('_provider_name2', ProviderClass2),
            ('_provider_name3', ProviderClass3),
        )
    """
    _dependence_map = None
    """
    Описание карты дополнительных данных (между подпровайдерами).
    См. метод _extend_provider_data

    ..code::

        _dependence_map = {
            '_provider_name': {
                # доп. аттрибут, который присвоится провайдеру provider_name
                'additional_provider_attribute': (
                    # у кого взять
                    _dependent_provider_name,
                    # что взять
                    dependent_provider_attribute
                ),
            }
        }
    """

    # словарь экземпляров провайдеров для поддержки работы с адаптерами
    providers = None

    def __init__(self):
        self.providers = {}
        self._providers = []
        self._state = {}
        for shortname, provider_class in self.providers_order:
            provider = provider_class()
            self._set_provider_to_loader(provider, shortname)
            # для поддержки работы с адаптерами
            self.providers[provider.name] = provider

    def _set_provider_to_loader(self, provider, shortname):
        """
        Установка зависимого подпровайдера в список для загрузки.

        :param provider: провайдер данных, наследник AbstractDataProvider
        :param str shortname: ключ из словаря self._dependence
        """
        provider._shortname = shortname
        self._providers.append(provider)
        setattr(self, shortname, provider)

    def init(self, **params):
        """Инициализация подпровайдеров."""
        for provider in self._providers:
            if hasattr(provider, 'init'):
                provider.init(**params)

    def load_data(self):
        """Загрузка данных во всех подпровайдерах."""
        for provider in self._providers:
            if hasattr(provider, 'load_data'):
                self._extend_provider_data(provider)
                provider.load_data()

    def _extend_provider_data(self, provider):
        """
        Дополнение данных провайдера данными предыдущих загруженных провайдеров
        согласно карте зависимостей self._dependence_map

        :type provider: AbstractDataProvider
        :param provider: провайдер данных, наследник AbstractDataProvider
        """
        # дополнение параметров результатами предыдущих провайдеров
        additional = self._dependence_map.get(provider._shortname, {})
        for param, (dependent_provider_name, att) in additional.items():
            dependent_provider = getattr(self, dependent_provider_name)
            setattr(provider, param, getattr(dependent_provider, att))


class AbstractReportBuilder(metaclass=ABCMeta):
    """Абстрактный класс построителя отчётов.

    Имеет обязательный атрибут build(), вызов которого производит
    непосредственную генерацию отчёта.
    Принимает данные от провайдера "как есть", через его свойства или целиком
    через специальный адаптер.
    """

    def __init__(self, provider=None, adapter=None, *args, **kwargs):
        """Конструктор класса билдера.

        :param provider: Провайдер данных.
        :param adapter: Адаптер для извлечения данных из провайдера.
        """

    @abstractmethod
    def build(self):
        """Метод, осуществляющий построение отчёта.

        Должен возвращать результат в виде файла или иной структуры данных.
        """


class BaseProviderAdapter(Mapping, dict):
    """Базовый класс для адаптеров, извлекающих данные из провайдера."""

    # список атрибутов провайдера, которые не должны быть "видны" через адаптер
    _attrs_stop_list = (
        'init',
        'load_data',
        'name',
        'provider_name',
        'providers',
    )

    def __init__(self, provider):
        """Конструктор адаптера.

        :param provider: провайдер данных
        """
        assert isinstance(provider, AbstractDataProvider), type(provider)
        self.provider = provider
        self._cache = {}

    def _check_provider_attr(self, attr):
        """Проверка атрибута - можно ли его брать из провайдера.

        'Магические' и некоторые отдельные методы будут игнорироваться.
        """
        return not (attr.startswith('_') or attr in self._attrs_stop_list)


class FlatDataProviderAdapter(BaseProviderAdapter):
    """Данные провайдера в 'плоском' виде.

    Класс адаптера, получающего все данные из провайдера и представляющего их
    в "плоском" виде (словарь с единичной глубиной):
        {
            'MainDataProvider__Provider01__param01': 16,
            'MainDataProvider__Provider01__param02': 54,
            'MainDataProvider__Provider01__param03': 80
        }
    Обращение к такому адаптеру - как и к обычному словарю, через "[]",
    """

    def __init__(self, provider, splitter):
        """Конструктор адаптера.

        :param provider: провайдер данных
        :param splitter: строка-разделитель.
        """
        assert isinstance(splitter, str), type(splitter)

        super().__init__(provider)

        self.level_splitter = splitter
        self._all_keys = self._get_all_keys(self.provider)

    def _get_all_keys(self, provider, key_level=None):
        """Все ключи в иерархии провайдеров."""
        result = []
        if key_level is None:
            key_level = ''
        else:
            if key_level:
                key_level += self.level_splitter + provider.name
            else:
                key_level = provider.name

        for attr_name in dir(provider):
            # цикл по всем атрибутам провайдера
            if not self._check_provider_attr(attr_name):
                continue

            if key_level:
                key = self.level_splitter.join([key_level, attr_name])
            else:
                key = attr_name

            result.append(key)

        if hasattr(provider, 'providers'):
            # если есть вложенные провайдеры
            for p in provider.providers.values():
                result.extend(self._get_all_keys(p, key_level))

        return result

    def __getitem__(self, item):
        """Поиск элемента с ключом item в словаре данных адаптера."""
        if not isinstance(item, str):
            raise KeyError(item)
        if item not in self._all_keys:
            raise KeyError(item)
        key_parts = item.split(self.level_splitter)
        # указатель на объект, где будет искаться атрибут
        obj = self.provider
        for part in key_parts[:-1]:
            # цикл по вложенным провайдерам
            provider = obj.providers.get(part)
            if provider:
                obj = obj.providers[provider.name]
            else:
                raise KeyError(item)
        # самый последний элемент - это уже должен быть атрибут, а не провайдер
        attr = getattr(obj, key_parts[-1])
        if callable(attr):
            # метод, свойство
            value = attr()
        else:
            # атрибут
            value = attr

        return value

    def __len__(self):
        """Магический метод для поддержки операции len()."""
        return len(self._all_keys)

    def __bool__(self):
        return bool(self._all_keys)

    __nonzero__ = __bool__

    def __iter__(self):
        return iter(self._all_keys)


class NestedDataProviderAdapter(BaseProviderAdapter):
    """Данные провайдера в 'иерархическом' (вложенные словари) виде.

    Класс адаптера, получающего все данные провайдера и представляющего их
    в виде вложенных словарей:
        {
            'MainDataProvider': {
                'Provider01': {
                    'param01': 16,
                    'param02': 54,
                    'param03': 80
                }
            }
        }
    Обращение к такому адаптеру - как и к обычному словарю, через "[]".
    """

    def __init__(self, provider):
        """Конструктор адаптера.

        :param provider: провайдер данных
        """
        super().__init__(provider)

        self._all_keys = self._get_top_keys(self.provider)

    def _get_top_keys(self, provider):
        """все необходимые атрибуты адаптируемого провайдера."""
        result = []
        for attr_name in dir(provider):
            # цикл по всем атрибутам провайдера
            if not self._check_provider_attr(attr_name):
                continue
            result.append(attr_name)

        if hasattr(provider, 'providers'):
            # если есть вложенные провайдеры
            for p in provider.providers.values():
                result.append(p.name)

        return result

    def __getitem__(self, item):
        """Поиск элемента с ключом item в словаре данных адаптера."""
        if not isinstance(item, str):
            raise KeyError(item)
        if not self._check_provider_attr(item):
            raise KeyError(item)
        if hasattr(self.provider, item):
            attr = getattr(self.provider, item)
            if callable(attr):
                value = attr()
            else:
                value = attr
            return value

        # поиск по имени провайдера
        provider = self.provider.providers.get(item)
        if provider:
            provider_key = provider.__class__.__name__
            if provider_key not in self._cache:
                self._cache[provider_key] = NestedDataProviderAdapter(provider)
            return self._cache[provider_key]
        else:
            raise KeyError(item)

    def __len__(self):
        """Магический метод для поддержки операции len()."""
        return len(self._all_keys)

    def __bool__(self):
        return bool(self._all_keys)

    __nonzero__ = __bool__

    def __iter__(self):
        return iter(self._all_keys)
