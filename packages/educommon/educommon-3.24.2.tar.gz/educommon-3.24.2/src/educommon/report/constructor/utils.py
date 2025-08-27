from collections import (
    OrderedDict,
)
from inspect import (
    isclass,
)

from django.db.models.fields import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    IntegerField,
    NullBooleanField,
    TextField,
    TimeField,
)
from django.db.models.fields.related import (
    ForeignKey,
)
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
)

from m3_django_compat import (
    get_related,
)
from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)

from educommon.report.constructor.constants import (
    CT_BOOLEAN,
    CT_CHOICES,
    CT_DATE,
    CT_DATETIME,
    CT_DIRECT_RELATION,
    CT_NULL_BOOLEAN,
    CT_NUMBER,
    CT_OTHER,
    CT_REVERSE_RELATION,
    CT_TEXT,
    CT_TIME,
)


def get_field(model, name):
    """Возвращает поле с именем :arg:`name` модели :arg:`model`.

    Для обратных зависимостей в :arg:`name` нужно указывать имя атрибута
    объекта модели (см. :attr:`~django.db.models.ForeignKey.related_name`).

    :rtype: django.db.models.fields.Field or
        django.db.models.fields.related.RelatedField
    """
    # Поиск среди реальных полей модели.
    for field in getattr(model, '_meta').get_fields():
        if isinstance(field, ForeignObjectRel):
            field_name = field.get_accessor_name()
        else:
            field_name = field.name

        if name == field_name:
            return field

    # Поиск среди дополнительных полей модели.
    extra = getattr(model, 'report_constructor_params', {}).get('extra', {})
    for accessor_name, params in extra.items():
        if name == accessor_name:
            from educommon.report.constructor.base import (
                ExtraField,
            )

            field = params['field']
            field.model = model if isclass(model) else model.__class__
            field.name = name
            return ExtraField(accessor_name, field)

    raise FieldDoesNotExist(name)


def get_nested_field(model, field_name):
    """Возвращает поле модели с учетом вложенности связей.

    Например, такой вызов вернет поле ``surname`` модели ``Person``, на которую
    есть внешний ключ из модели ``Employee`` через поле ``person``.

    .. code-block:: python

       >>> get_nested_field(Employee, 'person.surname')

    :rtype: django.db.models.fields.Field or
        django.db.models.fields.related.RelatedField
    """
    attr_name, _, nested_attr = field_name.partition('.')

    try:
        attr_value = model._meta.get_field(attr_name)
    except FieldDoesNotExist:
        # если это не поле, то возможно это обратная связь
        for field in model._meta.get_fields():
            if field.one_to_many and attr_name == field.get_accessor_name():
                if nested_attr:
                    attr_value = field.related_model
                else:
                    attr_value = field
                break
        else:
            raise

    if nested_attr:
        if isinstance(attr_value, ForeignKey):
            attr_value = get_related(attr_value).parent_model

        try:
            return get_nested_field(attr_value, nested_attr)
        except FieldDoesNotExist:
            raise FieldDoesNotExist("{} has not field named '{}'".format(model.__name__, field_name))
    else:
        return attr_value


def get_columns_hierarchy(*columns):
    """Формирует иерахию полей по списку колонок.

    .. code-block:: python

       >>> get_columns_hierarchy('person.surname', 'person.firstname')
       {
           'person': {
               'surname': {},
               'firstname': {},
           }
       }

    :param columns: список строк с именами полей

    :rtype: collections.OrderedDict
    """

    result = OrderedDict()
    for column in columns:
        nodes = result
        for level_name in column.split('.'):
            if level_name not in nodes:
                nodes[level_name] = OrderedDict()
            nodes = nodes[level_name]

    return result


def get_field_value_by_display(field, display_value):
    """Возвращает значение поля с вариантами, соответствующее представлению.

    :param field: Поле модели.
    :type field: django.db.models.fields.Field

    :param display_value: Текстовое представление, соответствующее искомому
        значению поля.
    :type display_value: unicode

    :raises ValueError: если поле ``field`` не содержит вариантов допустимых
        значений, либо значения ``display_value`` нет среди допустимых
        вариантов.
    """
    if not field.choices:
        raise ValueError('Поле не содержит варианты выбора.')

    for value, display in field.choices:
        if display.lower() == display_value.lower():
            return value

    raise ValueError('Значения "{}" нет среди вариантов выбора.'.format(display_value))


def get_data_type(field):
    """Возвращает тип данных поля.

    :param field: поле модели.
    :type field: django.db.models.fields.Field

    :rtype: str
    """
    if field.concrete and field.choices:
        result = CT_CHOICES
    else:
        types_map = (
            (BooleanField, CT_BOOLEAN),
            (NullBooleanField, CT_NULL_BOOLEAN),
            (IntegerField, CT_NUMBER),
            (FloatField, CT_NUMBER),
            (DecimalField, CT_NUMBER),
            (CharField, CT_TEXT),
            (TextField, CT_TEXT),
            (DateField, CT_DATE),
            (TimeField, CT_TIME),
            (DateTimeField, CT_DATETIME),
            (ForeignKey, CT_DIRECT_RELATION),
            (ForeignObjectRel, CT_REVERSE_RELATION),
        )
        for field_base_class, column_type in types_map:
            if isinstance(field, field_base_class):
                result = column_type
                break
        else:
            result = CT_OTHER

    return result
