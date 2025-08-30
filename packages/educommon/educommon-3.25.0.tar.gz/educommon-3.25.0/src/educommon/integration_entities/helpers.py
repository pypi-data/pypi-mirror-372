from abc import (
    ABC,
    abstractmethod,
)
from itertools import (
    chain,
)
from typing import (
    Dict,
    Iterable,
    Optional,
    Union,
)

from django.db.models import (
    Model,
)
from django.utils import (
    timezone,
)

from m3_db_utils.models import (
    FictiveForeignKeyMixin,
)

from educommon.integration_entities.enums import (
    EntityLogOperation,
)


class AbstractEntitySaver(ABC):
    """Абстрактный класс сохранения записей в моделях.

    Используется в рамках выгрузок РВД, Сферум и ГИСРУО.
    """

    def __init__(
        self,
        to_save_entities: Dict[Union[EntityLogOperation, str], dict],
        model: Optional[Model],
        ignore_conflicts: Optional[bool] = False,
        create_batch_size: Optional[int] = None,
        update_batch_size: Optional[int] = None,
    ):
        """Инициализация."""
        self._to_save_entities = to_save_entities
        self.model = model
        self.ignore_conflicts = ignore_conflicts
        self.create_batch_size = create_batch_size
        self.update_batch_size = update_batch_size

    def __call__(self, *args, **kwargs):
        """Вызов."""
        self._delete_entities()
        self._update_entities()
        self._create_entities()

    @abstractmethod
    def _get_entities_base(self, operation_type: EntityLogOperation) -> Iterable[Model]:
        """Базовый метод, возвращающий объекты для сохранения в зависимости от типа операции."""

    @property
    def _to_create_entities(self) -> Iterable[Model]:
        """Возвращает записи для создания."""
        return self._get_entities_base(EntityLogOperation.CREATE)

    @property
    def _to_update_entities(self) -> Iterable[Model]:
        """Возвращает записи для обновления."""
        return self._get_entities_base(EntityLogOperation.UPDATE)

    @property
    def _to_delete_entities(self) -> Union[list, Iterable[Model]]:
        """Возвращает записи для удаления.

        Частный случай, поэтому по умолчанию возвращает пустой список.
        """
        return []

    def _convert_fictive_foreign_keys(self, entities: Iterable[Model]):
        """Преобразование значений полей фиктивных внешних ключей.

        В рамках метода производится проверка наличия фиктивного внешнего ключа у модели. Если они есть и заполнены
        объектами модели, то производится получения идентификатора объекта модели и замена им самого объекта.
        """
        for entity in entities:
            if isinstance(entity, FictiveForeignKeyMixin):
                for field_name in entity.fictive_foreign_key_field_names:
                    field_value = getattr(entity, field_name, None)

                    if field_value and isinstance(field_value, Model):
                        setattr(entity, field_name, getattr(field_value, 'pk'))

    def _create_entities(self) -> None:
        """Создает новые записи."""
        self._convert_fictive_foreign_keys(entities=self._to_create_entities)

        self.model.objects.bulk_create(
            self._to_create_entities,
            batch_size=self.create_batch_size,
            ignore_conflicts=self.ignore_conflicts,
        )

    def _update_entities(self) -> None:
        """Обновляет записи."""
        self._convert_fictive_foreign_keys(entities=self._to_create_entities)

        for entity in self._to_update_entities:
            # Поле modified имеет свойство auto_now=True и оно не обновляется при update и bulk_update.
            # Поэтому, его нужно обновить вручную:
            entity.modified = timezone.now()

        self.model.objects.bulk_update(
            self._to_update_entities,
            [field.name for field in self.model._meta.fields if not field.primary_key],
            batch_size=self.update_batch_size,
        )

    def _delete_entities(self) -> None:
        """Удаляет записи или обрабатывает записи для удаления.

        Частный случай, поэтому метод мало где может пригодиться.
        """


class EntitySaver(AbstractEntitySaver):
    """Стандартный класс для сохранения моделей.

    Стандартный, потому что используется в большинстве случаев.
    """

    def _get_entities_base(self, operation_type: EntityLogOperation) -> Iterable[Model]:
        """Базовый метод, возвращающий объекты для сохранения в зависимости от типа операции."""
        return self._to_save_entities[operation_type].values()


class EntitySaverWithDeleting(EntitySaver):
    """Класс для сохранения моделей с обработкой записей для удаления."""

    @property
    def _to_delete_entities(self) -> Iterable[Model]:
        """Возвращает записи для обновления."""
        return self._get_entities_base(EntityLogOperation.DELETE)

    def _delete_entities(self) -> None:
        """Обновляет записи как удаленные, которые лежат по ключу удаления в _to_save_entities."""
        self.model.objects.bulk_update(
            self._to_delete_entities,
            [field.name for field in self.model._meta.fields if not field.primary_key],
            batch_size=self.update_batch_size,
        )


class EntitySaverWithRealDeleting(EntitySaver):
    """Класс для сохранения моделей с обработкой записей для удаления из базы данных."""

    @property
    def _to_delete_entities(self) -> Iterable[Model]:
        """Возвращает записи для удаления."""
        return self._get_entities_base(EntityLogOperation.DELETE)

    def _delete_entities(self) -> None:
        """Удаляет из бд записи, которые лежат по ключу удаления в _to_save_entities."""
        self.model.objects.filter(
            pk__in=[entity.pk for entity in self._to_delete_entities],
        ).delete()


class ChainEntitySaver(AbstractEntitySaver):
    """Класс для сохранения моделей.

    Chain, потому что формирование объектов для сохранения происходит с помощью itertools.chain
    """

    def _get_entities_base(self, operation_type: EntityLogOperation) -> Iterable[Model]:
        """Базовый метод, возвращающий объекты для сохранения в зависимости от типа операции."""
        return chain.from_iterable(
            [
                entities.values()
                for operation_entities in self._to_save_entities.values()
                for operation, entities in operation_entities.items()
                if operation == operation_type
            ]
        )


class IterableEntitySaver(AbstractEntitySaver):
    """Класс для сохранения моделей.

    Iterable, потому что формирование объектов для сохранения происходит в цикле.
    Используется в gis_ruo.
    """

    def __init__(self, *args, **kwargs):
        """Инициализация."""
        super().__init__(*args, model=None, **kwargs)

        # Для динамического хранения сущностей
        self.to_save_entities_ = {}

    def __call__(self, *args, **kwargs):
        """Вызов."""
        for entity_model, to_save_entities_ in self._to_save_entities.items():
            # В отличие от базовой реализации AbstractEntitySaver,
            # где модель определяется при инициализации, здесь несколько моделей для обработки.
            # Поэтому и модель и набор ее сущностей для сохранения определяются динамически:
            self.model = entity_model
            self.to_save_entities_ = to_save_entities_
            self._create_entities()
            self._update_entities()
            self._delete_entities()

    def _get_entities_base(self, operation_type: EntityLogOperation) -> Iterable[Model]:
        """Базовый метод, возвращающий объекты для сохранения в зависимости от типа операции."""
        return self.to_save_entities_[operation_type].values()


class IterableEntitySaverWithDeleting(IterableEntitySaver):
    """Класс для итерабельного сохранения моделей с обработкой записей для удаления."""

    @property
    def _to_delete_entities(self) -> Iterable[Model]:
        """Возвращает записи для обновления."""
        return self._get_entities_base(EntityLogOperation.DELETE)

    def _delete_entities(self) -> None:
        """Удаляет записи."""
        self.model.objects.filter(
            pk__in=[entity.pk for entity in self._to_delete_entities],
        ).delete()
