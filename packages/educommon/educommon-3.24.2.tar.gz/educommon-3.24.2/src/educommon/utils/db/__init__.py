from functools import (
    reduce,
)
from itertools import (
    groupby,
)
from operator import (
    or_,
)

from django.apps import (
    apps,
)
from django.db import (
    models,
    router,
)
from django.db.models.base import (
    Model,
)
from django.db.models.deletion import (
    Collector,
)
from django.db.models.fields.related import (
    RelatedField,
)
from django.db.models.query_utils import (
    Q,
)
from m3_django_compat import (
    get_related,
)

from objectpack.models import (
    ModelProxy,
)


def get_field(obj, field_name):
    """Возвращает поле модели c учетом внешних ключей.

    ::

      get_field(obj, 'person.user.username')

    :param basestring field_name: Имя поля.

    :rtype: django.db.model.fields.Field
    """
    name, _, nested = field_name.partition('.')
    field = obj._meta.get_field(name)
    if nested:
        assert isinstance(field, models.ForeignKey)
        return get_field(get_related(field).parent_model, nested)
    else:
        return field


def get_related_fields(model, skip_func=None):
    """Возвращает поля моделей системы, ссылающихся на указанную модель.

    :param model: Модель, для которой будут найдены все зависимые поля.
    :type model: django.db.models.base.Model

    :param skip_func: Функция исключения, в которой будет определяться
        исключаемые поля.
    :type skip_func: lambda

    :rtype: generator
    """
    assert issubclass(model, Model), model

    for related_model in apps.get_models():
        if not related_model._meta.proxy:
            for field in related_model._meta.get_fields():
                if (
                    field.concrete
                    and isinstance(field, RelatedField)
                    and issubclass(model, get_related(field).parent_model)
                    and (not skip_func or not skip_func(field))
                ):
                    yield field


def get_related_instances(obj, collapse=True, skip_func=None):
    """Возвращает связанные с ``obj`` объекты.

    :param obj: Объект, для которого будет осуществляться поиск связанных
        объектов.
    :type obj: django.db.models.base.Model

    :param bool collapse: Флаг, указывающий на необходимость "объединения"
        ссылок на объект. В тех случаях, когда в объекте модели есть несколько
        внешних ключей, ссылающихся на один и тот же объект, этот параметр
        определяет, сколько раз будет возвращен ссылающийся объект: если
        ``collapse`` равен ``True``, то ссылающийся объект будет возвращен один
        раз, а для ``False`` ссылающийся объект будет возвращен для каждого
        внешнего ключа.

    :param skip_func: Функция исключения, в которой будет определяться
        исключаемые поля.
    :type skip_func: lambda


    .. code-block:: python
       :caption: Пример использования

       >>> job = Job.objects.get(...)
       >>> list(get_related_instances(job))
       [
           <Employee: Сотрудник{Аббасова Лола Артуровна}>,
           <Employee: Сотрудник{Исакиев Игнат Васильевич}>,
           <SysAdmin: {9}>,
           <SysAdmin: {12}>,
           <SysAdmin: {14}>,
       ]
       >>> address = Address.objects.create(...)
       >>> person = Person.objects.create(act_address=address,
       ...                                reg_address=address)
       >>> list(get_related_instances(person))
       [
           <Address: {1}>,
       ]
       >>> list(get_related_instances(person, collapse=False))
       [
           <Address: {1}>,
           <Address: {1}>,
       ]

    :param obj: Объект, для котого нужно найти связанные объекты.
    :type obj: :class:`django.db.models.base.Model`

    :rtype: generator
    """

    assert isinstance(obj, Model), type(obj)
    for model, fields in groupby(get_related_fields(obj.__class__, skip_func), lambda field: field.model):
        conditions = reduce(or_, (Q(**{field.name: obj}) for field in fields))
        for related_obj in model.objects.filter(conditions).iterator():
            if collapse:
                yield related_obj
            else:
                for field in model._meta.get_fields():
                    if (
                        field.concrete
                        and isinstance(field, RelatedField)
                        and (field.related_model == obj.__class__ and getattr(related_obj, field.attname) == obj.pk)
                        and (not skip_func or not skip_func(field))
                    ):
                        yield related_obj


def get_related_instances_proxy(obj, skip_func=None):
    """Возвращает связанные объекты для обычных и proxy-моделей.

    Эта функция является оберткой над ``get_related_instances``, пример
    использования см. в ``get_related_instances``.

    :param obj: Объект, для которого будет осуществляться поиск связанных
        объектов.
    :param skip_func: Функция исключения, в которой будет определяться
        исключаемые поля.
    :return: генератор связанных объектов
    :rtype: generator
    """
    if isinstance(obj, ModelProxy):
        obj = getattr(obj, obj.model.__name__.lower())
    return get_related_instances(obj, collapse=False, skip_func=skip_func)


def get_non_block_relations(obj):
    """Возвращает неблокирующие удаление объекта ``obj`` связи.

    Функция использует Django-коллектор, может создавать значительную нагрузку
    на БД, следует применять с осторожностью.

    :param obj: Объект, для которого будет осуществляться поиск связанных
        объектов.
    :return: Словарь, ключами которого являются имена моделей, а значениями -
        кортежи связанных объектов.
    :rtype: dict
    """

    displayed_relations = dict()
    collector = Collector(using=router.db_for_write(obj.__class__, instance=obj))
    collector.collect((obj,))
    # Коллектор содержит ссылку на obj, удалим сам объект из коллектора
    collector.data[obj.__class__].remove(obj)

    for model, related_objects in collector.data.items():
        if all((getattr(model, 'display_related_error', True), related_objects)):
            key = '.'.join(
                (
                    model._meta.app_label,
                    model._meta.object_name,
                )
            )
            displayed_relations[key] = tuple(related_objects)
    return displayed_relations
