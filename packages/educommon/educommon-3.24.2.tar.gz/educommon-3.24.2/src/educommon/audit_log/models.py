import re
from datetime import (
    datetime,
)
from logging import (
    WARNING,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Union,
)

from celery.signals import (
    before_task_publish,
    task_postrun,
    task_prerun,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.contrib.postgres.fields import (
    ArrayField,
    HStoreField,
)
from django.core.exceptions import (
    ValidationError,
)
from django.core.validators import (
    MinValueValidator,
)
from django.db import (
    models,
)
from django.db.backends.signals import (
    connection_created,
)
from django.dispatch.dispatcher import (
    receiver,
)
from django.utils import (
    timezone,
)

from educommon.audit_log.utils import (
    get_audit_log_context,
    get_model_by_table,
    set_db_param,
)
from educommon.django.db.models import (
    BaseModel,
    ReadOnlyMixin,
)
from educommon.thread_data import (
    thread_data,
)
from educommon.utils.misc import (
    message_to_sentry,
)


if TYPE_CHECKING:
    from django.db.models import (
        Field,
    )


class Table(ReadOnlyMixin, BaseModel):
    """Модель для хранения информации о таблицах, отслеживаемых системой аудита."""

    name = models.CharField(max_length=250, verbose_name='Имя таблицы')
    schema = models.CharField(max_length=250, verbose_name='Схема таблицы')
    logged = models.BooleanField(
        default=True,
        verbose_name='Отслеживаемость таблицы',
    )

    class Meta:
        unique_together = ('name', 'schema')
        verbose_name = 'Логируемая таблица'
        verbose_name_plural = 'Логируемые таблицы'


class AuditLog(ReadOnlyMixin, BaseModel):
    """Модель для хранения записей журнала изменений.

    Каждая запись описывает изменение конкретного объекта определённой модели,
    с указанием пользователя, действия, IP-адреса и зафиксированных данных.

    Поля:
        - table: ссылка на таблицу, в которой произошло изменение;
        - data: сериализованные значения объекта до изменения;
        - changes: изменения (только изменённые поля);
        - operation: тип действия (создание, изменение, удаление);
        - user_id, user_type_id, ip, time: информация об авторе действия.
    """

    OPERATION_CREATE = 1
    OPERATION_UPDATE = 2
    OPERATION_DELETE = 3
    OPERATION_CHOICES = (
        (OPERATION_CREATE, 'Создание'),
        (OPERATION_UPDATE, 'Изменение'),
        (OPERATION_DELETE, 'Удаление'),
    )

    user_id = models.IntegerField(
        null=True,
        db_index=True,
        verbose_name='Пользователь',
    )
    user_type_id = models.IntegerField(
        null=True,
        db_index=True,
        verbose_name='Тип пользователя',
    )
    ip = models.GenericIPAddressField(null=True, verbose_name='IP адрес')
    time = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='Дата, время')
    table = models.ForeignKey(
        Table,
        verbose_name='Таблица',
        on_delete=models.CASCADE,
    )
    object_id = models.IntegerField(db_index=True, verbose_name='Объект модели')
    data = HStoreField(null=True, verbose_name='Объект')
    changes = HStoreField(null=True, verbose_name='Изменения')
    operation = models.SmallIntegerField(choices=OPERATION_CHOICES, verbose_name='Действие')

    @property
    def transformed_data(self) -> Dict[str, Any]:
        """Преобразованные поля объекта."""
        return self._transform_fields(self.data)

    @property
    def transformed_changes(self) -> Dict[str, Any]:
        """Преобразованные поля изменений."""
        return self._transform_fields(self.changes)

    def is_read_only(self):
        """Запрещает запись в лог приложению."""
        return True

    def get_read_only_error_message(self, delete):
        """Возвращает сообщение об ошибке при попытке изменить или удалить запись."""
        action_text = 'удалить' if delete else 'изменить'
        result = 'Нельзя {} запись лога.'.format(action_text)
        return result

    @property
    def model(self):
        """Класс измененной модели."""
        return get_model_by_table(self.table)

    @property
    def fields(self):
        """Все поля измененной модели.

        :returns dict: {имя колонки в БД: поле, ...}
        """
        model = self.model
        if model:
            result = {field.get_attname_column()[1]: field for field in model._meta.fields}
            return result

    @property
    def user(self):
        """Пользователь, внесший изменения."""
        result = None
        try:
            content_type = ContentType.objects.get(id=self.user_type_id)
        except ContentType.DoesNotExist:
            pass
        else:
            model_class = content_type.model_class()
            if model_class:
                try:
                    return model_class.objects.get(pk=self.user_id)
                except model_class.DoesNotExist:
                    pass

        return result

    def _convert_str_to_dict(self, fields: str) -> Dict[str, Any]:
        """Преобразование строки из HStore в словарь."""
        # Перезагружаем значения модели из базы данных
        self.refresh_from_db()
        try:
            fields = dict(fields)
            message = 'Удалось после refresh_from_db()'
        except ValueError:
            # Вручную создаем словарь из строки
            pattern = r'"(\w+)"\s*=>\s*([^,]+)'
            # Ищем совпадения в строке
            matches = re.findall(pattern, fields)
            # Создаем словарь из найденных пар ключ-значение
            fields = {key: None if value == 'NULL' else value[1:-1] for key, value in matches}
            message = 'Удалось вручную'

        message_to_sentry(
            message=f'{message} преобразовать в словарь поле HStore модели AuditLog',
            extra={'fields': fields, 'id': self.id},
            tag='transformed_fields',
            level=WARNING,
        )

        return fields

    def _transform_fields(self, fields: Union[Dict[str, Optional[str]], str]) -> Dict[str, Any]:
        """Преобразует значения полей лога в соответствии с типами полей модели."""
        if isinstance(fields, str):
            fields = self._convert_str_to_dict(fields)

        transformed_fields = dict(fields)

        model_fields = self.fields
        for field, value in fields.items():
            if field in model_fields:
                field_type = model_fields[field]
                if isinstance(field_type, ArrayField):
                    transformed_fields[field] = self._transform_array_field(field_type.base_field, value)
                else:
                    try:
                        transformed_fields[field] = field_type.to_python(value)
                    except ValidationError:
                        transformed_fields[field] = value

        return transformed_fields

    def _transform_array_field(self, base_field: 'Field', value: Optional[Union[str, list]]) -> Optional[List[Any]]:
        """Преобразует значение поля ArrayField."""
        if value:
            if isinstance(value, list):
                return value

            items = value[1:-1]
            if items:
                return [base_field.to_python(item) for item in items.split(',')]

    class Meta:
        verbose_name = 'Запись журнала изменений'
        verbose_name_plural = 'Записи журнала изменений'


