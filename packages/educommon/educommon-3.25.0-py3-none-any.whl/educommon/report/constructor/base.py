# pylint: disable=protected-access
from django.core.exceptions import (
    ValidationError,
)
from django.db import (
    models,
)
from django.db.models.fields import (
    Field,
)
from django.db.models.fields.related import (
    RelatedField,
)
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
    OneToOneRel,
)
from django.utils.encoding import (
    force_str,
)

from m3_django_compat import (
    ModelOptions,
    get_related,
)
from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)

from educommon.django.db.utils import (
    LazyModel,
)
from educommon.report.constructor import (
    constants,
)
from educommon.report.constructor.utils import (
    get_data_type,
    get_field,
)
from educommon.utils.misc import (
    cached_property,
)


def _get_accessor_name(field):
    """Возвращает название поля модели.

    :rtype: str
    """
    if isinstance(field, ForeignObjectRel):
        accessor_name = field.get_accessor_name()
    else:
        accessor_name = field.name

    return accessor_name


def field_ignored_by_model_params(model, accessor_name):
    """Возвращает True, если поле должно игнорироваться из-за настройки модели.

    Исходит из значения параметра ``model.report_constructor_params``.

    Исключаются:
        - поля указанные в ``model.report_constructor_params['except']``;
        - поля *не* указанные в ``model.report_constructor_params['only']``;
        - поля моделей, у которых ``model.report_constructor_params['skip']``
          содержит истинное значение;

    :param model: Модель в рамках которой происходит проверка.
    :type model: django.db.models.Model
    :param str accessor_name: путь, через ".", до поля от указанной модели.

    :rtype: bool
    """
    if not hasattr(model, 'report_constructor_params'):
        return False

    params = model.report_constructor_params
    assert isinstance(params, dict), params
    assert sum(1 if param in params else 0 for param in ('skip', 'except', 'only')) <= 1, (
        'Должен быть указан только один параметр.',
        model,
        params,
    )

    if 'extra' in params and accessor_name in params['extra']:
        return False

    if 'skip' in params and params['skip']:
        return True

    if 'except' in params:
        for param in params['except']:
            parts = param.split('.')
            parts_count = len(parts)
            if accessor_name.split('.')[:parts_count] == parts:
                return True

    if 'only' in params:
        parts = accessor_name.split('.')
        parts_count = len(parts)
        for param in params['only']:
            if param.split('.')[:parts_count] == parts:
                return False
            if param.split('.')[0] in parts:
                return False
        return True

    return False


def skip_field(model, field, accessor_name):
    """Возвращает True, если поле модели должно игнорироваться конструктором.

    Игнорируются:
        - поля с типами ``AutoField`` и ``FileField``;
        - поля, исключенные параметром ``model.report_constructor_params``;

    :param model: Модель в рамках которой происходит проверка.
    :type model: django.db.models.Model
    :param field: Поле для проверки, не обязательно
        принадлежит указанной модели.
    :type field: django.db.models.Field
    :param str accessor_name: путь, через ".", до поля от указанной модели.

    :rtype: bool
    """
    if isinstance(field, (models.AutoField, models.FileField)):
        return True

    return field_ignored_by_model_params(model, accessor_name)


