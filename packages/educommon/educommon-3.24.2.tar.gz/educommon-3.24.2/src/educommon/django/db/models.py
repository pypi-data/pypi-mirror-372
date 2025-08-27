from django.db import (
    models,
)
from m3.actions.exceptions import (
    ApplicationLogicException,
)
from m3.db import (
    BaseObjectModel,
)

from educommon.django.db.mixins import (
    DeferredActionsMixin,
    DeleteOnSaveMixin,
    ReprStrPreModelMixin,
    StringFieldsCleanerMixin,
)
from educommon.django.db.mixins.validation import (
    ModelValidationMixin,
)


class BaseModel(
    DeferredActionsMixin,
    DeleteOnSaveMixin,
    StringFieldsCleanerMixin,
    ModelValidationMixin,
    ReprStrPreModelMixin,
    BaseObjectModel,
):
    """Базовый класс для всех моделей системы."""

    class Meta:
        abstract = True


class ReadOnlyMixin(models.Model):
    """Класс-примесь для моделей с записями только для чтения.

    В основной модели должны быть реализованы два метода:
        - is_read_only()
        - get_read_only_error_message(delete)

    is_read_only(obj) должен возаращать True, если объект модели obj не
    подлежит изменению/удалению.

    get_read_only_error_message(delete=False) должен возвращать текст сообщения
    об ошибке. Параметр delete определяет операцию (False - изменение, True -
    удаление).
    """

    def _check_read_only(self, delete):
        """Вызывает исключение, если объект защищён от изменений или удаления."""
        if self.is_read_only():
            raise ApplicationLogicException(self.get_read_only_error_message(delete=delete))

    def safe_delete(self, *args, **kwargs):
        """Удаляет объект, если он не помечен как только для чтения."""
        self._check_read_only(delete=True)

        return super().safe_delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Удаляет объект, если он не помечен как только для чтения."""
        self._check_read_only(delete=True)

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Сохраняет объект, если он не помечен как только для чтения."""
        self._check_read_only(delete=False)

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
