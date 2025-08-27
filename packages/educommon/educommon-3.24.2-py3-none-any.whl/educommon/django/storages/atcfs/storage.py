import datetime
import os
import tempfile

from django.core.files import (
    File,
)
from django.core.files.storage import (
    Storage,
)
from django.urls import (
    reverse,
)
from m3 import (
    ApplicationLogicException,
)

from educommon.django.storages.atcfs.api import (
    AtcfsApi,
)
from educommon.django.storages.atcfs.exceptions import (
    AtcfsUnavailable,
)


# Сообщение, выдаваемое в интерфейс при сохранении если сервер недоступен.
ATCFS_UNAVAILABLE_MSG = """
Извините, в настоящий момент внешнее файловое хранилище недоступно,
сохранение приложенного файла невозможно. Пожалуйста, повторите действие позже
или удалите приложенный файл перед сохранением.
"""

# Ссылка на файл и имя, когда недоступен сервер.
UNAVAILABLE_FILE_NAME = 'Файл недоступен (сбой в работе файлового хранилища)'


class AtcfsStorage(Storage):
    """ATCFS Storage."""

    def __init__(self):
        self.api = AtcfsApi()

    def _open(self, name, mode='rb'):
        return File(open(self.path(name), mode))

    def save(self, name, content):
        if name is None:
            name = content.name
        # нам нужно только название без относительного пути
        name = os.path.basename(name)
        try:
            ident = self.api.upload_file(name, content)
        except AtcfsUnavailable:
            # Выдаем сообщение непосредственно в интерфейс.
            raise ApplicationLogicException(ATCFS_UNAVAILABLE_MSG)

        return ident

    def delete(self, ident):
        try:
            self.api.delete_file(ident)
        except AtcfsUnavailable:
            # Если сервер недоступен, то ничего не делаем.
            # Таким образом механизм удаления пойдет дальше,
            # и в базе идентификатор файла удалится. Однако, сам файл
            # на сервере ATC FS останется - можно пренебречь.
            pass

    def url(self, ident):
        try:
            file_url = self.api.get_file_url(ident)
        except AtcfsUnavailable:
            file_url = reverse('atcfs_unavailable')

        return file_url

    def size(self, ident):
        try:
            file_info = self.api.get_file_info(ident)
            file_size = file_info['size']
        except AtcfsUnavailable:
            file_size = 0

        return file_size

    def name(self, ident):
        try:
            file_info = self.api.get_file_info(ident)
            file_name = file_info['name']
        except AtcfsUnavailable:
            file_name = UNAVAILABLE_FILE_NAME

        return file_name

    def path(self, ident):
        """Загружаем файл, сохраняем его во временной папке, отдаем путь."""
        try:
            file_name, file_content = self.api.download_file(ident)
        except AtcfsUnavailable:
            file_name = 'empty'
            file_content = ''
        dir_path = tempfile.mkdtemp()
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as fd:
            fd.write(file_content)

        return file_path

    def exists(self, name):
        """Заглушка."""
        return False

    def listdir(self, path):
        """Заглушка."""
        return [], []

    def accessed_time(self, name):
        """Заглушка."""
        return datetime.datetime(1, 1, 1)

    def created_time(self, name):
        """Заглушка."""
        return datetime.datetime(1, 1, 1)

    def modified_time(self, name):
        """Заглушка."""
        return datetime.datetime(1, 1, 1)