class ColumnDescriptor:
    """Дескриптор поля модели, входящего в состав столбца отчета.

    Предназначен для извлечения из моделей необходимой информации.
    """

    def __init__(self, data_source, parent, field, level=0):
        """Инициализация экземпляра класса.

        :param data_source: Источник данных.

        :param parent: Дескриптор верхнего уровня. Определяет дескриптор для
            поля, из которого модель ссылается на поле данного дейскриптора.
        :type parent: ColumnDescriptor or None

        :param field: Поле модели, соответствующее данному дескриптору.
        :type field: Field or FakeField

        :param int level: Уровень вложенности дескриптора.
        """
        assert isinstance(parent, (ColumnDescriptor, type(None))), parent

        self.data_source = data_source
        self.parent = parent
        self.field = field
        self.level = level
        self.children = []

        if self.parent:
            self.parent.children.append(self)

    def __repr__(self, *args, **kwargs):
        return '{}<{}>'.format(self.__class__.__name__, self.full_accessor_name)

    @staticmethod
    def create(model, field_name, data_source, parent=None, level=0):
        model_params = getattr(model, 'report_constructor_params', {})
        assert sum(1 if param in model_params else 0 for param in ('skip', 'except', 'only')) <= 1, (
            'Может быть указан только один параметр.',
            model,
            model_params,
        )

        attr_name, _, nested_attr = field_name.partition('.')

        for field in getattr(model, '_meta').get_fields():
            accessor_name = _get_accessor_name(field)

            if skip_field(model, field, accessor_name):
                continue

            if isinstance(field, ForeignObjectRel):
                related_model = field.related_model
            else:
                if isinstance(field, RelatedField):
                    related_model = get_related(field).parent_model
                else:
                    related_model = None

            if accessor_name == attr_name:
                column_field = field
                break
        else:
            raise FieldDoesNotExist(field_name)

        result = ColumnDescriptor(data_source, parent, column_field, level)
        if nested_attr:
            if not related_model:
                raise FieldDoesNotExist(field_name)

            try:
                result = ColumnDescriptor.create(related_model, nested_attr, data_source, result, level + 1)
            except FieldDoesNotExist as error:
                raise FieldDoesNotExist('.'.join((attr_name, str(error))))

        return result

    def _check_to_exclude(self, field):
        """Метод проверяет необходимость игнорирования поля модели.

        Проверяется наличие поля в параметрах по всей иерархии моделей
        дескриптора, включая модель источника данных.

        :rtype bool
        """
        fld_accessor_name = _get_accessor_name(field)
        # проверка текущей модели дескриптора на игнор поля
        if skip_field(self.model, field, fld_accessor_name):
            return True
        # проверки моделей вышестоящих дескрипторов
        descriptor = self
        accessor_name = fld_accessor_name
        while descriptor.parent:
            accessor_name = '.'.join((descriptor.accessor_name, accessor_name))
            if skip_field(descriptor.parent.model, field, accessor_name):
                return True
            # проверка, что связанная модель поля, не связана с родительскими моделями полей
            if getattr(field, 'related_model', None) and field.related_model in descriptor.parent.related_field_models:
                return True

            descriptor = descriptor.parent
        # проверка модели источника данных
        accessor_name = '.'.join((self.full_accessor_name, fld_accessor_name))
        if skip_field(self.data_source.model, field, accessor_name):
            return True

        return False

    @property
    def model(self):
        if isinstance(self.field, ForeignObjectRel):
            model = self.field.related_model
        elif isinstance(self.field, RelatedField):
            model = get_related(self.field).parent_model
        else:
            model = None

        return model

    @cached_property
    def related_field_models(self):
        """Связанные модели полей."""
        fields_models = set()
        # Для первых в корне добавляем модели источника данных.
        if self.parent is None:
            data_source_columns = tuple(self.data_source.get_available_columns())
            fields_models.update({column.model for column in data_source_columns if column.model})
            fields_models.add(self.data_source.model)

        # получаем поля текущего экземпляра
        if self.model:
            fields = self.model._meta.get_fields()
            fields_models.update({field.related_model for field in fields if field.related_model})
            # добавляем саму модель экземпляра, если она есть
            fields_models.add(self.model)

        return fields_models

    @property
    def accessor_name(self):
        return force_str(_get_accessor_name(self.field))

    @property
    def lookup(self):
        return force_str(self.field.name)

    @property
    def full_accessor_name(self):
        if self.parent:
            return '.'.join((self.parent.full_accessor_name, self.accessor_name))
        else:
            return self.accessor_name

    @property
    def full_lookup(self):
        if self.parent:
            return '__'.join((self.parent.full_lookup, self.lookup))
        else:
            return self.lookup

    @property
    def data_type(self):
        """Тип данных в столбце.

        :rtype: str
        """
        if not isinstance(self.field, (Field, ForeignObjectRel, RelatedField)):
            result = self.field.data_type
        else:
            result = get_data_type(self.field)

        return result

    @property
    def choices(self):
        """Допустимые значения столбца с описанием."""
        return self.field.choices or None

    @property
    def title(self):
        if self.data_source.field_titles and self.full_accessor_name in self.data_source.field_titles:
            return self.data_source.field_titles[self.full_accessor_name]

        if isinstance(self.field, ForeignObjectRel):
            options = getattr(self.field.related_model, '_meta')
            if isinstance(self.field, OneToOneRel):
                result = options.verbose_name
            else:
                result = options.verbose_name_plural
        else:
            result = self.field.verbose_name

        return force_str(result)

    def get_full_title(self, delimiter=' → '):
        """Возвращает полное наименование с учетом иерархии.

        :param str delimiter: Разделитель наименований.

        :rtype: str
        """
        if self.parent:
            return delimiter.join((self.parent.get_full_title(delimiter), self.title))
        else:
            return self.title

    def is_root(self):
        return not self.parent

    @property
    def root(self):
        result = self

        while result.parent:
            result = result.parent

        return result

    def has_nested_columns(self):
        if self.model is None:
            return False

        for field in getattr(self.model, '_meta').get_fields():
            if not self._check_to_exclude(field):
                return True

        if hasattr(self.model, 'report_constructor_params') and 'extra' in self.model.report_constructor_params:
            extra = self.model.report_constructor_params['extra']
            for accessor_name, params in extra.items():
                field = ExtraField(accessor_name, params['field'])
                if not self._check_to_exclude(field):
                    return True

        return False

    def get_nested_columns(self):
        if self.model is None:
            yield ()
        else:
            for field in getattr(self.model, '_meta').get_fields():
                if not self._check_to_exclude(field):
                    yield ColumnDescriptor(self.data_source, self, field, level=self.level + 1)

            if hasattr(self.model, 'report_constructor_params') and 'extra' in self.model.report_constructor_params:
                extra = self.model.report_constructor_params['extra']
                for accessor_name, params in extra.items():
                    field = ExtraField(accessor_name, params['field'])
                    if not self._check_to_exclude(field):
                        yield ColumnDescriptor(self.data_source, self, field, level=self.level + 1)

    def validate_value(self, value):
        """Проверяет текстовое представление значения на соотв-е типу поля.

        :param str value: Текстовое представление значения для проверки.

        :raises django.core.exceptions.ValidationError: если значение аргумента
            value не прошло проверку. Описание ошибки будет в исключении.
        """
        if self.data_type == constants.CT_REVERSE_RELATION:
            raise ValidationError('Обратная связь не доступна для сравнения.')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        elif self.data_type == constants.CT_DIRECT_RELATION:
            raise ValidationError('Ключевые поля не доступны для сравнения.')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        elif self.data_type == constants.CT_CHOICES:
            lower_case_value = value.lower()
            for _, choice_display in self.field.choices:
                if choice_display.lower() == lower_case_value:
                    break
            else:
                raise ValidationError('Недопустимое значение для сравнения: {}.'.format(value))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        else:
            form_field = self.field.formfield()
            if form_field:
                form_field.validate(value)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class FakeField:
    """Класс несуществующего поля модели для отчета.

    Предназначен для подмены реальных полей при отображении в отчете.
    """

    def __init__(self, name):
        self.id = None
        self.name = name
        self.verbose_name = name
        self.concrete = False
        self.data_type = constants.CT_OTHER


