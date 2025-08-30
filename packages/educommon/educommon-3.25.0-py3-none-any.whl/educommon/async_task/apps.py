from django.apps import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):
    """Конфигурация реестра "Асинхронные задачи".

    Устанавливает имя и метку приложения для регистрации в системе Django.
    """

    name = __package__
    label = 'async_task'
