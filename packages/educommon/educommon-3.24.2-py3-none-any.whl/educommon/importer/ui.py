from m3_ext.ui import (
    all_components as ext,
)

from objectpack.ui import (
    BaseEditWindow,
    BaseWindow,
)


class BaseImportWindow(BaseEditWindow):
    """Базовое окно загрузки шаблона импорта."""

    def _init_components(self):
        super()._init_components()

        self.file_field = ext.ExtFileUploadField(
            anchor='100%',
            allow_blank=False,
            name='uploaded',
            label='Файл для загрузки',
        )

    def _do_layout(self):
        super()._do_layout()

        self.form.items.append(self.file_field)

    def set_params(self, params):
        super().set_params(params)

        self.height = 110
        # FIXME: При переопределении придется копипастить
        # Проброс ID окна для окна результата
        self.handler_beforesubmit = """
            function (submit) {submit.params["import_window_id"] = win.id}
        """

        self.form.file_upload = True
        self.save_btn.text = 'Загрузить'
        self.file_field.possible_file_extensions = params.get('extensions', None)


class ImportResultWindow(BaseWindow):
    """Окно для вывода результата импорта."""

    def _init_components(self):
        super()._init_components()

        self.result_field = ext.ExtTextArea(read_only=True)

        self.close_btn = ext.ExtButton(text='Закрыть', handler='function() {win.close()}')

        # Кнопка "Отмена" не блокируется в режиме "только для чтения"
        self._mro_exclude_list.append(self.close_btn)

    def _do_layout(self):
        super()._do_layout()

        self.items.append(self.result_field)
        self.buttons.extend(
            [
                self.close_btn,
            ]
        )

    def set_params(self, params):
        super().set_params(params)

        self.body_style = 'padding: 0;'
        self.layout = 'fit'
        self.modal = False

        self.result_field.value = params['result_text']


class ConfirmImportResultWindow(ImportResultWindow):
    """Окно для подтверждения импорта при наличии ошибок."""

    def _init_components(self):
        super()._init_components()

        self.confirm_import_btn = ext.ExtButton(
            text='Загрузить данные, в которых нет ошибок',
        )

    def _do_layout(self):
        super()._do_layout()

        self.buttons.insert(0, self.confirm_import_btn)

    def set_params(self, params):
        super().set_params(params)

        self.parent_window_id = params['import_window_id']

        if params.get('exit_from_import_on_close', False):
            # Закрытие окна импорта и окна результата
            self.close_btn.handler = """
                function() {
                    if (win.parentWindow) win.parentWindow.close();
                    win.close();
                }
            """

        if params.get('hide_confirm_button', False):
            self.confirm_import_btn.hidden = True
        else:
            # Хэндлер пробрасывает параметр для пропуска ошибок и снова
            # сабмитит форму импорта.
            self.confirm_import_btn.handler = """
                function() {
                    win.close();
                    win.parentWindow.actionContextJson.ignore_bad_rows = true;
                    win.parentWindow.submitForm();
                }
            """
