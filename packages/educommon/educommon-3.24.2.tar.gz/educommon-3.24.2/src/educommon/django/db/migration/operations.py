from contextlib import (
    closing,
    contextmanager,
)

from django.core.serializers import (
    deserialize,
    python as python_serializer_module,
)
from django.db import (
    connection,
)
from django.db.migrations.operations.base import (
    Operation,
)
from django.db.migrations.operations.fields import (
    AddField,
    AlterField,
    RemoveField,
    RenameField,
)
from django.db.models import (
    Max,
)


def get_objects_from_fixture(file_path, file_type=None, use_natural_foreign_keys=False):
    """Возвращает генератор объектов из файла фикстуры.

    :param basestring file_path: Путь к файлу с данными.
    :param basestring file_type: Тип файла фикстуры (xml, json или yaml).
    :param bool use_natural_foreign_keys: Флаг, указывающий на необходимость
        использовать "естественные" (natural) ключи.

    :rtype: generator
    """
    if file_type is None:
        file_type = file_path[file_path.rfind('.') + 1 :]
        if file_type not in ('json', 'xml', 'yaml'):
            raise ValueError('Неподдерживаемый тип файла ' + file_path)

    with open(file_path, 'r') as infile:
        with closing(
            deserialize(file_type, infile.read(), use_natural_foreign_keys=use_natural_foreign_keys)
        ) as objects:
            for obj in objects:
                yield obj


def correct_sequence_value(model, field='id', conn=connection):
    """Корректирует значение последовательности для указанного поля модели.

    Устанавливает в качестве значения последовательности максимальное значение
    указанного поля. Актуально, когда, например, после загрузки какихм-либо
    данных из фикстур становится возможной ситуация, когда при добавлении
    очередной записи последовательность выдаёт значение, которое уже есть в БД.

    :param model: Класс модели.
    :param str field: Имя поля, для последовательности которого выполняется
        корректировка значения.
    :param conn: Подключение к БД, в которой размещена таблица указанной
        модели.
    """
    max_id = model.objects.aggregate(max_id=Max(field))['max_id'] or 1

    cursor = conn.cursor()

    cursor.execute(
        'SELECT setval(pg_get_serial_sequence(%s,%s), %s)',
        (
            model._meta.db_table,
            model._meta.get_field(field).column,
            max_id,
        ),
    )


class LoadFixture(Operation):
    """Операция загрузки фикстур в миграции."""

    reversible = False

    reduces_to_sql = False

    atomic = True

    def __init__(self, file_path, force=False, file_type=None, use_natural_foreign_keys=False):
        """Инициализация экземпляра класса.

        :param str file_path: Путь к файлу.
        :param bool force: Флаг, определяющий необходимость принудительной
            загрузки фикстуры в БД вне зависимости от роутеров БД.
        :param str file_type: Тип файла (json, xml или yaml).
        :param bool use_natural_foreign_keys: Флаг, указывающий на наличие
            в фикстуре "естественных" (natural) ключей.
        """
        self.file_path = file_path
        self.force = force
        self.file_type = file_type
        self.use_natural_foreign_keys = use_natural_foreign_keys

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Выполняет миграцию для выбранного приложения."""

        @contextmanager
        def replace_model_loader():
            _get_model = python_serializer_module._get_model
            python_serializer_module._get_model = to_state.apps.get_model
            yield
            python_serializer_module._get_model = _get_model

        db_alias = schema_editor.connection.alias

        with replace_model_loader():
            for obj in get_objects_from_fixture(self.file_path):
                model = obj.object.__class__
                if self.allow_migrate_model(db_alias, model) or self.force:
                    obj.save()


class CorrectSequence(Operation):
    """Корректирует значение последовательности для указанного поля.

    .. seealso::

        :func:`~educommon.django.db.migration.operations.correct_sequence_value`
    """

    reversible = False

    reduces_to_sql = False

    def __init__(self, model_name, force=False):
        self.model_name = model_name
        self.force = force

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Выполняет миграцию для выбранного приложения."""
        db_alias = schema_editor.connection.alias
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(db_alias, model) or self.force:
            correct_sequence_value(model, conn=schema_editor.connection)


class CreateSchema(Operation):
    """Создает схему в БД."""

    reversible = True

    def __init__(self, schema_name, owner=None, aliases=None, cascade_drop=False):
        """Инициализация экземпляра.

        :param schema_name: Имя схемы.
        :param owner: Имя владельца схемы.
        :param aliases: Алиасы БД, в которых нужно создать схему. Если не
            указаны, то схема создается во всех БД системы.
        :param bool cascade_drop: Истинное значение аргумента указывает на
            автоматическое удаление всех объектов, содержащихся в схеме, при
            откате операции.
        """
        self.schema_name = schema_name
        self.owner = owner
        self.aliases = aliases
        self.cascade_drop = cascade_drop

    def state_forwards(self, app_label, state):
        pass

    def state_backward(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Выполняет миграцию для выбранного приложения."""
        if not self.aliases or schema_editor.connection.alias in self.aliases:
            sql = 'CREATE SCHEMA IF NOT EXISTS ' + self.schema_name
            if self.owner:
                sql += ' AUTHORIZATION ' + self.owner
            schema_editor.execute(sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """Откатывает миграцию для выбранного приложения."""
        if not self.aliases or schema_editor.connection.alias in self.aliases:
            sql = 'DROP SCHEMA IF EXISTS ' + self.schema_name
            if self.cascade_drop:
                sql += ' CASCADE'
            schema_editor.execute(sql)


class _AnotherAppMixin:
    def __init__(self, *args, **kwargs):
        self.__app_label = kwargs.pop('app_label', None)

        super().__init__(*args, **kwargs)

    def state_forwards(self, app_label, state):
        """Применяет изменение к заданному приложению или текущему."""
        super().state_forwards(self.__app_label or app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Выполняет миграцию для выбранного приложения."""
        super().database_forwards(self.__app_label or app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """Откатывает миграцию для выбранного приложения."""
        super().database_backwards(self.__app_label or app_label, schema_editor, from_state, to_state)


class AddField(_AnotherAppMixin, AddField):
    """Операция добавления поля в модель с поддержкой других приложений.

    Имя приложения можно указать в аргументе :arg:`app_label`.
    """


class AlterField(_AnotherAppMixin, AlterField):
    """Операция изменения поля в модели с поддержкой других приложений.

    Имя приложения можно указать в аргументе :arg:`app_label`.
    """


class RemoveField(_AnotherAppMixin, RemoveField):
    """Операция удаления поля в модели с поддержкой других приложений.

    Имя приложения можно указать в аргументе :arg:`app_label`.
    """


class RenameField(_AnotherAppMixin, RenameField):
    """Операция переименования поля в модели с поддержкой других приложений.

    Имя приложения можно указать в аргументе :arg:`app_label`.
    """