class PostgreSQLError(BaseModel):
    """Журнал ошибок, возникающих при работе триггеров журнала изменений."""

    user_id = models.IntegerField(
        'Пользователь',
        null=True,
    )
    ip = models.GenericIPAddressField(
        'IP адрес',
        null=True,
    )
    time = models.DateTimeField(
        'Дата, время',
        auto_now_add=True,
        validators=[MinValueValidator(datetime(1900, 1, 1))],
    )
    level = models.CharField(
        'Уровень ошибки',
        max_length=50,
    )
    text = models.TextField(
        'Текст ошибки',
    )

    class Meta:
        verbose_name = 'Ошибка PostgreSQL'
        verbose_name_plural = 'Ошибки PostgreSQL'
        db_table = 'audit"."postgresql_errors'


class LoggableModelMixin(models.Model):
    """Делает модель логируемой."""

    need_to_log = True

    class Meta:
        abstract = True


# -----------------------------------------------------------------------------
# Передача параметров контекста журналирования изменений в задания Celery.

# Именно такой способ передачи параметров контекста журналирования изменений
# выбран в связи с особенностями Celery, которые заключаются в том, что
# обработчики сигналов task_prerun, task_postrun и само задание выполняются в
# отдельных подключениях к БД, соответственно из обработчиков этих сигналов
# установить параметры нет возможности.


_package_name = __name__.rpartition('.')[0]


@before_task_publish.connect(dispatch_uid=_package_name + 'save')
def _save_audit_log_context_for_task(body, **_):
    """Дополняет параметры задания данными для журнала изменений.

    В словарь ``kwargs``, передаваемый в метод ``apply_async`` задания,
    добавляет параметр ``audit_log_params``, содержащий результат вызова
    функции :func:`~extedu.audit_log.utils.get_audit_log_context`.

    Работает только если запуск задания осуществляется в рамках обработки
    HTTP-запроса, т.е. если в :obj:`extedu.thread_data.http_request` сохранен
    HTTP-запрос.
    """
    if not hasattr(thread_data, 'http_request'):
        return

    body['kwargs'] = body.get('kwargs', {})
    request = thread_data.http_request
    body['kwargs']['audit_log_params'] = get_audit_log_context(request)


@task_prerun.connect(dispatch_uid=_package_name + 'set')
def _set_audit_log_context_for_task(kwargs, **_):
    """До выполнения задания сохраняет параметры контекста журнала изменений.

    Сохраненные в :obj:`extedu.thread_data.audit_log_params` параметры
    будут переданы в БД при подключении (см.
    ``_send_audit_log_context_to_db``).
    """
    if 'audit_log_params' in kwargs:
        thread_data.audit_log_params = kwargs['audit_log_params']


@task_postrun.connect(dispatch_uid=_package_name + 'unset')
def _unset_audit_log_context_for_task(task, kwargs, **_):
    """Очищает параметры журнала изменений после выполнения Celery-задания."""
    if hasattr(thread_data, 'audit_log_params'):
        del thread_data.audit_log_params


@receiver(connection_created, dispatch_uid=_package_name + 'send')
def _send_audit_log_context_to_db(**kwargs):
    """Передаёт параметры контекста журнала изменений в БД при подключении.

    Используется для установки параметров в PostgreSQL через set_config,
    чтобы аудит знал, кто инициировал изменения.
    """
    if hasattr(thread_data, 'audit_log_params'):
        for name, value in thread_data.audit_log_params.items():
            set_db_param('audit_log.' + name, value)


# -----------------------------------------------------------------------------