class ExtraField:
    """Класс дополнительного поля модели.

    Используется для доступа к атрибутам объектов моделей, а также результатам
    вызова функций с объектом модели в качестве аргумента.
    """

    def __init__(self, name, field):
        """Инициализация экземпляра.

        :param name: имя дополнительного поля (не должно совпадать ни с одним
            реальным полем модели).
        :type name: str

        :param field: тип данных атрибута, либо результата вызова функции.
        :type field: django.db.models.fields.Field
        """
        field.concrete = False
        field.choices = None

        self._name = name
        self._field = field

    @property
    def name(self):
        return self._name

    @property
    def concrete(self):
        return False

    @property
    def verbose_name(self):
        return self._field.verbose_name

    @property
    def data_type(self):
        result = get_data_type(self._field)
        return result

    @property
    def model(self):
        return self._field.model

    @property
    def formfield(self):
        return self._field.formfield


class _ModelDataSourceInfo:
    """Клас-примесь для работы с информацией об источнике данных."""

    def __init__(self, model, filter_func=None, field_titles=None):
        """Инициализация экземпляра.

        :param model: Модель, для источника данных которой определяются
            параметры. См. :class:`educommon.django.db.utils.LazyModel`

        :param filter_func: Фильтрующая функция. Накладывает дополнительные
            ограничения для данных в источнике.

        :param dict field_titles: Переопределенные наименования полей в
            источнике данных. Используется для изменения наименования поля
            умолчанию, которое берётся из атрибута ``verbose_name`` поля
            модели.

            .. code:: python

               _ModelDataSourceInfo(
                   ...,
                   field_titles={
                       'restored_to': 'Сведения до восстановления',
                       'person.surname': 'Фамилия физ. лица',
                   }
               )
        """
        self._model = LazyModel(model)
        self._filter_func = filter_func
        self.field_titles = field_titles

    @cached_property
    def model(self):
        return self._model.get_model()

    @cached_property
    def name(self):
        """Внутрисистемное имя источника данных."""
        result = '.'.join((self._model.app_label, self._model.model_name))

        return force_str(result)

    @cached_property
    def title(self):
        """Отображаемое пользователю наименование источника данных."""
        result = getattr(self.model, '_meta').verbose_name
        return force_str(result)


class ModelDataSourceParams(_ModelDataSourceInfo):
    """Параметры для дескриптора источника данных в шаблоне отчета."""

    def get_data_source_descriptor(self):
        """Возвращает дескриптор источника данных."""
        return ModelDataSourceDescriptor(self._model.get_model(), self._filter_func, self.field_titles)


