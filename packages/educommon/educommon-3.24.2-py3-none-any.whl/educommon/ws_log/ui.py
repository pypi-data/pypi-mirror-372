"""Описания пользовательского интерфейса приложения логирования СМЭВ."""

from m3_ext.ui import (
    all_components as ext,
)
from m3_ext.ui.icons import (
    Icons,
)

from objectpack.ui import (
    BaseEditWindow,
    BaseListWindow,
    ModelEditWindow,
)

from educommon.ws_log.models import (
    SmevLog,
    SmevProvider,
)


class SmevLogEditWindow(ModelEditWindow.fabricate(SmevLog, field_list=['request', 'response', 'result'])):
    """Окно редактирования логов СМЭВ."""

    def set_params(self, params):
        """Настройка окна."""
        super().set_params(params)

        self.height, self.width = 800, 800

        self.make_read_only()

        for field in self.form.items:
            if isinstance(field, ext.ExtTextArea):
                field.height = 240


class SmevLogListWindow(BaseListWindow):
    """Окно списка логов СМЭВ."""

    def _init_components(self):
        """Создание компонентов окна."""
        super()._init_components()

        self.print_button = ext.ExtButton(text='Печать', handler='printSmevLogsReport', icon_cls='printer')

    def _do_layout(self):
        """Расположение компонентов окна."""
        super()._do_layout()

        self.grid.top_bar.items.append(self.print_button)
        self.grid.top_bar.button_edit.icon_cls = Icons.APPLICATION_VIEW_DETAIL

    def set_params(self, params):
        """Настройка окна."""
        super().set_params(params)

        self.maximized = True
        self.settings_report_window_url = params['settings_report_window_url']
        self.template_globals = 'ui-js/smev-logs-list-window.js'


class SmevProviderListWindow(BaseListWindow):
    """Окно списка поставщиков СМЭВ."""

    def set_params(self, params):
        super().set_params(params)

        self.width = 1000


class SmevProviderEditWindow(ModelEditWindow):
    """Окно добавления/редактирования поставщиков СМЭВ."""

    model = SmevProvider

    def set_params(self, params):
        super().set_params(params)

        self.form.label_width = 200
        self.width = 500


class SmevLogReportWindow(BaseEditWindow):
    def _init_components(self):
        """Создание компонентов окна."""
        super()._init_components()

        self.field_date_begin = ext.ExtDateField(name='date_begin', label='Дата с', allow_blank=False, anchor='100%')

        self.field_date_end = ext.ExtDateField(name='date_end', label='Дата по', allow_blank=False, anchor='100%')

        self.field_institute = ext.ExtDictSelectField(
            label='Организация',
            name='institute_id',
            display_field='code',
            anchor='100%',
            hide_trigger=False,
            hide_edit_trigger=True,
            allow_blank=False,
        )

    def _do_layout(self):
        """Расположение компонентов окна."""
        super()._do_layout()

        self.form.items.extend(
            [
                self.field_institute,
                self.field_date_begin,
                self.field_date_end,
            ]
        )

    def set_params(self, params):
        """Настройка окна."""
        super().set_params(params)

        self.height, self.width = 200, 400

        self.field_institute.pack = params['institute_pack']

        if params.get('institute'):
            self.field_institute.set_value_from_model(params['institute'])

        self.template_globals = 'ui-js/smev-logs-report-setting-window.js'
