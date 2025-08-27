from educommon.report.constructor.base import (
    ModelDataSourceParams,
)


class DataSourceParamsRegistry:
    """Реестр параметров данных.

    При первом чтении из реестра отправляет сигнал ``init`` для добавления
    в реестр параметров для источников данных системы. Каждое django-приложение
    должно в обработчике этого сигнала зарегистрировать свои параметры
    источников данных.
    """

    def __init__(self):
        """Инициализация реестра.

        По завершении инициализации отправляет сигнал ``post_init``.
        """
        self._data_sources_params = {}

    def register(self, data_source_params):
        """Регистрация параметров источника данных."""
        assert isinstance(data_source_params, ModelDataSourceParams)
        assert data_source_params.name
        assert data_source_params.name not in self._data_sources_params

        self._data_sources_params[data_source_params.name] = data_source_params

    def get(self, data_source_name):
        """Возвращает параметры источника данных по имени.

        :param str data_source_name: Имя источника данных.
        """
        return self._data_sources_params[data_source_name]

    def __contains__(self, key):
        return key in self._data_sources_params

    def iterkeys(self):
        return self._data_sources_params.keys()

    def itervalues(self):
        return self._data_sources_params.values()

    def iteritems(self):
        return self._data_sources_params.items()


registry = DataSourceParamsRegistry()
