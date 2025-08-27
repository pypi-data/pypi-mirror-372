import inspect
import sys
from collections import (
    defaultdict,
)

from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
)
from django.db import (
    IntegrityError,
    models,
    transaction,
)
from django.db.models.fields.related_descriptors import (
    ForwardOneToOneDescriptor,
    ReverseOneToOneDescriptor,
)
from django.db.models.query import (
    QuerySet as DjangoQuerySet,
)
from django.dispatch import (
    Signal,
)
from django.forms.forms import (
    NON_FIELD_ERRORS,
)
from m3_django_compat import (
    Manager as DjangoManager,
    atomic,
)

from educommon.django.db.validators import (
    IModelValidator,
)
from educommon.utils.misc import (
    NoOperationCM,
)


class QuerySet(DjangoQuerySet):
    """Доработанная для ModelValidationMixin версия QuerySet.

    Переопределяет методы create() и get_or_create(), добавляя валидацию
    объекта перед его сохранением в БД.
    """

    def create(self, **kwargs):
        """Создаёт объект модели.

        Копипаста метода из Django 1.4 с добавлением вызова full_clean().
        Обусловлено невозможностью расширения метода.
        """
        if self.model.clean_and_save_inside_transaction:
            cm = atomic()
        else:
            cm = NoOperationCM()

        with cm:
            obj = self.model(**kwargs)
            obj.full_clean()
            self._for_write = True
            obj.save(force_insert=True, using=self.db)

        return obj

    def get_or_create(self, **kwargs):
        """Ищет или создаёт объект модели.

        Копипаста метода из Django 1.4 с добавлением вызова full_clean().
        Обусловлено невозможностью расширения метода.
        """
        assert kwargs, 'get_or_create() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        lookup = kwargs.copy()
        for f in getattr(self.model, '_meta').fields:
            if f.attname in lookup:
                lookup[f.name] = lookup.pop(f.attname)
        try:
            self._for_write = True
            return self.get(**lookup), False
        except self.model.DoesNotExist:
            try:
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                obj = self.model(**params)
                obj.full_clean()
                sid = transaction.savepoint(using=self.db)
                obj.save(force_insert=True, using=self.db)
                transaction.savepoint_commit(sid, using=self.db)
                return obj, True
            except IntegrityError as e:
                transaction.savepoint_rollback(sid, using=self.db)

                try:
                    return self.get(**lookup), False
                except self.model.DoesNotExist:
                    raise e from None


class Manager(DjangoManager):
    """Доработанная версия менеджера моделей системы.

    Вместо QuerySet из Django использует доработанный QuerySet, выполняющий
    валидацию объекта перед его сохранением в БД в методе create().
    """

    def get_queryset(self):
        return QuerySet(self.model, using=self._db)


pre_clean = Signal()
"""Сигнал, отправляемый перед валидацией модели.

:param defaultdict errors: Словарь, содержащий ошибки валидации экземпляра
    модели.

.. seealso::

   :py:class:`ModelValidationMixin`
"""


post_clean = Signal()
"""Сигнал, отправляемый после валидации модели.

:param defaultdict errors: Словарь, содержащий ошибки валидации экземпляра
    модели.

.. seealso::

   :py:class:`ModelValidationMixin`
"""


