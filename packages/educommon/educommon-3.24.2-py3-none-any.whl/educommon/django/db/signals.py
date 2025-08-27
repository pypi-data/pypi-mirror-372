from typing import (
    Callable,
    Optional,
)

from django.db.models import (
    Model,
)
from django.dispatch.dispatcher import (
    Signal,
)
from educommon import (
    logger,
)


class BaseBeforeMigrateHandler:
    """
    Базовый обработчик сигнала before_handle_migrate_signal.

    Должен быть унаследован и инстанс наследника регистрироваться
    как обработчик сигнала.
    """

    def _is_accessing_non_migrating_databases(self, migrating_database: str) -> bool:
        for model_cls in self._get_working_models():
            db = self._get_model_db(model_cls)
            if db != migrating_database:
                return True

        return False

    def _get_model_db(self, model_cls: type[Model]) -> str:
        """
        Возвращает псевдоним базы данных, к которой пойдет запрос
        по данной модели.
        """

        return model_cls.objects.all().db

    def _get_migrating_database(self, sender) -> str:
        """Возвращает псевдоним базы данных, с которой работает миграция."""

        return sender.database

    def _get_working_models(self) -> set[type[Model]]:
        """Модели, с которым будет работать обработчик сигнала."""

        raise NotImplementedError()

    def handler(self, sender, *args, **kwargs):
        """Непосредственный обработчик сигнала."""

        raise NotImplementedError()

    def __call__(self, sender, *args, **kwargs):
        migrating_database = self._get_migrating_database(sender)
        if self._is_accessing_non_migrating_databases(migrating_database):
            logger.debug('Предотвращена попытка доступа к базе данных, по которой не производится миграция')
            return

        return self.handler(sender, *args, **kwargs)


class BaseAfterMigrateHandler:
    """
    Базовый обработчик сигнала after_handle_migrate_signal.

    Должен быть унаследован и инстанс наследника регистрироваться
    как обработчик сигнала.
    """

    def _is_accessing_non_migrating_databases(self, migrating_database: str) -> bool:
        for model_cls in self._get_working_models():
            db = self._get_model_db(model_cls)
            if db != migrating_database:
                return True

        return False

    def _get_model_db(self, model_cls: type[Model]) -> str:
        """
        Возвращает псевдоним базы данных, к которой пойдет запрос
        по данной модели.
        """

        return model_cls.objects.all().db

    def _get_migrating_database(self, sender) -> str:
        """Возвращает псевдоним базы данных, с которой работает миграция."""

        return sender.database

    def _get_working_models(self) -> set[type[Model]]:
        """Модели, с которым будет работать обработчик сигнала."""

        raise NotImplementedError()

    def handler(self, sender, *args, **kwargs):
        """Непосредственный обработчик сигнала."""

        raise NotImplementedError()

    def __call__(self, sender, *args, **kwargs):
        migrating_database = self._get_migrating_database(sender)
        if self._is_accessing_non_migrating_databases(migrating_database):
            logger.debug('Предотвращена попытка доступа к базе данных, по которой не производится миграция')
            return

        return self.handler(sender, *args, **kwargs)


class BeforeHandleMigrateSignal(Signal):
    _handler_base_class = BaseBeforeMigrateHandler

    def connect(
        self,
        receiver: Callable,
        sender: Optional = None,
        weak: bool = True,
        dispatch_uid: Optional[str] = None,
    ) -> None:
        """Регистрирует обработчик, если он является допустимым типом."""
        if not isinstance(receiver, self._handler_base_class):
            logger.warning(
                f'Обработчик сигнала before_handle_migrate_signal {receiver} не зарегистрирован, поскольку '
                f'он не является подклассом {self._handler_base_class.__name__}'
            )

        return super().connect(receiver, sender, weak, dispatch_uid)


class AfterHandleMigrateSignal(Signal):
    _handler_base_class = BaseBeforeMigrateHandler

    def connect(
        self,
        receiver: Callable,
        sender: Optional = None,
        weak: bool = True,
        dispatch_uid: Optional[str] = None,
    ) -> None:
        """Регистрирует обработчик, если он является допустимым типом."""
        if not isinstance(receiver, self._handler_base_class):
            logger.warning(
                f'Обработчик сигнала after_handle_migrate_signal {receiver} не зарегистрирован, поскольку '
                f'он не является подклассом {self._handler_base_class.__name__}'
            )

        return super().connect(receiver, sender, weak, dispatch_uid)


before_handle_migrate_signal = BeforeHandleMigrateSignal()
after_handle_migrate_signal = AfterHandleMigrateSignal()
