from functools import (
    partial,
)

from typing import (
    Any,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
)

from django.core.exceptions import (
    ValidationError,
)
from m3 import (
    ApplicationLogicException,
    OperationResult,
)

from objectpack.actions import (
    BaseAction,
    BaseWindowAction,
    ObjectPack,
)
from objectpack.filters import (
    FilterByField,
)

from educommon.async_task.helpers import (
    revoke_async_tasks,
)
from educommon.async_task.models import (
    AsyncTaskStatus,
    AsyncTaskType,
    RunningTask,
)
from educommon.async_task.ui import (
    AsyncTaskListWindow,
    AsyncTaskResultViewWindow,
)
from educommon.objectpack.filters import (
    ColumnFilterEngine,
)
from educommon.utils.ui import (
    ChoicesFilter,
)

if TYPE_CHECKING:
    from django.db.models.query import (
        QuerySet,
    )


class AsyncTaskPack(ObjectPack):
    """Пак асинхронных задач."""

    title = 'Асинхронные задачи'
    width, height = 800, 400
    model = RunningTask
    list_sort_order = ('-queued_at', 'task_type', 'status')

    list_window = AsyncTaskListWindow
    view_result_window = AsyncTaskResultViewWindow

    _menu_icon: Optional[str] = None
    """css-класс иконки в главном меню."""

    can_delete = False

    filter_engine_clz = ColumnFilterEngine
    _ff = partial(FilterByField, model)

    columns = [
        {
            'data_index': 'get_queued_at_display',
            'header': 'Задача начата',
            'width': 5,
            'filter': _ff(
                'queued_at',
                'queued_at__date',
            ),
        },
        {
            'data_index': 'task_type_str',
            'header': 'Тип задачи',
            'width': 5,
            'sortable': True,
            'sort_fields': ('task_type_id',),
            'filter': ChoicesFilter(
                choices=[(value.key, value.title) for value in AsyncTaskType.get_model_enum_values()],
                parser=str,
                lookup='task_type_id',
            ),
        },
        {
            'data_index': 'description',
            'header': 'Описание задачи',
            'width': 9,
            'filter': _ff('description', 'description__icontains'),
        },
        {
            'data_index': 'get_user_profile_display',
            'header': 'Пользователь',
            'width': 8,
            'sortable': False,
        },
        {
            'data_index': 'status_str',
            'header': 'Статус задачи',
            'width': 5,
            'sortable': True,
            'sort_fields': ('status_id',),
            'filter': ChoicesFilter(
                choices=[(value.key, value.title) for value in AsyncTaskStatus.get_model_enum_values()],
                parser=str,
                lookup='status_id',
            ),
        },
    ]

    def __init__(self):
        super().__init__()

        self.view_result_action = ViewResultWindowAction()
        self.revoke_task_action = RevokeAsyncTaskAction()
        self.actions.extend(
            (
                self.view_result_action,
                self.revoke_task_action,
            )
        )

    def declare_context(self, action):
        """Декларация контекста."""
        context = super().declare_context(action)

        if action is self.revoke_task_action:
            context.update(
                async_task_ids={'type': 'str', 'default': ''},
            )

        return context

    def get_list_window_params(self, params, request, context):
        """Получение параметров окна списка."""
        params = super().get_list_window_params(params, request, context)

        params['view_url'] = self.view_result_action.get_absolute_url()
        params['revoke_url'] = self.revoke_task_action.get_absolute_url()

        return params

    def _collect_extend_menu_kwargs(self) -> Dict[str, Any]:
        """Сбор именованных аргументов для создания пункта меню."""
        kwargs = {}
        if self._menu_icon:
            kwargs['icon'] = self._menu_icon

        return kwargs

    def extend_menu(self, menu):
        """Пункт меню."""
        kwargs = self._collect_extend_menu_kwargs()

        return menu.Item(self.title, self.list_window_action, **kwargs)


class ViewResultWindowAction(BaseWindowAction):
    """Экшн окна просмотра результатов."""

    perm_code = 'view'

    def set_window_params(self):
        """Установка параметров окна."""
        try:
            running_task, _ = self.parent.get_obj(self.request, self.context)
        except self.parent.get_not_found_exception():
            raise ApplicationLogicException(self.parent.MSG_DOESNOTEXISTS)

        self.win_params.update(
            title='Состояние задачи',
            height=self.parent.height,
            width=self.parent.width,
            read_only=True,
            object=running_task,
        )

    def create_window(self):
        """Создание экземпляра окна."""
        self.win = self.parent.view_result_window()


class RevokeAsyncTaskAction(BaseAction):
    """Экшен отмены выполнения задачи.

    Завершает выполнение задачи. Изменяет их статусы на "Отменена".
    """

    def run(self, request, context):
        """Выполнение экшена."""
        running_tasks = self._get_running_tasks(context.async_task_ids.split(','))
        task_id_to_status = {task.id: task.status for task in running_tasks.only('id', 'status')}
        all_tasks_are_cancellable = all(AsyncTaskStatus.is_cancellable(status) for status in task_id_to_status.values())
        if not all_tasks_are_cancellable:
            return OperationResult(success=False, message='Необходимо выбрать только те задачи, которые запущены!')

        to_revoke_task_ids = [
            str(task_id) for task_id, status in task_id_to_status.items() if AsyncTaskStatus.is_cancellable(status)
        ]

        revoke_async_tasks(to_revoke_task_ids)

        return OperationResult()

    def _get_running_tasks(self, ids: List[str]) -> 'QuerySet[RunningTask]':
        """Возвращает кварисет асинхронных задач."""
        try:
            running_task_qs = self.parent.model.objects.filter(id__in=ids)
        except ValidationError:
            running_task_qs = self.parent.model.objects.none()

        return running_task_qs
