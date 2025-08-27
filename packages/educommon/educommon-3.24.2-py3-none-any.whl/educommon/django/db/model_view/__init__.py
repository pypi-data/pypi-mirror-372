"""Средства для работы с представлениями объектов моделей.

Под представлением объекта модели подразумевается объект, задачей которого
является формирование какого-либо представления (HTML, JSON и т.п.) на основе
объекта модели.
"""

from abc import (
    ABCMeta,
    abstractmethod,
)

from django.apps import (
    apps,
)
from django.template.loader import (
    render_to_string,
)
from django.utils.encoding import (
    force_str,
)

from m3_django_compat import (
    get_model,
)

from educommon.utils.db import (
    get_field,
)
from educommon.utils.misc import (
    cached_property,
    get_nested_attr,
)
from educommon.utils.ui import (
    local_template,
)


class ModelView(metaclass=ABCMeta):
    """Базовый класс для представлений объектов модели."""

    def __init__(self, model, description=None, priority=0):
        """Инициализация класса представления модели

        Представления с бОльшим приоритетом (priority) перезаписывают уже
        зарегистированные представления, у которых приоритет ниже.
        При попытке регистрации двух моделей с одинаковым приоритетом,
        который по умолчанию 0, будет выброшено исключение

        :param model: Модель, для которой регистрируется представление
        :param description: Текстовое описание представления
        :param priority: Приоритет
        """
        self._model = model
        self._description = description
        self.priority = priority

    @cached_property
    def model(self):
        if isinstance(self._model, str):
            return apps.get_model(*self._model.split('.'))
        else:
            return self._model

    @abstractmethod
    def get_view(self, objects):
        """Возвращает представление для указанных объектов."""


# -----------------------------------------------------------------------------
# Извлечение данных из объектов


class DataExtractor(metaclass=ABCMeta):
    """Базовый класс для извлекателей данных."""

    @abstractmethod
    def get(self, obj):
        """Возвращает данные, извлеченные из объекта."""


class Text(DataExtractor):
    def __init__(self, text):
        self._text = text

    def get(self, obj):
        return self._text


class ModelVerboseName(DataExtractor):
    """Текстовое описание объекта модели."""

    def get(self, obj):
        return obj._meta.verbose_name


class ModelVerboseNamePlural(DataExtractor):
    """Текстовое описание объектов модели."""

    def get(self, obj):
        return obj._meta.verbose_name_plural


class FieldVerboseName(DataExtractor):
    """Описание поля модели."""

    def __init__(self, field_name):
        self._field_name = field_name

    def get(self, obj):
        return get_field(obj, self._field_name).verbose_name or ''


class AttrValue(DataExtractor):
    """Значение атрибута."""

    def __init__(self, field_name):
        self._field_name = field_name

    def get(self, obj):
        try:
            return get_nested_attr(obj, self._field_name) or ''
        except AttributeError:
            return ''


class JoinedAttrValues(DataExtractor):
    """Значения атрибутов через разделитель."""

    def __init__(self, delimiter=' / ', *field_names):
        self._field_names = field_names
        self._delimiter = delimiter

    def get(self, obj):
        values = []
        for field_name in self._field_names:
            try:
                value = force_str(get_nested_attr(obj, field_name) or '')
            except AttributeError:
                return ''
            else:
                values.append(value)

        return self._delimiter.join(values)


class FieldChoiceValue(DataExtractor):
    """Значение поля с choices."""

    def __init__(self, field_name):
        self._field_name = field_name

    def get(self, obj):
        field = get_field(obj, self._field_name)
        try:
            value = get_nested_attr(obj, self._field_name)
        except AttributeError:
            return ''
        else:
            return force_str(dict(field.flatchoices).get(value, value), strings_only=True)


# -----------------------------------------------------------------------------


