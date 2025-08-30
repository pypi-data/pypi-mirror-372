from abc import (
    ABCMeta,
    abstractmethod,
)


class IConfig(metaclass=ABCMeta):
    """Конфигурация управлением доступом на основе ролей.

    Позволяет ограничивать выбор классов, на которые может ссылаться
    :class:`~educommon.auth.rbac.models.UserRole` в атрибуте ``user``.
    """

    @property
    @abstractmethod
    def user_types(self):
        """Типы классов пользователей, которым назначаются роли.

        Отсутствие указывает на то, что ограничение по назначаемым ролям будет
        отключено.

        :rtype: set of django.db.models.Model or bool
        """


class DefaultConfig(IConfig):
    """Конфигурация без ограничения ролей пользователей."""

    user_types = False


# : Конфигурация управлением доступом.
rbac_config = DefaultConfig()
