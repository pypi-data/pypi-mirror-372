"""Набор классов для реализации справочников контингента.

BaseCatalogVirtualModel - виртуальная модель на основе JSON файла.
BaseEnumerateProductSpecific - перечисление с продуктовыми зависимостями.
BaseModelView - перечисление на основе виртуальной модели.
"""

import json
import os

from m3.db import (
    BaseEnumerate,
)

from objectpack.models import (
    VirtualModel,
)


def load_values(filename):
    """Загружает данные справочника из файла в формате JSON.

    Файл должен располагаться в папке json_data и содержать словарь значений.

    :param str filename: Имя файла (без пути!) с данными справочника.

    :rtype: dict
    """
    filepath = os.path.join(os.path.dirname(__file__), 'json_data', filename)

    with open(filepath, 'r') as infile:
        result = json.load(infile)

    assert isinstance(result, list), type(result)

    return result


class BaseCatalogVirtualModel(VirtualModel):
    """Виртуальная модель для справочников на основе JSON файла.

    Виртуальная модель на основе BaseCatalogVirtualModel выгружает данные
    из JSON файла. Каждая запись может содержать множество полей.
    JSON файл при этом должен иметь определенную структуру
    [
        // Запись в модели
        {
            "field_name1": value1,
            "field_name2": value2,
            ...
        },
        ...
    ]
    """

    id_field = None
    """Имя поля, значение которого будет являться идентификатором записи.

    Копируется в поле ``id``.
    """

    # В потомках данные заполняются вызовом
    # _load_enum_values("my-catalog.json")
    data = None

    fields_to_serialize = ['id']

    @classmethod
    def get_serialized_values(cls, ids):
        """Список сериализованных объектов для маппинга в ExtMultiSelectField."""
        return json.dumps(list(cls.objects.filter(id__in=ids).values(*cls.fields_to_serialize)))

    @classmethod
    def _get_ids(cls):
        for record in cls.data:
            if cls.id_field is not None:
                record['id'] = record[cls.id_field]
            yield record

    def __init__(self, params):
        """Инициализация объекта модели.

        :param dict params: Данные объекта модели.
        """
        super().__init__()

        for param in params:
            setattr(self, param, params[param])

    def __str__(self):
        """Строковое представление записи в виртуальной модели."""
        raise NotImplementedError


class ProductSpecific:
    """Интерфейс для продукто-зависимых перечислений.

    Предоставляет возможность выбора специально заданных
    значений из справочника для конкретного продукта.
    Для этого, при инциализации проекта, необходимо выполнить:
        EduProgramKind.set_category(EduProgramKind.WEBEDU_CODES),
    в этом случае пользователи увидят не весь справочник обр.программ по УФТТ,
    а только программы, необходимые в школах.

    Если не вызывать метод .set_category(), системе будут доступны
    полные версии справочников.
    """

    # Для каждого продукта задается список значений (ключей из value)
    WEBEDU_CODES = ()
    KINDER_CODES = ()
    SSUZ_CODES = ()
    EXTEDU_CODES = ()

    current_kind = None

    @classmethod
    def set_category(cls, list_codes):
        """Активация одной из категорий."""
        cls.current_kind = tuple(list_codes)


class BaseEnumerateProductSpecific(BaseEnumerate, ProductSpecific):
    """BaseEnumerate c ProductSpecific возможностями."""

    @classmethod
    def set_category(cls, list_codes):
        """Активация одной из категорий."""
        assert all(code in cls.values for code in list_codes), (
            'Все значения list_codes должны содержаться в values класса'
        )

        super().set_category(list_codes)

    @classmethod
    def get_choices(cls):
        """Возвращает заданные для конкретных продуктов значения."""
        codes = cls.current_kind or cls.values

        return [(k, v) for k, v in cls.values.items() if k in codes]


class BaseModelView(ProductSpecific):
    """Базовый класс для перечисления на основе виртуальной модели.

    Перечисления необходимы для создании полей модели ссылающихся
    на справочник, а также для сторов UI компонент.
    При переопределении необходимо указать
    model - модель, наследник BaseCatalogVirtualModel
    value_field - поле, выступающее в качестве значения
    display_field - поле для отображения
    """

    # Виртуальная модель. Наследники класса BaseCatalogVirtualModel.
    model = None

    # Поле, выступающее в качестве значения
    value_field = None

    # Поле для отображения
    display_field = None

    @classmethod
    def get_choices(cls):
        """Отображаем данные для выбора.

        :return: [(value_field, display_field), ...]
        """
        codes = cls.current_kind or [rec[cls.value_field] for rec in cls.model.data]

        result = (
            (record[cls.value_field], record[cls.display_field])
            for record in cls.model.data
            if record[cls.value_field] in codes
        )

        result = tuple(sorted(result, key=lambda code_name: code_name[1]))

        return result