class HtmlTableView(ModelView):
    """Представление объектов в виде таблицы HTML.

    При реализации представления необходимо описать ячейки заголовка таблицы и
    ячейки данных. Для описания содержимого ячеек следует использовать
    извлекатели данных (см. :class:`DataExtractor`).

    ::

      class SubjectOffice(models.Model):
          subject = models.ForeignKey(
              'subject.Subject',
              verbose_name='Предмет',
          )
          office = models.ForeignKey(
              'office.Office',
              verbose_name='Аудитория',
          )


      subject_office_view = HtmlTableView(
          model='subject.SubjectOffice',
          columns=(
              dict(
                  header=FieldVerboseName('subject'),
                  data=AttrValue('subject.name'),
              ),
              dict(
                  header=FieldVerboseName('office.unit.short_name'),
                  data=AttrValue('office.unit.short_name'),
              ),
              dict(
                  header=FieldVerboseName('office.cabinet_number'),
                  data=AttrValue('office.cabinet_number'),
              ),
          ),
      )
    """

    #: Путь к файлу шаблона HTML-представления.
    _template = local_template('table-view.html')

    #: Описание колонок таблицы.
    #:
    #: Каждый элемент кортежа должен быть словарем с двумя ключами - ``header``
    #: и ``data``. Каждый из них должен содержать настроенный извлекатель
    #: данных для заголовка и тела таблицы соответственно. У извлекателей
    #: данных для заголовков в метод ``get()`` в качестве аргумента будет
    #: передана модель, а в извлекатель для тела таблицы - объект модели.
    _columns = ()

    def __init__(self, model, columns, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

        self._columns = columns

    def _get_description(self, model):
        """Возвращает данные для заголовка таблицы."""
        return self._description.get(model) if self._description else None

    def _get_header_data(self, model):
        """Возвращает данные для ячеек заголовка таблицы.

        :rtype: tuple
        """
        if all(not column.get('header') for column in self._columns):
            return None

        return tuple(column['header'].get(model) for column in self._columns)

    def _get_body_data(self, objects):
        """Возвращает данные для ячеек тела таблицы.

        :rtype: tuple
        """
        return tuple(tuple(column['data'].get(obj) for column in self._columns) for obj in objects)

    def get_view(self, objects):
        """Возвращает строку с HTML-таблицей, содержащей данные объектов.

        :param objects: Объекты, для которых необходимо сформировать
            представление.
        :type objects: Iterable

        :rtype: str
        """
        if not objects:
            return ''

        assert len(set(obj.__class__ for obj in objects)) == 1, objects

        if self.model is None:
            model = objects[0].__class__
        else:
            model = self.model

        return render_to_string(
            template_name=self._template,
            context=dict(
                description=self._get_description(model),
                header=self._get_header_data(model),
                body=self._get_body_data(objects),
            ),
        )


# -----------------------------------------------------------------------------


class ModelViewRegistry:
    """Реестр представлений моделей.

    Предоставляет средства для регистрации представлений в реестре и получения
    представлений для модели.
    """

    def __init__(self, default_view=None):
        self._registry = {}
        self._default_view = default_view

    @staticmethod
    def _get_model_key(model):
        if isinstance(model, str):
            model = get_model(*model.split('.'))

        if model._meta.proxy:
            model = model._meta.proxy_for_model

        key = '.'.join((model._meta.app_label, model._meta.model_name))

        return key.lower()

    def register(self, *views):
        """Регистрация представления модели.

        :param model: Модель. Может быть задана классом модели, либо строкой
            вида 'app_label.ModelClass'.
        :type model: django.db.models.base.ModelBase or basestring

        :param view: Представление модели.
        :type view: ModelView
        """
        for view in views:
            key = ModelViewRegistry._get_model_key(view.model)
            registered_view = self._registry.get(key)

            if registered_view and registered_view is not view:
                # Сравниваем приоритеты представлений
                if registered_view.priority == view.priority:
                    raise ValueError(
                        'Для модели {} уже зарегистрировано представление {} с приоритетом {}.'.format(
                            key, view, view.priority
                        )
                    )
                elif registered_view.priority > view.priority:
                    # Пропускаем моедль, если у текущей зарегистированной
                    # модели приоритет больше
                    continue

            self._registry[key] = view

    def get(self, model):
        """Возвращает представление для указанной модели.

        :param model: Модель. Может быть задана классом модели, либо строкой
            вида 'app_label.ModelClass'.
        :type model: django.db.models.base.ModelBase or basestring

        :rtype: ModelView or None
        """
        key = ModelViewRegistry._get_model_key(model)
        if key in self._registry:
            return self._registry[key]
        elif self._default_view:
            return self._default_view
        else:
            raise ValueError('Для модели {} не зарегистрировано представление.'.format(key))


# -----------------------------------------------------------------------------


#: Реестры представлений моделей.
registries = {}
