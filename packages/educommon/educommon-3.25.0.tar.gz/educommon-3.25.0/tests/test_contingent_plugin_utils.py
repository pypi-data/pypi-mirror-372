from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    QuerySet,
)
from django.test import (
    TestCase,
)
from m3 import (
    ApplicationLogicException,
)
from m3_django_compat import (
    get_model,
)

from educommon.contingent.contingent_plugin.utils import (
    convert_to_json,
    get_new_param_tuples,
    get_original_and_deleted_instances_info,
    get_param_value_from_deleted_model,
    get_params_from_deleted_model,
)


ContingentModelDeleted = get_model('contingent_plugin', 'ContingentModelDeleted')


class TestContingentPluginUtils(TestCase):
    """Тесты для функций из educommon.contingent.contingent_plugin."""

    # Любая django - модель, поэтому возьмём ContingentModelDeleted
    model = ContingentModelDeleted

    @classmethod
    def get_next_id(cls):
        """Получение следующей id записи.

        Нужно, поскольку в одной из функций используется lru_cache,
        поэтому нужно, чтобы id не совпадали
        """

        if not hasattr(cls, '_model_deleted_id'):
            cls._model_deleted_id = 1
        else:
            cls._model_deleted_id += 1
        return cls._model_deleted_id

    @staticmethod
    def get_content_type_for_model(model):
        """Получение ContentType для указанной модели."""

        return ContentType.objects.get_for_model(model)

    def create_contingent_model_deleted_obj(self, model, object_id, data):
        """Создание объекта модели ContingentModelDeleted."""

        obj = ContingentModelDeleted.objects.create(
            content_type=self.get_content_type_for_model(model),
            object_id=object_id,
            data=data,
        )
        return obj

    def get_params_from_deleted_model(self, data, object_id=1):
        """Запись данных и их чтение в таблице ContingentModelDeleted."""
        self.create_contingent_model_deleted_obj(model=self.model, object_id=object_id, data=data)
        return get_params_from_deleted_model(self.model, object_id)

    def test_get_params_from_deleted_model(self):
        """Тест функции get_params_from_deleted_model."""

        data_list = ['string', '', '{}', {'param1': 'param1_value', 'параметр1': 'параметр1_value'}]
        for obj_id, data in enumerate(data_list, self.get_next_id()):
            json_data = convert_to_json(data)
            params = self.get_params_from_deleted_model(json_data, object_id=obj_id)
            if isinstance(data, dict):
                self.assertDictEqual(data, params)
            else:
                self.assertEqual(data, params)

    def test_get_params_from_deleted_model_incorrect_data(self):
        """Тесты на некорректный формат json в бд."""

        data_list = ['notjson', '{param}']
        for obj_id, data in enumerate(data_list, self.get_next_id()):
            with self.assertRaises(ApplicationLogicException):
                self.get_params_from_deleted_model(data, object_id=obj_id)

    def test_get_param_value_from_deleted_model(self):
        """Тест получения значения параметра для удалённого объекта модели."""

        data = {'param1': 'param1_value', 'none_param': None}
        object_id = self.get_next_id()
        self.create_contingent_model_deleted_obj(model=self.model, object_id=object_id, data=convert_to_json(data))

        for param, expected_value in data.items():
            param_value = get_param_value_from_deleted_model(model=self.model, object_id=object_id, param_name=param)
            self.assertEqual(param_value, expected_value)

    def prepare_data_for_query_config(self):
        """Подготовка данных для проверки изменений в маппинге выгрузки."""

        params_dict = {'PARAM1': 'value1', 'PARAM2': 'value2'}
        param1, param2 = list(params_dict.keys())
        mapping_tuples = ((param1, param1, None, None), (param2, (param2, 'param_func'), None, None))
        query_config = (QuerySet().none(), mapping_tuples)

        object_id = self.get_next_id()
        self.create_contingent_model_deleted_obj(
            model=self.model, object_id=object_id, data=convert_to_json(params_dict)
        )

        return params_dict, query_config, object_id

    def test_get_new_param_tuples(self):
        """Тест замены параметров в маппинге."""

        params_dict, query_config, object_id = self.prepare_data_for_query_config()
        _, mapping_tuples = query_config

        new_param_tuples = get_new_param_tuples(mapping_tuples, self.model)
        for param_tuple in new_param_tuples:
            output_param_name, output_param_source, _, _ = param_tuple
            field_name, function = output_param_source
            new_param_value = function(object_id)

            self.assertTrue(output_param_name in params_dict)
            self.assertIsInstance(output_param_source, tuple)
            self.assertEqual(len(output_param_source), 2)
            self.assertEqual(params_dict[output_param_name], new_param_value)

    def test_get_original_and_deleted_instances_info(self):
        """Тестирование дополнения маппинга выгрузки в Контингент."""

        params_dict, query_config, object_id = self.prepare_data_for_query_config()
        _, mapping_tuples = query_config

        original_query_config, new_query_config = get_original_and_deleted_instances_info(self.model, query_config)
        self.assertIs(query_config, original_query_config)

        new_query, new_mapping_tuples = new_query_config
        self.assertEqual(new_query.count(), 1)
        self.assertEqual(new_query[0].data, convert_to_json(params_dict))
