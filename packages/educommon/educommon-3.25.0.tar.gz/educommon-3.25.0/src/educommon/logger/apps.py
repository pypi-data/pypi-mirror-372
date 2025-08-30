from django.apps.config import (
    AppConfig,
)


class EduLoggerConfig(AppConfig):
    """Приложение с механизмами логирования."""

    name = 'educommon.logger'
    label = 'logger'

    def __set_default_settings(self):
        """Установка дефолтных значений настроек приложения."""
        from django.conf import (
            settings,
        )

        from educommon.logger import (
            app_settings as defaults,
        )

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))

    def ready(self):
        """Вызывается после инициализации приложения."""
        super().ready()

        # Установка дефолтных значений в settings.py
        self.__set_default_settings()
