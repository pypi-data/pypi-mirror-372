"""Роутеры для приложений Django."""

from abc import (
    ABCMeta,
)

from django.core.exceptions import (
    ImproperlyConfigured,
)
from m3_django_compat import (
    DatabaseRouterBase,
)


class ServiceDbRouterBase(DatabaseRouterBase, metaclass=ABCMeta):
    """Основа роутера для моделей приложений, использующих сервисную БД.

    Все модели, имена которых указаны в атрибуте ``service_db_model_names``,
    закрепляет за сервисной БД, а остальные модели приложения закрепляет за
    основной БД. Имя приложения указывается в атрибуте ``app_name``.

    Пример использования:

        class DatabaseRouter(ServiceDbRouterBase):
            app_name = 'esia_saml'
            service_db_model_names = {'EsiaRequestLog'}
    """

    # имя приложения
    app_name = None

    # имена моделей плагина, которые должны храниться в сервисной БД
    service_db_model_names = None

    def __init__(self):
        """Определяет алиасы основной и сервисной баз данных."""
        from django.conf import (
            settings,
        )
        from django.db.utils import (
            DEFAULT_DB_ALIAS,
        )

        aliases = list(settings.DATABASES)
        if len(aliases) != 2:
            # Роутер поддерживает только конфигурации с двумя БД.
            raise ImproperlyConfigured('Database router support only two databases')

        self.default_db_alias = DEFAULT_DB_ALIAS

        alias_index = 1 if aliases[0] == DEFAULT_DB_ALIAS else 0
        self.service_db_alias = aliases[alias_index]

        self.service_db_model_names = {model_name.lower() for model_name in self.service_db_model_names}

    def _db_for_model(self, model, **hints):
        """Возвращает имя БД для чтения/записи данных из модели *model*."""
        if model._meta.app_label != self.app_name:
            # модель не имеет отношения к плагину
            return None
        elif model.__name__.lower() in self.service_db_model_names:
            return self.service_db_alias
        else:
            return self.default_db_alias

    db_for_read = _db_for_model
    db_for_write = _db_for_model

    def _allow(self, db, app_label, model_name):
        """Определяет, разрешён ли доступ к модели в указанной БД."""
        assert db in (self.default_db_alias, self.service_db_alias)

        if app_label == self.app_name:
            if model_name is None:
                return True
            else:
                model_name = model_name.lower()
                return (db == self.default_db_alias and model_name not in self.service_db_model_names) or (
                    db == self.service_db_alias and model_name in self.service_db_model_names
                )
