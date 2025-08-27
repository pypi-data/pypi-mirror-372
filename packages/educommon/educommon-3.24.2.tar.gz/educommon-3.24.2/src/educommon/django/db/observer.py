from weakref import (
    WeakValueDictionary,
)

from django.db.models.base import (
    Model,
)
from django.db.models.signals import (
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)

from educommon.utils import (
    SingletonMeta,
)


class ModelObserverBase(metaclass=SingletonMeta):
    """Базовый класс для наблюдателей за моделями.

    Предоставляет возможность реализовывать реакцию на изменение и удаление
    объектов моделей.

    В отличие от сигналов Django позволяет более гибко определять перечень
    наблюдаемых моделей, например указывать базовый класс модели (см. метод
    ``_is_observable()``).

    Классы-потомки могут реализовывать реакцию на изменение и/или удаление
    объектов в методах ``pre_save``, ``post_save``, pre_delete`` и
    ``post_delete`` (все методы реализовывать не обязательно). Метод
    ``_create_context()`` определяет содержимое контекста, передаваемого в эти
    методы.

    Пример реализации наблюдателя, выводящего в консоль информацию об
    изменениях в наблюдаемых моделях.

    .. code-block:: python

       class ModelLogger(ModelObserverBase):
           def _is_observable(self, model):
               return model  in self._observables

           def _create_context(self, instance):
               result = super()._create_context(
                   instance
               )

               if instance.pk:
                   result.original = None
               else:
                   model = instance.__class__
                   result.original = model.objects.get(pk=instance.pk)

               return result

           def post_save(self, instance, context, **kwargs):
               print '{}{{{}}}'.format(instance.__class__.__name__,
                                       instance.pk)

               for field in instance._meta.concrete_fields:
                   old_value = getattr(context.original, field.attname)
                   new_value = getattr(instance, field.attname)
                   if old_value != new_value:
                       print '\t{}: {} --> {}'.format(
                           field.name, old_value, new_value
                       )

    .. seealso::

       * :class:`~educommon.django.db.observer.ModelOnlyObserverMixin`
       * :class:`~educommon.django.db.observer.ModelDescendantsObserverMixin`
       * :class:`~educommon.django.db.observer.OriginalObjectMixin`
    """

    class Context:
        """Класс-контейнер для контекста наблюдателя.

        Предназначен для хранения дополнительных объектов, связанных с
        наблюдаемым объектом. Например, в нем можно хранить объект модели в
        состоянии *до* изменения.

        .. caution:

           Для хранения объектов контекста в наблюдателе используются слабые
           ссылки, поэтому для корректной работы нельзя допускать хранение
           наблюдаемого объекта в контексте, т.к. это заблокирует его
           уничтожение сборщиком мусора.
        """

    def _create_context(self, instance):
        """Возвращает контекст для экземпляра модели.

        :param instance: Объект (экземпляр) наблюдаемой модели.

        :rtype: ModelObserverBase.Context
        """
        context = self.Context()
        self._contexts[context] = instance

        return context

    def _get_context(self, instance):
        """Возвращает объект контекста, соответствующий экземпляру модели.

        В случае, если для указанного экземпляра модели контекст еще не
        создавался, то он создается и добавляется в хранилище.

        :rtype: :class:`ModelObserverBase.Context` or None.
        """
        for context, obj in self._contexts.items():
            if id(instance) == id(obj) and instance.__class__ is obj.__class__:
                return context

        return self._create_context(instance)

    def _remove_context(self, instance):
        """Удаляет из хранилища контекст для указанного экземпляра модели."""
        for context, obj in self._contexts.items():
            if id(instance) == id(obj) and instance.__class__ is obj.__class__:
                del self._contexts[context]
                break

    def __init__(self):
        # модели, за которыми осуществляется наблюдение
        self._observables = set()

        # хранилище контекстов
        self._contexts = WeakValueDictionary()
        # ---------------------------------------------------------------------
        # Подключение к сигналам

        def wrapper(handler):
            def inner(instance, sender, **kwargs):
                if handler.__self__._is_observable(sender):
                    handler(instance=instance, sender=sender, **kwargs)

            return inner

        pre_save.connect(wrapper(self.__pre_save_handler), weak=False)
        post_save.connect(wrapper(self.__post_save_handler), weak=False)
        pre_delete.connect(wrapper(self.__pre_delete_handler), weak=False)
        post_delete.connect(wrapper(self.__post_delete_handler), weak=False)
        # ---------------------------------------------------------------------

    def observe(self, model):
        """Включает наблюдение за указанной моделью.

        В случае, если указанная модель является абстрактной, то наблюдение
        будет выполняться за всеми моделями, являющимися потомками указанной
        модели.

        :param model: Класс наблюдаемой модели.
        """
        assert model is Model or issubclass(model, Model), type(model)

        self._observables.add(model)

    def _is_observable(self, model):
        """Возвращает ``True``, если модель находится под наблюдением.

        :rtype: bool
        """
        raise NotImplementedError()

    def __pre_save_handler(self, instance, **kwargs):
        # Если в наблюдателе есть методы для обработки save-сигналов, то
        # для них создается контекст.
        if hasattr(self, 'pre_save') or hasattr(self, 'post_save'):
            context = self._get_context(instance)

        if hasattr(self, 'pre_save'):
            self.pre_save(instance=instance, context=context, **kwargs)

    def __post_save_handler(self, instance, **kwargs):
        if hasattr(self, 'post_save'):
            self.post_save(instance=instance, context=self._get_context(instance), **kwargs)

        self._remove_context(instance)

    def __pre_delete_handler(self, instance, **kwargs):
        # Если в наблюдателе есть методы для обработки delete-сигналов, то
        # для них создается контекст.
        if hasattr(self, 'pre_delete') or hasattr(self, 'post_delete'):
            context = self._get_context(instance)

        if hasattr(self, 'pre_delete'):
            self.pre_delete(instance=instance, context=context, **kwargs)

    def __post_delete_handler(self, instance, **kwargs):
        if hasattr(self, 'post_delete'):
            self.post_delete(instance=instance, context=self._get_context(instance), **kwargs)

        self._remove_context(instance)


class ModelOnlyObserverMixin:
    """Класс-примесь для наблюдения только за указанными моделями."""

    def _is_observable(self, model):
        return model in self._observables


class ModelDescendantsObserverMixin:
    """Класс примесь для наблюдения за моделями и их потомками."""

    def _is_observable(self, model):
        return any(model is observable or issubclass(model, observable) for observable in self._observables)


class OriginalObjectMixin:
    """Класс-примесь, добавляющая в контекст наблюдателя исходный объект."""

    # Кеш исходных объектов. Используется для предотвращения повторной загрузки
    # при использовании нескольких наблюдателей.
    __cache = WeakValueDictionary()

    class _Empty:
        pass

    __empty = _Empty()

    def _create_context(self, instance):
        result = super()._create_context(instance)

        if instance.pk is None:
            result.original = None
        else:
            # В связи с тем, что в моделях переопределен метод __hash__, разные
            # экземпляры одного и того же объекта модели можно отличить только
            # с помощью функции id. Поэтому не используем в качестве ключа
            # экземпляр объекта модели.
            cache_key = (instance.__class__, id(instance))
            if cache_key not in self.__cache:
                try:
                    original = instance.__class__.objects.get(pk=instance.pk)
                except instance.__class__.DoesNotExist:
                    original = self.__empty

                self.__cache[cache_key] = original

            result.original = self.__cache[cache_key]
            if isinstance(result.original, self._Empty):
                result.original = None

        return result
