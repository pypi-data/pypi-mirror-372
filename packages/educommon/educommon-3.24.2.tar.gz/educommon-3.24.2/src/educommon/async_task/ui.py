from django.utils.html import (
    escapejs,
)
from m3_ext.ui.containers import (
    ExtContainer,
    ExtGridRowSelModel,
)
from m3_ext.ui.controls import (
    ExtButton,
)
from m3_ext.ui.fields import (
    ExtStringField,
    ExtTextArea,
)
from m3_ext.ui.icons import (
    Icons,
)
from m3_ext.ui.misc import (
    ExtDataStore,
)
from m3_ext.ui.panels import (
    ExtObjectGrid,
)

from objectpack.ui import (
    BaseWindow,
)

from educommon.async_task.helpers import (
    get_running_task_result,
    update_running_task,
)
from educommon.async_task.models import (
    AsyncTaskStatus,
)
from educommon.objectpack.ui import (
    BaseListWindow,
)
from educommon.utils.ui import (
    append_template_globals,
)


class AsyncTaskListWindow(BaseListWindow):
    """Окно списка исполняемых асинхронных задач."""

    def _init_components(self):
        """Инициализация элементов окна."""
        super()._init_components()

        self.grid.top_bar.button_view = ExtButton(
            text='Просмотр',
            icon_cls='icon-application-view-detail',
            handler='viewTask',
        )
        self.grid.top_bar.revoke_button = ExtButton(
            text='Отменить',
            handler='revokeTask',
            icon_cls=Icons.CANCEL,
        )

    def _do_layout(self):
        """Размещение элементов окна."""
        super()._do_layout()

        self.grid.top_bar.items.append(self.grid.top_bar.button_view)
        self.grid.top_bar.items.append(self.grid.top_bar.revoke_button)

    def set_params(self, params, *args, **kwargs):
        """Устанавливает параметры окна."""
        super().set_params(params, *args, **kwargs)

        append_template_globals(self, 'ui-js/async-task-list-win.js')
        append_template_globals(self, 'ui-js/async-task-revoke.js')
        self.view_url = params['view_url']
        self.revoke_url = params['revoke_url']


class AsyncTaskResultViewWindow(BaseWindow):
    """Окно результатов задачи."""

    def _init_components(self):
        """Инициализация элементов окна."""
        super()._init_components()

        self.top_region = ExtContainer(region='north', layout='form', height=80, style={'padding': '5px'})
        self.center_region = ExtContainer(region='center', layout='fit', style={'padding': '5px'})
        self.bottom_region = ExtContainer(region='south', layout='form', height=150, style={'padding': '5px'})
        self.task_type_fld = ExtStringField(anchor='100%', label='Тип', read_only=True)
        self.description_fld = ExtStringField(anchor='100%', label='Описание', read_only=True)
        self.progress_fld = ExtStringField(anchor='100%', label='Прогресс', read_only=True)
        self.error_fld = ExtTextArea(anchor='100%', label='Сообщение об ошибке', read_only=True)
        self.state_fld = ExtStringField(anchor='100%', label='Состояние задачи', read_only=True)
        self.results_grid = ExtObjectGrid(
            title='Результаты',
            layout='fit',
        )
        self.close_btn = ExtButton(text='Закрыть', handler='function() {win.close()}')

        # Кнопка "Отмена" не блокируется в режиме "только для чтения"
        self._mro_exclude_list.append(self.close_btn)

    def _do_layout(self):
        """Размещение элементов окна."""
        super()._do_layout()

        self.layout = 'border'
        self.items[:] = [self.top_region, self.center_region, self.bottom_region]
        self.center_region.items.append(self.results_grid)
        self.bottom_region.items.extend([self.progress_fld, self.state_fld, self.error_fld])
        self.top_region.items.extend([self.task_type_fld, self.description_fld])
        self.buttons.extend(
            [
                self.close_btn,
            ]
        )

    def _configure_results_grid(self, data: dict):
        """Конфигурирование грида с результатами задачи."""
        self.results_grid.header = True
        self.results_grid.sm = ExtGridRowSelModel(single_select=True)
        self.results_grid.allow_paging = False
        self.results_grid.add_column(
            header='Ключ',
            data_index='key',
            width=10,
        )
        self.results_grid.add_column(
            header='Значение',
            data_index='value',
            width=30,
        )
        rows = [(i, k, escapejs(v)) for i, (k, v) in enumerate(data.items())]
        self.results_grid.set_store(ExtDataStore(rows))

    def set_params(self, params):
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.height = 450
        self.maximizable = True

        running_task = params['object']
        task_result = get_running_task_result(running_task)
        if task_result.state and AsyncTaskStatus.from_state(task_result.state) != running_task.status:
            update_running_task(running_task.id, status=AsyncTaskStatus.from_state(task_result.state))

        self.task_type_fld.value = running_task.task_type_str
        self.description_fld.value = running_task.description
        self.progress_fld.value = task_result.progress
        self.error_fld.value = task_result.error
        self.state_fld.value = task_result.state

        self._configure_results_grid(task_result.values)
