import json
from functools import (
    partial,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from m3 import (
    ApplicationLogicException,
)

from educommon.contingent.contingent_plugin.models import (
    ContingentModelDeleted,
)
from educommon.utils.caching import (
    lru_cache,
)


JSON_ERROR_STRING = 'Произошла ошибка при попытке преобразования данных'


def json_operation(json_function, obj, error_string=None):
    """Преобразует данные в соответствии с функцией json_function.

    :param json_function: Функция для преобразования данных (скорее всего
        json.dumps или json.loads)
    :type json_function: Callable
    :param obj: Объект для преобразования
    :type obj: Any
    :param error_string: Сообщение об ошибке. Если параметр не задан
        выводится сообщение JSON_ERROR_STRING
    :type error_string: Optional[str]

    :return: Результат преобразования, который зависит от выполняемой операции
    :rtype: Any
    """

    try:
        result = json_function(obj)
    except (TypeError, ValueError) as e:
        if not error_string:
            error_string = '{} ({})'.format(JSON_ERROR_STRING, e)
        raise ApplicationLogicException(error_string)

    return result


# Функция для преобразования данных из json строки
convert_from_json_string = partial(json_operation, json.loads)
# Функция для преобразования данных в json строку
convert_to_json = partial(json_operation, json.dumps)


@lru_cache(maxsize=1)
def get_params_from_deleted_model(model, object_id):
    """Возвращает словарь с параметрами для нужного объекта модели.

    Параметры берутся из класса ContingentModelDeleted.
    Если на основе данных объекта модели нет записи,возвращается None.
    Примечание: lru_cache используется, чтобы не делать одни и те же запросы
    по тем же моделям и id, если запросы идут последовательно.

    :param model: Модель, для которой будут делаться запросы
    :param object_id: id объекта
    :type object_id: int

    :return: Словарь с параметрами из модели ContingentModelDeleted для
        конкретного экземпляра модели или None, если запись не найдена
    :rtype: Optional[dict]

    :raise: ApplicationLogicException
    """
    obj = ContingentModelDeleted.objects.filter(
        content_type=ContentType.objects.get_for_model(model), object_id=object_id
    ).first()

    if not obj:
        return

    return convert_from_json_string(obj.data)


def get_param_value_from_deleted_model(model, object_id, param_name):
    """Возвращает значение параметра для объекта модели.словаря.

    Значения параметров берутся из модели ContingentModelDeleted.
    Если для объекта нет указанного параметра, возвращается None.
    Значение в словаре также может быть None

    :param param_name: Имя параметра, значение которого нужно получить
    :type param_name: str
    :param object_id: id объекта
    :type object_id: int
    :param model: Модель, для которой будут делаться запросы

    :return: Значение параметра из словаря в модели ContingentModelDeleted
        или None, если его там нет
    :rtype: Any
    """
    params = get_params_from_deleted_model(model, object_id)
    param_value = params.get(param_name)

    return param_value


def get_new_param_tuples(params_tuples, model):
    """Для всех параметров в маппинге запросов меняет способ их получения.

    Каждый параметр запроса будет браться из таблицы
    ContingentModelDeleted, если он там есть для нужного экземпляра. Если
    параметра нет, для него возвращается None

    Пример:
        На вход методу поступает:
            (('INN', 'inn', None, None))
        На выходе метода:
            (('INN', ('object_id', partial_func, None, None))
        где partial_func - функция для получения параметра 'INN' из
            модели ContingentModelDeleted на основе id переданного объекта

    :param params_tuples: Параметры для запроса
    :type params_tuples: tuple
    :param model: Модель, для которой будут делаться запросы

    :return: Изменённые параметры для запроса
    :rtype: tuple
    """
    result_tuples = []
    for params_tuple in params_tuples:
        param_name = params_tuple[0]
        new_function = partial(get_param_value_from_deleted_model, model, param_name=param_name)
        param_tuple = (param_name, ('object_id', new_function), None, None)
        result_tuples.append(param_tuple)

    return tuple(result_tuples)


def get_original_and_deleted_instances_info(model, query_config):
    """Дополнение маппинга выгрузки запросом к значениям удалённых объектов.

    :param query_config: "конфигурация запроса" - кортеж типа
        (запрос к модели, кортеж, содержащий кортежи с описанием
        параметров и способов их получения).
    :type query_config: Tuple[QuerySet, tuple]
    :param model: Модель, для которой будут делаться запросы

    :return: кортеж с параметрами запросов без изменений,
        а второй элемент - кортеж с заменёнными параметрами
        запросов для получения данных об удалённых записях моделей
    :rtype: Tuple[Tuple[QuerySet, tuple], Tuple[QuerySet, tuple]]
    """
    model_content_type = ContentType.objects.get_for_model(model)
    new_query = ContingentModelDeleted.objects.filter(content_type=model_content_type)

    _, params_tuples = query_config
    new_param_tuples = get_new_param_tuples(params_tuples, model)

    deleted_objects_query_config = new_query, new_param_tuples

    return query_config, deleted_objects_query_config
