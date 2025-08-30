from django.apps.config import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):
    name = 'educommon.about'
    label = 'educommon_about'
    verbose_name = 'Базовое приложение "Информация о системе".'
