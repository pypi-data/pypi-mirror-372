"""Модели приложения логирования СМЭВ."""

import datetime

from django.db import (
    models,
)
from django.db.models import (
    Q,
)
from django.db.models.expressions import (
    Case,
    Value,
    When,
)

from m3.db import (
    BaseEnumerate,
    BaseObjectModel,
)


class SmevSourceEnum(BaseEnumerate):
    """Источники взаимодействия."""

    EPGU = 0
    RPGU = 1
    INTER = 2
    BARS_OBR = 3
    CONCENTRATOR = 4
    MFC = 5

    SOURCE_TYPES = (
        (EPGU, 'ЕПГУ'),
        (RPGU, 'РПГУ'),
        (INTER, 'Межведомственное взаимодействие'),
        (BARS_OBR, 'Барс-Образование'),
        (CONCENTRATOR, 'Концентратор'),
        (MFC, 'МФЦ'),
    )

    values = dict(SOURCE_TYPES)


class ExtendedSmevLogManager(models.Manager):
    """Расширенный менеджер логов СМЭВ.

    Аннотирует дополнительные поля.
    """

    def get_queryset(self):
        query = super().get_queryset()
        return query.annotate(
            # Пустые и null значения приведем к значению по умолчанию "Успешно"
            # для использования в фильтрации
            result_with_default=Case(
                When(Q(result__isnull=True) | Q(result=''), then=Value(SmevLog.RESULT_DEFAULT_VALUE)),
                default='result',
                output_field=models.CharField(),
            ),
        )


class SmevLog(BaseObjectModel):
    """Логи СМЭВ web-сервисов."""

    # Виды взаимодействия
    IS_SMEV = 0
    IS_NOT_SMEV = 1
    INTERACTION_TYPES = (
        (IS_SMEV, 'СМЭВ'),
        (IS_NOT_SMEV, 'Не СМЭВ'),
    )

    # Направление запроса
    INCOMING = 1
    OUTGOING = 0
    DIRECTION = (
        (INCOMING, 'Входящие запросы'),
        (OUTGOING, 'Исходящие запросы'),
    )

    # Потребители сервиса
    ENTITY = 0
    INDIVIDUAL = 1
    CONSUMER_TYPES = (
        (ENTITY, 'Юридическое лицо'),
        (INDIVIDUAL, 'Физическое лицо'),
    )

    # Источник взаимодействия
    EPGU = SmevSourceEnum.EPGU
    RPGU = SmevSourceEnum.RPGU
    INTER = SmevSourceEnum.INTER
    BARS_OBR = SmevSourceEnum.BARS_OBR
    SOURCE_TYPES = SmevSourceEnum.SOURCE_TYPES

    RESULT_DEFAULT_VALUE = 'Успешно'

    service_address = models.CharField('Адрес сервиса', max_length=250, null=True, blank=True)

    method_name = models.CharField('Код метода', max_length=250, null=True, blank=True, db_index=True)

    method_verbose_name = models.CharField('Наименование метода', max_length=250, null=True, blank=True)

    request = models.TextField('SOAP запрос', null=True, blank=True)
    response = models.TextField('SOAP ответ', null=True, blank=True)
    result = models.TextField('Результат', null=True, blank=True)

    time = models.DateTimeField('Время СМЭВ запроса', default=datetime.datetime.now, db_index=True)

    interaction_type = models.PositiveSmallIntegerField(
        'Вид взаимодействия', choices=INTERACTION_TYPES, default=IS_SMEV
    )

    direction = models.SmallIntegerField(choices=DIRECTION, verbose_name='Направление запроса')

    consumer_type = models.PositiveSmallIntegerField(
        'Потребитель сервиса', choices=CONSUMER_TYPES, default=INDIVIDUAL, null=True, blank=True
    )

    consumer_name = models.CharField('Наименование потребителя', max_length=100, null=True, blank=True)

    source = models.PositiveSmallIntegerField(
        'Источник взаимодействия', choices=SOURCE_TYPES, default=None, null=True, blank=True
    )

    target_name = models.CharField('Наименование электронного сервиса', max_length=100, null=True, blank=True)

    objects = models.Manager()
    extended_manager = ExtendedSmevLogManager()

    class Meta:
        verbose_name = 'Лог запросов СМЭВ'
        verbose_name_plural = 'Логи запросов СМЭВ'


class SmevProvider(BaseObjectModel):
    """Поставщики СМЭВ."""

    # Источник взаимодействия
    EPGU = SmevSourceEnum.EPGU
    RPGU = SmevSourceEnum.RPGU
    INTER = SmevSourceEnum.INTER
    CONCENTRATOR = SmevSourceEnum.CONCENTRATOR
    SOURCE_TYPES = SmevSourceEnum.SOURCE_TYPES

    mnemonics = models.CharField('Мнемоника', max_length=100)
    address = models.CharField('Адрес СМЭВ', max_length=100)
    source = models.PositiveSmallIntegerField('Источник взаимодействия', choices=SOURCE_TYPES)
    service_name = models.CharField('Наименование эл. сервиса', max_length=100)
    service_address_status_changes = models.CharField(
        'Адрес сервиса изменения статуса', max_length=100, null=True, blank=True
    )
    entity = models.CharField('Наименование юр.лица', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Поставщик СМЭВ'
        verbose_name_plural = 'Поставщики СМЭВ'
        unique_together = ('mnemonics', 'address')
