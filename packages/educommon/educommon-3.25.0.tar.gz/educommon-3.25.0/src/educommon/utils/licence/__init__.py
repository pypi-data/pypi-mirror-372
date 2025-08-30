import os.path

from django.core.exceptions import (
    ImproperlyConfigured,
)
from lxml import (
    etree,
)

from educommon.utils.misc import (
    cached_property,
)
from educommon.utils.xml import (
    get_text,
    load_xml_document,
)


class LicenceError(Exception):
    """Ошибка проверки файла лицензии."""


class Licence:
    """Базовый класс лицензии."""

    def __init__(self, licence_file_path, schema_file_path, config, params_root='//BarsLicence/LicenceData'):
        """Инициализация экземпляра класса.

        :param basestring licence_file_path: Путь к файлу лицензии.
        :param basestring schema_file_path: Путь к файлу c XML-схемой.
            Если указан, то файл лицензии будет проверяться на соответсвие этой
            схеме.
        :param basestring params_root: XPath-выражение для извлечения корневого
            элемента с параметрами лицензии.
        :param dict config: Словарь конфигурации лицензии.

        :raises django.core.exceptions.ImproperlyConfigured: если файл лицензии
            отсутствует или не доступен для чтения, либо цифровая подпись файла
            лицензии не проходит проверку.

        Пример конфигурации

        .. code-block:: python

           from educommon.utils.licence.converters import get_date_value

           config = dict(
               start_date=('startdate', get_date_value),
               end_date=('enddate', get_date_value),
           )
        """
        if schema_file_path:
            self.schema_file_path = os.path.abspath(schema_file_path)
        else:
            self.schema_file_path = None
        self.licence_file_path = os.path.abspath(licence_file_path)
        self._config = config
        self._params_root = params_root

    def _check_file(self, file_path):
        """Проверяет существование файла и наличие к нему доступа.

        :param basestring file_path: Путь к файлу.

        :raises django.core.exceptions.ImproperlyConfigured: если файл не
            существует, либо к нему нет доступа.
        """
        if not os.path.exists(file_path):
            raise ImproperlyConfigured(f'Licence file not found: {file_path}')

        if not os.access(file_path, os.R_OK):
            raise ImproperlyConfigured(f"Can't read licence file: {file_path}")

    @cached_property
    def _params_elements(self):
        """Возвращает XML-дерево файла лицензии.

        :rtype: list of lxml.etree._Element

        :raises LicenceError: Если при проверке возникли ошибки.
        """
        self._check_file(self.licence_file_path)
        if self.schema_file_path:
            self._check_file(self.schema_file_path)
            schema_uri = 'file://' + self.schema_file_path
        else:
            schema_uri = None

        try:
            document_tree = load_xml_document(
                document_uri='file://' + self.licence_file_path,
                schema_uri=schema_uri,
            )
        except etree.XMLSyntaxError as error:
            raise LicenceError('Error parsing licence XML document {}:\n{}'.format(self.licence_file_path, str(error)))

        result = document_tree.xpath(self._params_root)[0]

        # поскольку промежуточный результат в памяти хранить необязательно,
        # а необходим он только в 2 местах, кладем его в список 2 раза, после
        # этого достаем в каждом и не храним в памяти промежуточные результаты
        return [result, result]

    @cached_property
    def _params(self):
        """Параметры лицензии, загруженные в соответствии с конфигурацией.

        :rtype: dict
        """
        params_root_element = self._params_elements.pop()

        return {
            param_name: converter(get_text(params_root_element.xpath(xpath)))
            for param_name, (xpath, converter) in self._config.items()
        }

    @cached_property
    def plugins(self):
        """Список разрешенных к использованию плагинов.

        :rtype: set
        """
        params_root_element = self._params_elements.pop()

        return set(params_root_element.xpath('plugins/plugin/attribute::name'))

    def __getattr__(self, attr_name):
        return self._params[attr_name]
