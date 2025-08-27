import os

from abc import (
    ABCMeta,
    abstractmethod,
)

from django.conf import (
    settings,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    BooleanField,
    DateField,
    DateTimeField,
    FileField,
    FloatField,
    IntegerField,
    TimeField,
)
from django.db.models.fields.related import (
    RelatedField,
)
from django.utils.dateparse import (
    parse_date,
    parse_datetime,
    parse_time,
)
from django.utils.encoding import (
    force_str,
)

from m3_django_compat import (
    get_related,
)

from educommon.audit_log.models import (
    AuditLog,
)


class LogProxyMeta(type(AuditLog), ABCMeta):
    """Метакласс для устранения конфликта при наследовании от AuditLog и использовании ABCMeta"""


class LogProxy(AuditLog, metaclass=LogProxyMeta):
    """Абстрактный класс прокси-модели для отображения."""

    class Meta:
        proxy = True

    @property
    def user_name(self):
        """Отображаемое имя пользователя."""
        user_type_id = self.user_type_id
        user_id = self.user_id
        if user_type_id is not None and user_id is not None:
            try:
                model = ContentType.objects.get(id=user_type_id).model_class()
            except ContentType.DoesNotExist:
                result = 'Model:{}, id:{}'.format(user_type_id, user_id)
            else:
                result = self.user_fullname or f'{model._meta.verbose_name}({user_id})'
        else:
            result = ''

        return result

    @property
    @abstractmethod
    def user_fullname(self) -> str:
        """Полное имя пользователя."""

    @property
    @abstractmethod
    def user_organization(self) -> str:
        """Название организации, к которой привязан пользователь."""

    @property
    def model_fullname(self):
        """Отображаемое и системное имя модели."""
        model = self.model
        if model:
            return '{} - {}'.format(model._meta.verbose_name, model.__name__)
        return self.table.name

    @property
    def model_name(self):
        """Отображаемое имя модели."""
        model = self.model

        if model:
            verbose = model._meta.verbose_name
            if verbose:
                return ' - '.join((force_str(verbose), model.__name__))
            return model.__name__
        return self.table.name

    @property
    def diff(self):
        """Возвращает diff для объекта.

        :return: list[dict]: Словари, с ключами "name", "old", "new", где:
            "name" - verbose_name поля модели, если удалось определить,
                     иначе его имя,
            "old" и "new" - старое и новое значение поля соответственно.
        """
        empty = {}

        if self.operation == self.OPERATION_CREATE:
            keys = self.data.keys()
            data = empty
            new_data = self.data or empty
        elif self.operation == self.OPERATION_UPDATE:
            keys = self.changes.keys()
            data = self.data or empty
            new_data = self.changes or empty
        elif self.operation == self.OPERATION_DELETE:
            keys = self.data.keys()
            data = self.data or empty
            new_data = empty
        else:
            keys = data = new_data = empty

        result = [
            {
                'name': self.get_field_string(key),
                'old': self.convert_field_value(key, data.get(key, '')),
                'new': self.convert_field_value(key, new_data.get(key, '')),
            }
            for key in keys
        ]
        result.sort(key=lambda x: x['name'])

        return result

    def get_field_string(self, column_name):
        """Возвращает отображаемое имя поля модели.

        :param str column_name: имя столбца в БД.
        :return str: verbose_name столбца, если есть, иначе column_name.
        """
        name = column_name
        if self.fields:
            field = self.fields.get(column_name)
            if field and field.verbose_name:
                name = force_str(field.verbose_name)

        return name

    def convert_field_value(self, column_name, value):
        """Возвращает значение поля."""

        def get_choice(choices, choice_id):
            if choice_id:
                choice_id = int(choice_id)
            return dict(choices).get(choice_id, choice_id)

        if value is None:
            return ''

        if self.fields:
            field = self.fields.get(column_name)
            if field:
                try:
                    if isinstance(field, RelatedField):
                        if value:
                            related = get_related(field)
                            model = related.parent_model
                            field_name = related.relation.field_name
                            qs = model._default_manager.filter(**{field_name: value})[:1]
                            if qs:
                                value = '{{{}}} {}'.format(
                                    qs[0].id,
                                    self._get_object_verbose_name(qs[0]),
                                )
                    elif isinstance(field, BooleanField):
                        value_map = {'t': 'Да', 'f': 'Нет'}
                        value = value_map.get(value, value)
                    elif isinstance(field, IntegerField) and field.choices:
                        value = get_choice(field.choices, value)
                except (ValueError, TypeError):
                    pass
        return force_str(value)

    @property
    def object_string(self) -> str:
        """Отображаемое имя экземпляра модели."""
        instance = self.instance
        if instance:
            return self._get_object_verbose_name(instance)
        return self._get_removed_object_verbose_name()

    @property
    def instance(self):
        """Восстановленный экземпляр модели."""
        result = None

        if self.model:
            result = self.model()
            fields_dict = {field.name: field for field in self.model._meta.fields}
            for key, value in self.data.items():
                field = fields_dict.get(key)
                converted_value = value
                if field:
                    try:
                        if isinstance(field, DateTimeField):
                            converted_value = parse_datetime(value)
                        elif isinstance(field, DateField):
                            converted_value = parse_date(value)
                        elif isinstance(field, TimeField):
                            converted_value = parse_time(value)
                        elif isinstance(field, IntegerField):
                            converted_value = int(value)
                        elif isinstance(field, FloatField):
                            converted_value = float(value)
                        elif isinstance(field, FileField):
                            file_path = os.path.join(settings.MEDIA_ROOT, converted_value)
                            if not os.path.exists(file_path):
                                converted_value = None
                    except (ValueError, TypeError):
                        pass
                setattr(result, key, converted_value)

        return result

    @staticmethod
    def _get_object_verbose_name(instance):
        """Возвращает отображаемое значение в str для инстанса модели."""
        # pylint: disable=broad-except

        if hasattr(instance, 'log_display'):
            try:
                return instance.log_display()
            except Exception:
                pass
        elif hasattr(instance, 'display'):
            try:
                return instance.display()
            except Exception:
                pass
        return str(instance)

    def _get_removed_object_verbose_name(self):
        """Возвращает отображаемое значение в str для инстанса модели."""
        attrs = ('name', 'fullname', 'full_name', 'code', 'id')
        for attr in attrs:
            if attr in self.data:
                return self.data[attr]
        return ''