class ModelDataSourceDescriptor(_ModelDataSourceInfo):
    """Дескриптор модели, являющейся источником данных в шаблоне отчета."""

    def __init__(self, *args, **kwargs):
        super(ModelDataSourceDescriptor, self).__init__(*args, **kwargs)

        self.column_descriptors_cache = {}

    @cached_property
    def _options(self):
        return ModelOptions(self._model.get_model())

    def add_source_filter(self, query, include_available_units, user):
        """Добавление фильтра к источнику данных."""
        if self._filter_func:
            return self._filter_func(query, include_available_units, user)
        return query

    def get_available_columns(self):
        model = self._model.get_model()

        for field in getattr(model, '_meta').get_fields():
            if not skip_field(model, field, _get_accessor_name(field)):
                yield ColumnDescriptor(self, None, field)

        if hasattr(model, 'report_constructor_params') and 'extra' in model.report_constructor_params:
            extra = model.report_constructor_params['extra']
            for accessor_name, params in extra.items():
                field = ExtraField(accessor_name, params['field'])
                yield ColumnDescriptor(self, None, field)

    @staticmethod
    def _get_model_field_by_name(model, field_name):
        """Получает поле модели и модель связанную с ним по его имени.

        Рейзит FieldDoesNotExist если поле с таким именем не найдено.
        """
        for field in getattr(model, '_meta').get_fields():
            if skip_field(model, field, field_name):
                continue

            if isinstance(field, ForeignObjectRel):
                found_field_name = field.get_accessor_name()
                field_model = field.related_model
            else:
                found_field_name = field.name
                if isinstance(field, RelatedField):
                    field_model = get_related(field).parent_model
                else:
                    field_model = None

            if found_field_name == field_name:
                column_field = field
                model = field_model
                break

        else:
            if (
                hasattr(model, 'report_constructor_params')
                and 'extra' in model.report_constructor_params
                and field_name in model.report_constructor_params['extra']
            ):
                column_field = get_field(model, field_name)
            else:
                raise FieldDoesNotExist('{}.{}'.format(model.__name__, field_name))

        return column_field, model

    def is_column_ignored(self, accessor_name):
        """Проверяет исключение модели ``model.report_constructor_params``.

        :param str accessor_name: путь, через ".", до поля от указанной модели.

        :rtype: bool
        """
        level_names = []
        model = self.model
        for level_name in accessor_name.split('.'):
            level_names.append(level_name)
            full_accessor_name = '.'.join(level_names)

            if field_ignored_by_model_params(model, full_accessor_name):
                return True

        return False

    def is_column_exist(self, accessor_name):
        """Проверяет существование поля в моделе.

        :param str accessor_name: путь, через ".", до поля от указанной модели.

        :rtype: bool
        """
        model = self.model
        for name in accessor_name.split('.'):
            try:
                _, model = self._get_model_field_by_name(model, name)
            except FieldDoesNotExist:
                return False

        return True

    def get_column_descriptor(self, accessor_name):
        """Возвращает дескриптор столбца по его имени.

        .. code-block:: python

           data_source.get_column_descriptor('person.surname')

        :rtype: ColumnDescriptor
        """
        level_names = []
        model = self.model
        result = None
        for level_name in accessor_name.split('.'):
            level_names.append(level_name)
            full_accessor_name = '.'.join(level_names)

            if not model:
                raise FieldDoesNotExist(full_accessor_name)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Поиск поля в модели.

            column_field, model = self._get_model_field_by_name(model, level_name)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Создание дескриптора столбца, если его нет в кэше.

            if full_accessor_name in self.column_descriptors_cache:
                result = self.column_descriptors_cache[full_accessor_name]
            else:
                result = ColumnDescriptor(self, result, column_field, len(level_names) - 1)
                self.column_descriptors_cache[full_accessor_name] = result
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        return result

    def get_fake_column_descriptor(self, column_name):
        """Возвращает дескриптор отсутствующего столбца по его имени.

        .. code-block:: python

           data_source.get_fake_column_descriptor('person.surname')

        :rtype: FakeColumnDescriptor
        """
        level_names = []
        model = self.model
        result = None
        for level_name in column_name.split('.'):
            level_names.append(level_name)
            full_accessor_name = '.'.join(level_names)

            if full_accessor_name in self.column_descriptors_cache:
                result = self.column_descriptors_cache[full_accessor_name]

            if not model:
                return ColumnDescriptor(self, result, FakeField(column_name), len(level_names) - 1)
            # Создание дескриптора столбца, если его нет в кэше.

            if full_accessor_name in self.column_descriptors_cache:
                result = self.column_descriptors_cache[full_accessor_name]
            else:
                result = ColumnDescriptor(self, result, FakeField(column_name), len(level_names) - 1)
                self.column_descriptors_cache[full_accessor_name] = result
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        return result
