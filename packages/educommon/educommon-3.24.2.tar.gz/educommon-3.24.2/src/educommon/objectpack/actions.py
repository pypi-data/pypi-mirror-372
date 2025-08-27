from collections import (
    OrderedDict,
)

from django.template.loader import (
    render_to_string,
)
from m3.actions import (
    OperationResult,
)
from m3_django_compat import (
    ModelOptions,
)
from m3_ext.ui.results import (
    ExtUIComponentResult,
)

from objectpack.actions import (
    BaseAction,
    BasePack,
    BaseWindowAction,
    ObjectRowsAction,
)
from objectpack.models import (
    ModelProxy,
)

from educommon.objectpack import (
    ui,
)
from educommon.objectpack.ui import (
    BaseGridWindow,
)
from educommon.utils.ui import (
    reconfigure_grid_by_access,
)


class BaseGridPack(BasePack):
    """
    Пак умеющий строить динамический грид с изменяющимся
    количеством колонок в зависимости от значений полей фильтрации.
    """

    window = BaseGridWindow

    # аттрибуты грида
    column_param_name = None
    """
    Например, для колонок из классов можно определить

    column_param_name = 'classyear_id'
    """
    row_id_name = None
    """
    Например, для строк из звонков расписания можно определить

    row_id_name = 'call_id'
    """

    @property
    def id_param_name(self):
        return f'{self.short_name}_id'

    @property
    def grid_panel(cls):
        """Класс панели с гридом.

        .. note::
            Вынесено в метод для случая, когда пак работает с гридом,
            размещенным не в окне, а, например, в табе
        """
        return cls.window.grid_panel_cls

    def __init__(self):
        super().__init__()

        self.grid_action = BaseGridCreateAction()
        self.window_action = BaseGridWinAction()
        self.actions.extend([self.grid_action, self.window_action])

    def create_columns(self, request, context):
        """Метод возвращающий колонки.

        .. seealso:: objectpack.actions.ObjectPack.columns

        :rtype: list
        """
        return []

    def create_grid(self, columns):
        """Создание грида.

        :param list columns: список колонок
        :rtype: m3_ext.ui.ExtObjectGrid
        """
        grid = self.grid_panel.create_grid(pack=self, columns=columns)

        return grid

    def set_grid_params(self, grid, request, context):
        """Настройка параметров для конфигурации грида.

        Параметры грида передаются панели с гридом в метод configure_grid.
        :param grid: грид
        :type grid: m3_ext.ui.ExtObjectGrid
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :rtype: dict
        :returns: словарь параметров для создания грида
        """
        # пак для настройки грида (column_param_name, id_param_name, url_data)
        params = {'pack': self}

        return params

    def configure_grid(self, grid, request, context):
        """Метод конфигурирования грида после его создания.

        :param grid: грид
        :type grid: m3_ext.ui.ExtObjectGrid
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        """
        params = self.set_grid_params(grid, request, context)
        grid = self.grid_panel.configure_grid(grid, params)

        return grid

    def get_grid_action_url(self):
        """Получение адреса экшна построения грид.

        :rtype: str
        """
        return self.grid_action.get_absolute_url()

    def get_rows_url(self):
        """Получение адреса экшна, возвращающего строки грида.

        Должен быть определен в потомке.
        :rtype: str
        """
        raise NotImplementedError(f'Не определен метод get_rows_url() в {self.__class__.__name__}!')

    def create_window(self, request, context):
        """Получение окна."""
        return self.window()

    def get_window_params(self, request, context):
        """Параметры для показа окна.

        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :rtype: dict

        .. note::
            Используется только если данный пак отвечает и за показ окна
            с гридом

        """
        params = {
            # пак отвечающий за получения грида окном
            'grid_pack': self
        }

        return params


class BaseGridCreateAction(BaseAction):
    """Базовый экшн построения грида."""

    perm_code = 'view'

    def run(self, request, context):
        pack = self.parent
        columns = pack.create_columns(request, context)
        grid = pack.create_grid(columns)
        pack.configure_grid(grid, request, context)

        return ExtUIComponentResult(grid)


class BaseGridWinAction(BaseWindowAction):
    """Экшн показа окна."""

    perm_code = 'view'

    def create_window(self):
        self.win = self.parent.create_window(self.request, self.context)

    def set_window_params(self):
        super().set_window_params()

        self.win_params = self.parent.get_window_params(self.request, self.context)


class ExtObjectRowsAction(ObjectRowsAction):
    def get_total_count(self):
        """В отличие от оригинала убирает из запроса лишнюю обработку данных.

        :return: Количество объектов в выборке
        :rtype: int
        """
        return self.query.select_related(None).values('id').count()


