from m3.db import (
    safe_delete,
)
from m3_django_compat import (
    atomic,
    get_model,
)

from educommon.m3.extensions.listeners.delete_check.signals import (
    post_cascade,
    pre_cascade,
)
from educommon.m3.extensions.listeners.delete_check.utils import (
    get_related_instances_and_handlers,
)


class CascadeDeletePackMixin:
    """Mixin определяющий исключаемые поля модели при проверке DeleteCheck.

    Поскольку DeleteCheck срабатывает до вызова delete_row возникают ситуации,
    когда нам требуется при работе с этим паком исключить определенные
    поля модели, из которых имеются ссылки на модель. Для решения данных
    ситуаций используется атрибут cascade_delete_objects.

    .. code-block:: python

        cascade_delete_objects = (('parent', 'parentportfolio', 'person'),)
    """

    # содержит кортежи формата
    # (имя приложения, имя модели приложения, имя поля)
    cascade_delete_objects = ()

    def _cascade_delete(self, obj_id, request, context):
        """Удаляет связанные объекты, указанные в cascade_delete_objects."""
        for app_label, model_name, field_name in self.__class__.cascade_delete_objects:
            model = get_model(app_label, model_name)
            lookup = {f'{field_name}_id': obj_id}
            for obj in model.objects.filter(**lookup):
                if hasattr(obj, 'safe_delete') and callable(obj.safe_delete):
                    obj.safe_delete()
                else:
                    safe_delete(obj)

    @classmethod
    def skip_field(cls, field):
        """Определяет, следует ли исключить поле из проверки DeleteCheck."""
        if cls.cascade_delete_objects:
            for app_label, model_name, field_name in cls.cascade_delete_objects:
                model = get_model(app_label, model_name)
                if field.name == field_name and field.model == model:
                    return True

        return False

    @atomic
    def delete_row(self, obj_id, request, context):
        self._cascade_delete(obj_id, request, context)

        return super().delete_row(obj_id, request, context)


class CascadeDeleteMixin:
    """Определяет связи, исключаемые при проверке в ``DeleteCheck``.

    Перед удалением объекта модели обеспечивает удаление или изменение
    зависимых от него объектов, если настройки зависимых объектов
    (``cascade_delete_for``) позволяют это делать.

    (``cascade_delete_for``) может быть как кортежем с перечислением полей,
    так и словарем, ключем в котором выступает поле, а значением словарь с
    дополнительными параметрами. В случае, если среди дополнительных параметров
    указан ``on_delete`` то вызыватся будет именно он, а не поведение, которое
    указано в атрибуте ``on_delete`` поля.

    .. code-block:: python
       :caption: Пример использования

       class ModelA(CascadeDeleteMixin, models.Model):
           field = models.TextField()


       class ModelB(models.Model):
           link = models.ForeignKey(ModelA)
           cascade_delete_for = (link,)


       class ModelC(models.Model):
           link = models.ForeignKey(ModelA, on_delete=models.SET_NULL)
           cascade_delete_for = (link,)


       def some_func(obj):
           obj.link = ModelA()
           obj.link.save()
           obj.save()
           # В случае, если ModelA и ModelD наследуются от ModelValidationMixin
           # то вместо вызова `save` должен быть метод `clean_and_save`


       class ModelD(models.Model):
           link = models.ForeignKey(ModelA, on_delete=models.SET_NULL)
           cascade_delete_for = {link: {'on_delete': some_func}}

    При удалении объектов модели ModelA с помощью метода ``safe_delete()``
    произойдет следующее:

    - Связанные с ними объекты модели ``ModelB`` также будут удалены. Это
    поведение по-умолчанию, т.к. если не указвать атрибут ``on_delete`` для
    поля, то он по умолчанию будет равен ``CASCADE``, что подразумевает
    удаление связанных объектов.

    - У всех связанных объектов из модели ``ModelС`` значение поля ``link``
    будет изменено на None, т.к. такое поведение указано в ``on_delete`` поля.

    - Все связанные объекты из модели ``ModelD`` станут ссылатся на другие
    (новые) объеты из модели ``ModelA``. Произойдет это потому что в
    ``cascade_delete_for`` для поля ``link`` выставлен опциональный параметр
    ``on_delete``, в котором содержится функция, вызываемая при удалении
    связанного объекта. Данная функция имеет больший приоритет чем поведение
    указанное в ``on_delete`` поля (SET_NULL).

    .. code-block:: python
        :caption: Пример использования сингала pre_cascade

        class ModelA(CascadeDeleteMixin, models.Model):
            field = models.TextField()


        class ModelB(ReadOnlyMixin, models.Model):
            # Объекты изменяются только при изменениях, вызванных в
            # обработчиках сигналов на моделях-источниках
            _changed_from_signal = False

            def is_read_only(self):
                # Изменение доступно только из подписки на
                # изменения в источниках.
                return not self._changed_from_signal and self.id

            link = models.ForeignKey(ModelA)


        @receiver(pre_cascade, sender=ModelB)
        def pre_cascade_delete(instance, **_):
            # Каскадное удаление по умолчанию удаление по сигналу.
            instance._changed_from_signal = True
    """

    @staticmethod
    def skip_field(field):
        """Проверяет, включено ли поле в каскадное удаление."""
        cascade_delete_for = getattr(field.model, 'cascade_delete_for', ())
        if isinstance(cascade_delete_for, dict):
            cascade_delete_for = tuple(cascade_delete_for.keys())

        return field in cascade_delete_for

    @atomic
    def safe_delete(self):
        """Выполнение действий над связанными объектами перед удалением."""
        for obj, handler in get_related_instances_and_handlers(
            self, skip_func=lambda field: not self.skip_field(field)
        ):
            params = dict(sender=self._meta.model, instance=obj, initiator=self)
            pre_cascade.send(**params)
            handler(obj)
            post_cascade.send(**params)

        return super().safe_delete()
