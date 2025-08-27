"""Реестр "Асинхронные задачи"."""

import django


if django.VERSION < (3, 2):
    default_app_config = __name__ + '.apps.AppConfig'