class ModelValidationMixin(models.Model):
    """Примесь, добавляющая необходимость валидации перед сохранением.

    Также примесь переопределяет менеджер модели по умолчанию. В новом
    менеджере переопределяются два метода: create() и get_or_create(), которые
    перед созданием объекта модели выполняют валидацию.

    Пример:

    .. code-block:: python

        # Использование валидаторов модели

        # models.py основной системы
        class MyModel(BaseModel):
            # Поле обязательно в основной системе
            read_rules = models.BooleanField(...)

            # Поле обязательно при включенном плагине
            read_rules_plugin = models.BooleanField(...)

            validators = BaseModel.validators + [
                RequiredBooleanValidator('read_rules'),
            ]


        # extenders.py в плагине
        from app.models import MyModel

        MyModel.validators.append(RequiredBooleanValidator('read_rules_plugin'))
    """

    #: Признак использования транзакций при проверке и сохранении.
    #:
    #: Необходимость выполнения одновременной проверки и сохранения экземпляров
    #: модели (``.clean_and_save()``, ``.objects.create()``) возникает,
    #: например, при использовании ``.select_for_update()`` внутри
    #: ``full_clean()``.
    clean_and_save_inside_transaction = False

    objects = Manager()

    #: Список классов-валидаторов
    #:
    #: Позволяет задать набор валидаторов для основной системы и изменять
    #: его в плагинах.
    validators = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert not self.validators or all(isinstance(validator, IModelValidator) for validator in self.validators), (
            self.validators
        )

        self.__set_valid_flag(False)

    def __set_valid_flag(self, value):
        self.__dict__['_ModelValidationMixin__object_is_valid'] = value

    def clean(self):
        """Переносит валидацию объекта модели в метод simple_clean().

        При этом работа с исключениями ValidationError остается в данном
        методе, что позволяет не обрабатывать их в каждой модели.
        Если объект или связанные объекты не существуют, перехватывает
        ObjectDoesNotExist и выводит соответствующее сообщение.
        """
        errors = defaultdict(list)

        try:
            super().clean()
        except ValidationError as error:
            errors.update(error.update_error_dict(errors))

        try:
            self.simple_clean(errors)
        except ObjectDoesNotExist:
            # Достанем из стека вызовов объект модели, в которой было
            # вызвано исключение.
            tb = sys.exc_info()[-1]  # traceback
            # Фрейм, в котором сгенерировано исключение, будет последним.
            error_frame = inspect.getinnerframes(tb)[-1][0]
            descriptior_types = (
                ForwardOneToOneDescriptor,
                ReverseOneToOneDescriptor,
            )
            # Источником исключения может быть модель, кварисет или дескриптор
            exception_source = error_frame.f_locals['self']

            if isinstance(exception_source, descriptior_types):
                model_from = exception_source.related.model
                model_to = exception_source.related.field.model
                message = (
                    'При сохранении объекта "{}" для связанного объекта "{}" '
                    'не найдено соответствующего объекта "{}".'.format(
                        self._meta.verbose_name,
                        model_from._meta.verbose_name,
                        model_to._meta.verbose_name,
                    )
                )
            else:
                model_or_query = exception_source[0]
                if isinstance(model_or_query, models.Model):
                    model_name = model_or_query._meta.verbose_name
                elif isinstance(model_or_query, models.QuerySet):
                    model_name = model_or_query.model._meta.verbose_name
                message = f'Указанный объект {model_name} не существует.'

            errors.update({NON_FIELD_ERRORS: message})

        for validator in self.validators:
            validator.clean(instance=self, errors=errors)

        if errors:
            raise ValidationError(errors)

    def simple_clean(self, errors):
        """Выполняет валидацию объекта модели вместо метода clean().

        :param errors: Словарь с сообщениями об ошибках. Каждый ключ словаря
            должен соответствовать полю модели, а значением ключа является
            список сообщений об ошибках в этом поле. Подробнее см.
            django.core.exceptions.ValidationError.
        :type errors: collections.defaultdict
        """
        pass

    def full_clean(self, exclude=None):
        """Проставляет отметку о выполнении валидации экземпляра модели.

        Отправляет сигналы pre_clean и post_clean.
        """
        errors = defaultdict(list)

        pre_clean.send(sender=self.__class__, instance=self, errors=errors)

        try:
            super().full_clean(exclude)
        except ValidationError as error:
            errors.update(error.update_error_dict(errors))

        post_clean.send(sender=self.__class__, instance=self, errors=errors)

        if errors:
            raise ValidationError(errors)

        self.__set_valid_flag(True)

    @atomic
    def save(self, *args, **kwargs):
        """После сохранения объекта снимает отметку о выполнении валидации."""
        if not self.ready_to_save:
            raise AssertionError(
                'Attempt to save data without validation (model {}.{})'.format(
                    self.__class__.__module__, self.__class__.__name__
                )
            )

        super().save(*args, **kwargs)

        # Перед следующим сохранением нужно будет снова вызвать full_clean
        self.__set_valid_flag(False)

    @property
    def ready_to_save(self):
        """Готовность к сохранению объекта модели в БД."""
        return getattr(self, '_ModelValidationMixin__object_is_valid', False)

    def clean_and_save(self):
        """Валидация объекта и сохранение."""
        if self.clean_and_save_inside_transaction:
            cm = atomic()
        else:
            cm = NoOperationCM()

        with cm:
            self.full_clean()
            self.save()

    class Meta:
        # pylint: disable=no-init
        abstract = True
