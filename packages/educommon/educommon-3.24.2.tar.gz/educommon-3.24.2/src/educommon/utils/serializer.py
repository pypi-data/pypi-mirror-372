"""Инструменты для сериализации моделей."""

from collections import (
    defaultdict,
)

from django.core import (
    serializers,
)
from django.db.models import (
    ForeignKey,
)
from django.db.models.query import (
    QuerySet,
)
from m3_django_compat import (
    ModelOptions,
    get_related,
)


class SerializeQueue:
    """Выборочная сериализация данных из разных моделей в JSON.

    Производит сериализацию моделей со всеми зависимостями от них в фикстуру,
    которую затем можно загрузить через команду loaddata

    Пример применения:

    # всё, что было раньше этой даты не будет сохранено и восстановлено
    limit_date = date(2013, 8, 31)

    # необходимые периоды
    required_periods = Period.objects.filter(
        date_begin__gt=limit_date
    ).values_list(
        'id', flat=True
    )

    # физ.лица
    persons = Person.objects.filter(id__in=person_list)

    # сотрудники
    teachers = Teacher.objects.filter(id__in=teacher_list)

    # профили пользователей
    user_profiles = UserProfile.objects.filter(
        person_id__in=person_list
    )

    # Сериализация с учётом валидных периодов
    # То есть всем кверисетам, при наличии ссылки на модель Period будет
    # добавлен фильтр period__in=required_periods
    sq = SerializeQueue(
        include={
            'Period': required_periods,
        }
    )

    # Добавить физ.лица
    sq.add_objects(persons)

    # Добавить профили
    sq.add_objects(user_profiles)

    # добавить логины пользователей
    users = User.objects.filter(userprofile__in=user_profiles)
    sq.add_objects(users)

    # добавить сотрудников и все модели, которые на них ссылаются и потом
    # все, кто ссылается на тех, кто ссылается и т.д.
    sq.add_related_objects(teachers)

    # всё что накоплено - в файл
    sq.serialize(filename)

    Примечание! Некоторые модели, имеющие ссылки на другие модели, включенные
    в список условий include или exclude могут иметь праметр Null=True в
    ForeignKey и не попасть под фильтрацию.
    Например, в ЭШ, модель SubjectPlan (КТП) может иметь ссылку на ClassYear,
    а может и нет.

    """

    def __init__(self, include=None, exclude=None, **kwargs):
        """Накопление и сериализация

        :param include: модели и объекты для условия "__in"
        :param exclude: модели и объекты для операции ".exclude()"
        """
        # контейнер для добавляемых объектов
        self._objects = []
        # кеш уже добавленных моделей и объектов, чтобы избежать повторов
        self._model_cache = defaultdict(list)
        # условия вхождения - список моделей и инстансов
        self._include_conditions = {} if include is None else include
        # условия исключения - список моделей и инстансов
        self._exclude_conditions = {} if exclude is None else exclude

    def _object_in_cache(self, model_name, obj_id):
        """Проверить наличие объекта в кеше."""
        objects = self._model_cache.get(model_name)
        if objects:
            return obj_id in objects
        else:
            return False

    def _add_object_to_cache(self, model_name, obj_id):
        """Добавить объект в кеш."""
        self._model_cache[model_name].append(obj_id)

    def _ext_filter(self, query_set):
        """Фильтрация кверисета c учётом условий вхождения и исключения

        :param query_set:
        :return:
        """
        fields = self.all_foreign_keys(query_set.model)
        for field, rel_model in fields:
            # добавление условий по внешним ключам
            attname = field.attname
            if attname.endswith('_id'):
                attname = attname.replace('_id', '')
                attname = f'{attname}__in'
            # добавление фильтра вхождения
            objects = self._include_conditions.get(rel_model._meta.object_name)
            if objects:
                query_set = query_set.filter(**{attname: objects})
            # добавление фильтра исключения
            objects = self._exclude_conditions.get(rel_model._meta.object_name)
            if objects:
                query_set = query_set.exclude(**{attname: objects})

        return query_set

    @staticmethod
    def all_foreign_keys(model):
        """Возвращает список внешних ссылок для заданной модели

        :param model: Класс модели
        :return: список кортежей вида [(поле, ссылочная модель), ...]
        """
        return [
            (field, get_related(field).parent_model) for field in model._meta.fields if isinstance(field, ForeignKey)
        ]

    @staticmethod
    def related_objects(obj):
        """Возвращает список кверисетов зависимых моделей

        :param obj:
        :return:
        """
        _relations = ModelOptions(obj).get_all_related_objects()
        result = []

        for rel in _relations:
            _attname = rel.field.attname
            if _attname.endswith('_id'):
                _attname = _attname.replace('_id', '')
            _attname = f'{_attname}__pk'
            # Пытаемся определить наличие зависимых объектов:
            rel_qs = rel.field.model.objects.filter(**{str(_attname): obj.id})
            if rel_qs.exists():
                result.append(rel_qs)

        return result

    def add_objects(self, query_set, filtered=True):
        """Добавить объекты пачкой.

        :param query_set: Кверисет, возвращающий объекты моделей
        :param filtered: флаг, применять или нет общую фильтрацию
        :return:
        """
        assert isinstance(query_set, QuerySet), type(query_set)

        if filtered:
            query_set = self._ext_filter(query_set)
        for obj in query_set:
            # добавить объект
            if not self._object_in_cache(str(obj.__class__), obj.id):
                self._objects.append(obj)
                self._add_object_to_cache(str(obj.__class__), obj.id)

    def add_related_objects(self, query_set, filtered=True):
        """Добавить объекты пачкой с учётом зависимых.

        :param query_set: Кверисет, возвращающий объекты моделей
        :param filtered: флаг, применять или нет общую фильтрацию
        """
        assert isinstance(query_set, QuerySet), type(query_set)

        if filtered:
            query_set = self._ext_filter(query_set)

        for obj in query_set:
            # сначала добавить сам объект
            if not self._object_in_cache(str(obj.__class__), obj.id):
                self._objects.append(obj)
                self._add_object_to_cache(str(obj.__class__), obj.id)
            # затем добавить всех, кто на него ссылается
            for new_query_set in self.related_objects(obj):
                # рекурсивно позвать себя
                self.add_related_objects(new_query_set, filtered)

    def serialize(self, filename):
        """Собственно, сериализация в файл

        :param filename: имя файла
        """
        data = serializers.serialize('json', self._objects, indent=4)
        with open(filename, 'wb') as json_out:
            json_out.write(data)
