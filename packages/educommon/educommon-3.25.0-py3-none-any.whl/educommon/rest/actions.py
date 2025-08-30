from objectpack.actions import (
    BasePack,
)

from educommon.rest import (
    mixins,
)


class BaseRestPack(BasePack):
    """Базовый пак для всех REST паков."""


class RestPack(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseRestPack,
):
    """Пак для обработки запросов методами: GET, POST, PUT, PATCH, DELETE.

    Для обработки запросов методом GET исользуются методы пака list и retrieve.
    Для обработки запросов методом POST используется метод пака create.
    Для обработки запросов методом PUT и PATCH используется метод пака update.
    Для обработки запросов методом DELETE используется метод пака destroy.
    """


class RestReadOnlyPack(mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseRestPack):
    """Пак который обрабатывает запросы только методом GET.

    Доступные методы пака: list и retrieve.
    """
