from abc import (
    ABCMeta,
    abstractmethod,
)

from educommon.utils.registry import (
    ModelHandlerRegistry,
)


class AbstractInstanceStorage(metaclass=ABCMeta):
    @abstractmethod
    def save(self, instance, **kwargs):
        """Сохранение данных для объекта модели."""


class AbstractInstanceDataStorage(AbstractInstanceStorage):
    """Абстрактный класс для сохранения данных объекта модели.

    Сохранение данных объекта происходит, если для модели определена
    функция-обработчик (вызываемый объект) в соответствующем реестре.
    Обработчики должны возвращать данные, которые нужно сохранить для
    объекта модели. В методе _save_instance_data должна быть реализована
    логика для сохранения полученных данных в БД.
    Основным методом для вызова является save.
    """

    def __init__(self, registry):
        """
        :param registry: Реестр моделей и их обработчиков
        :type registry: ModelHandlerRegistry
        """
        assert isinstance(registry, ModelHandlerRegistry)
        self.registry = registry

    def _get_instance_data(self, instance):
        """Возвращает данные, которые нужно сохранить для объекта модели.

        :param instance: Объект модели

        :return: Результат вызова обработчика для данной модели
        :rtype: Any
        """
        handler = self.registry.get_model_handler(instance.__class__)
        if not handler:
            return
        object_data = handler(instance)
        return object_data

    def _is_instance_already_saved(self, instance, **kwargs):
        """Возвращает признак, что данные объекта уже сохранены.

        :param instance: Объект модели

        :rtype: bool
        """
        return False

    @abstractmethod
    def _save_instance_data(self, instance, **kwargs):
        """Фиксирует данные объекта в базе данных.

        :param instance: Объект модели
        """

    def save(self, instance, **kwargs):
        """Сохранение данных объекта (в общем виде).

        :param instance: Объект модели
        """
        if not self.registry.is_model_has_handler(instance.__class__) or self._is_instance_already_saved(
            instance, **kwargs
        ):
            return

        self._save_instance_data(instance)
