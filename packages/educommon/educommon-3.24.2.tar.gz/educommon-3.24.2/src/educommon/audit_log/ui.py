from m3_ext.ui.containers import (
    ExtContainer,
)
from m3_ext.ui.fields import (
    ExtStringField,
)
from m3_ext.ui.panels import (
    ExtObjectGrid,
)

from objectpack.ui import (
    BaseWindow,
)

from educommon.utils.ui import (
    formed,
)


class ViewChangeWindow(BaseWindow):
    """Окно просмотра изменений."""

    def _init_components(self):
        """Метод создаёт визуальные компоненты.

        Метод отражает поля модели, но не определяет расположение компонентов в окне.
        """
        super()._init_components()

        self.grid = ExtObjectGrid(region='center')
        self.grid.add_column(data_index='name', header='Поле')
        self.grid.add_column(data_index='old', header='Старое значение')
        self.grid.add_column(data_index='new', header='Новое значение')
        self.grid.top_bar.hidden = True

        self.user_field = ExtStringField(label='Пользователь')
        self.unit_field = ExtStringField(label='Учреждение')
        self.top_region = ExtContainer(region='north', layout='hbox', height=32)

    def _do_layout(self):
        """Метод располагает уже созданные визуальные компоненты на окне."""
        super()._do_layout()

        self.layout = 'border'
        self.width, self.height = 750, 400

        self.grid.cls = 'word-wrap-grid'

        self.top_region.items.extend(
            (
                formed(self.user_field, flex=1, style=dict(padding='5px')),
                formed(self.unit_field, flex=1, style=dict(padding='5px')),
            )
        )
        self.items.extend((self.top_region, self.grid))

    def set_params(self, params):
        """Метод принимает словарь, содержащий параметры окна, передаваемые в окно слоем экшнов."""
        self.grid.action_data = params['grid_action']
        log_record = params['object']
        self.title = '{}: {}'.format(log_record.get_operation_display(), log_record.model_name)
        if log_record.user:
            self.user_field.value = f'{log_record.user_fullname} / {log_record.user.username}'
            self.unit_field.value = log_record.user_organization