class RelationsCheckMixin:
    """Миксин для экшенов удаления и редактирования.

    Проверяет наличие ссылок на редактируемый/удаляемый объект
    и выводящий данную информацию в табличном виде.
    """

    # Описание настроек отображения информации для каждой модели.
    rel_conf = {}
    # Список с именами моделей, которые должны проверяться
    rel_list = []
    # Список с именами моделей, которые нужно исключить из проверки
    rel_ignore_list = []
    err_msg = 'На объект "{obj}" есть ссылки:'
    render_template_name = 'relations-check-mixin-template.html'

    def __init__(self, rel_conf=None, rel_list=None, rel_ignore_list=None, err_msg=None, *args, **kwargs):
        """
        :param rel_conf: настройки отображения
        :type dict
        :param rel_list: список моделей
        :type: list
        :param rel_ignore_list: список игнорироемых моделей
        :type list
        :param err_msg: сообщение об ошибке
        :type: string
        .. note::
        Пример настроек:
        rel_conf = {
            'ModelName': {
                 # Заголовок таблицы
                 'title'
                 # Колонки таблицы
                 'columns': ()
                 # Максимальное число выводимых объектов
                 'objects_limit': 30,
                 # Функция для дополнительной настройки queryset'а
                 'get_query':
                 # Функция формирующая список значений для столбцов
                 'display':

        """

        if rel_conf:
            self.rel_conf = rel_conf
        if rel_list:
            self.rel_list = rel_list
        if rel_ignore_list:
            self.rel_ignore_list = rel_ignore_list
        if err_msg:
            self.err_msg = err_msg

        super().__init__(*args, **kwargs)

    def _get_relations_to_check(self):
        """Получение всех связанных моделей для проверки."""
        model = self._get_check_model()
        opts = ModelOptions(model)
        all_related_objects = [rel_obj.relation for rel_obj in opts.get_all_related_objects()]
        result = all_related_objects[:]

        if self.rel_ignore_list:
            result = [rel for rel in all_related_objects if rel.field.model.__name__ not in self.rel_ignore_list]

        if self.rel_list:
            result = [rel for rel in all_related_objects if rel.field.model.__name__ in self.rel_list]

        return result

    def _get_check_model(self):
        """Получение модели для проверки."""

        def _extract_proxy_from_model(model):
            """Если получена не модель, а прокси, то извлекает из него модель.

            Функция рекурсивна, т.к. возможны прокси на прокси.
            """
            if issubclass(model, ModelProxy) and hasattr(model, 'model'):
                model = _extract_proxy_from_model(model.model)
            elif model._meta.proxy:
                # прокси django
                model = _extract_proxy_from_model(model._meta.proxy_for_model)

            return model

        return _extract_proxy_from_model(self.parent.model)

    def _get_objects_to_check(self, request, context):
        """Получение списка проверяемых объектов."""
        ids = getattr(context, self.parent.id_param_name, [])
        if isinstance(ids, int):
            ids = [ids]

        return self._get_check_model().objects.filter(id__in=ids)

    def collect_related_objects(self, request, context):
        """Получение списка связанных объектов.

        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext

        """

        model = self._get_check_model()
        objects = self._get_objects_to_check(request, context)
        relations = self._get_relations_to_check()

        result = OrderedDict()

        # цикл по удаляемым объектам
        for obj in objects:
            assert isinstance(obj, model)

            object_relations = result.setdefault(
                obj.id,
                {
                    'object': obj,
                    'relations': [],
                    'err_msg': self.err_msg.format(
                        model_verbose=model._meta.verbose_name.capitalize(),
                        obj=obj,
                    ),
                },
            )

            for rel in relations:
                assert getattr(rel, 'parent_model', getattr(rel, 'model')) == model

                rel_model_name = rel.field.model.__name__
                conf = self.rel_conf.get(rel_model_name, {})

                query = rel.field.model.objects.filter(**{str(rel.field.attname): obj.pk})
                if conf.get('get_query'):
                    query = conf['get_query'](query, obj)

                count = query.count()
                objects_limit = conf.get('objects_limit', 100)
                query = query[:objects_limit]

                display = conf.get('display', lambda obj: [str(obj)])
                objects = [display(o) for o in query]

                if count:
                    object_relations['relations'].append(
                        {
                            'model': rel.field.model,
                            'title': (conf.get('title') or rel.field.model._meta.verbose_name),
                            'columns': conf.get('columns'),
                            'objects': objects,
                            'count': count,
                        }
                    )

        return dict(
            items=[v for v in result.values() if v['relations']],
            model_name=model._meta.verbose_name,
        )

    def pre_run(self, request, context):
        """Вывод окна отчета.

        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext

        """

        super().pre_run(request, context)

        related_objects_data = self.collect_related_objects(request, context)

        if related_objects_data['items']:
            html = render_to_string(
                self.render_template_name,
                related_objects_data,
            )
            params = dict(html=html, width=800, height=600)
            win = ui.RelatedErrorWindow()
            win.set_params(params)

            return OperationResult(success=False, code=win.get_script())


class ViewWindowPackMixin:
    """Примесь к паку с окном просмотра.

    Добавляет кнопку просмотра в ListWindow, запрещает редактирование.
    """

    def create_edit_window(self, create_new, request, context):
        window = super().create_edit_window(create_new, request, context)

        window.make_read_only()

        return window

    def create_list_window(self, is_select_mode, request, context):
        window = super().create_list_window(is_select_mode, request, context)

        reconfigure_grid_by_access(window.grid)

        return window
