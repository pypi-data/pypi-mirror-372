"""Внедряем в джанговский дефолтный FieldFile необходимый функционал для работы с AtcfsStorage."""

import re

from django.core.files.storage import (
    DefaultStorage,
    get_storage_class,
)
from django.db.models.fields import (
    files,
)

from educommon.django.storages.atcfs.storage import (
    AtcfsStorage,
)


DEFAULT_FILE_STORAGE = get_storage_class()


def is_atcfs_storage(storage):
    """Функция определяет является ли переданный storage AtcfsStorage.

    :param storage: объект Storage
    :return: True/False
    """
    # Первый случай это когда storage выставлен напрямую через параметр в филде.
    # Второй случай когда в сетингсах установлен DEFAULT_FILE_STORAGE,
    # и он не переопределен через параметр storage в филде.
    if (
        isinstance(storage, AtcfsStorage)
        or isinstance(storage, DefaultStorage)
        and DEFAULT_FILE_STORAGE == AtcfsStorage
    ):
        return True

    return False


# Переопределяем __init__ FieldFile.
# Необходимо установить field_name,
# в котором будет храниться реальное название файла.

uuid_re = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

old_field_file__init__ = files.FieldFile.__init__


def new_field_file__init__(self, instance, field, name):
    """Инициализирует FieldFile с дополнительной логикой для AtcfsStorage."""
    old_field_file__init__(self, instance, field, name)
    if is_atcfs_storage(self.storage):
        if self.name and uuid_re.match(self.name):
            self.file_name = self.storage.name(self.name)
        else:
            self.file_name = ''


files.FieldFile.__init__ = new_field_file__init__


# Переопределяем __str__ FieldFile.

old_field_file__str__ = files.FieldFile.__str__


def new_field_file__str__(self):
    """Возвращает строковое представление файла."""
    if is_atcfs_storage(self.storage):
        return self.file_name or ''
    else:
        return old_field_file__str__(self)


files.FieldFile.__str__ = new_field_file__str__


# Переопределяем get_prep_value FileField.

old_file_field_get_prep_value = files.FileField.get_prep_value


def new_file_field_get_prep_value(self, value):
    """Подготавливает значение FileField для сохранения в БД."""
    if is_atcfs_storage(self.storage):
        if value is None:
            return None
        return value.name
    else:
        return old_file_field_get_prep_value(self, value)


files.FileField.get_prep_value = new_file_field_get_prep_value
