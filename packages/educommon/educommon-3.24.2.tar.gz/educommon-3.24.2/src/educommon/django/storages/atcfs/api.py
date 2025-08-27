import cgi
import hashlib
import re
import uuid
from urllib.parse import (
    unquote,
)

import requests

from educommon.django.storages.atcfs import (
    settings,
)
from educommon.django.storages.atcfs.exceptions import (
    AtcfsUnavailable,
)


class AtcfsApi:
    """Класс для работы с запросами к ATCFS."""

    def _build_url(self, *args):
        """Функция составления полного урла.

        :param args: составные части пути
        :return: фбсолютный урл
        """
        chunks = (settings.URL,) + args
        url = '/'.join(chunks)

        return url

    def _get_credential_headers(self):
        """Метод генерации данных для аутентификации на сервере ATCFS.

        :return: словарь с необходимыми для атунетификации полями
        """
        request_id = str(uuid.uuid4())
        sign = '{vis_id}_{vis_user}_{request_id}_{secret_key}'.format(
            **{
                'vis_id': settings.VIS_ID,
                'vis_user': settings.VIS_USER,
                'request_id': request_id,
                'secret_key': settings.SECRET_KEY,
            }
        )
        sign = hashlib.md5(sign).hexdigest()
        headers = {
            'AtcFs-VisId': settings.VIS_ID,
            'AtcFs-VisUser': settings.VIS_USER,
            'AtcFs-RequestId': request_id,
            'AtcFs-Sign': sign,
        }

        return headers

    def _send_request(self, method, url, headers=None, params=None, data=None):
        """Отправка запроса.

        :param method: get|post|delete
        :param url: URL, на который отправляется запрос
        :param headers: дополнительные заголовки
        :param params: параметры, которые будут переданы в URL
        :param data: данные для передачи
        :return: response
        """
        full_headers = self._get_credential_headers()
        full_headers.update(headers or {})
        try:
            return requests.request(
                method=method,
                url=url,
                headers=full_headers,
                params=params,
                data=data,
                timeout=(settings.CONNECT_TIMEOUT, None),
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.packages.urllib3.exceptions.ConnectTimeoutError,
        ):
            raise AtcfsUnavailable()

    def upload_file(self, name, content):
        """Загрузка файла на сервер ATCFS.

        :param name: название файла
        :param content: содержимое файла
        :return: идентификатор файла на сервере ATCFS
        """
        url = self._build_url(settings.FILES_PATH)
        headers = {'Content-Type': 'application/octet-stream'}
        params = {'fileName': name}
        data = content
        response = self._send_request(method='post', url=url, headers=headers, params=params, data=data)
        if response.status_code != 201:
            raise Exception(response.text)
        ident = response.text

        return ident

    def download_file(self, ident):
        """Загружаем файл с сервера в память.

        :param ident: идентификатор файла
        :return: тюпл название и содержимое
        """
        url = self._build_url(settings.FILES_PATH, ident)
        response = self._send_request(method='get', url=url)
        if response.status_code != 200:
            raise Exception(response.text)
        _, params = cgi.parse_header(response.headers.get('Content-Disposition'))
        file_name = params['filename*']
        try:
            file_name = re.findall(r'UTF-8\'\'(.*)', file_name)[0]
            file_name = unquote(file_name)
        except IndexError:
            pass
        file_content = response.content

        return file_name, file_content

    def delete_file(self, ident):
        """Удаление файла на сервере ATCFS.

        :param ident: идентификатор файла
        """
        url = self._build_url(settings.FILES_PATH, ident)
        response = self._send_request(method='delete', url=url)
        if response.status_code != 200:
            raise Exception(response.text)

    def get_file_url(self, ident):
        """Получить прямую ссылку на файл.

        :param ident: идентификатор файла
        :return: url
        """
        url = self._build_url(settings.TMP_FILE_LINK_PATH, ident)
        response = self._send_request(method='get', url=url)
        if response.status_code != 200:
            raise Exception(response.text)
        tmp_ident = response.text
        file_url = self._build_url(settings.TMP_FILES_PATH, tmp_ident)

        return file_url

    def get_file_info(self, ident):
        """Получить информацию о файле.

        :param ident: идентификатор файла
        :return: словарь с названием файла и его размером
        """
        url = self._build_url(settings.FILE_INFO_PATH, ident)
        response = self._send_request(method='get', url=url)
        if response.status_code != 200:
            raise Exception(response.text)
        file_json = response.json()
        file_info = {
            'name': file_json['fileName'],
            'size': file_json['size'],
        }

        return file_info
