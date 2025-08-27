from copy import (
    copy,
)

import xlrd
from m3.actions.exceptions import (
    ApplicationLogicException,
)
from m3.actions.results import (
    OperationResult,
)
from m3_django_compat import (
    get_request_params,
)

from objectpack.actions import (
    BaseAction,
    BasePack,
    BaseWindowAction,
    multiline_text_window_result,
)

from educommon.importer.loggers import (
    ImportLogger,
    SeparateImportLogger,
)
from educommon.importer.proxy import (
    fabricate_proxies,
)
from educommon.importer.proxy_import import (
    ProxyLoader,
)
from educommon.importer.ui import (
    BaseImportWindow,
    ConfirmImportResultWindow,
)
from educommon.importer.XLSReader import (
    START_ROW,
    XLSLoader,
)


class BaseImportPack(BasePack):
    """Базовый пак, реализующий действия по импорту."""

    title = ''
    result_window_title = None

    import_window = BaseImportWindow
    # result_window = BaseImportResultWindow

    # постраничные загрузчики
    loaders = {}
    # разрешенные расширения файлов
    extensions = []

    # Необходимо ли для получения loader'ов иметь возможность прочитать
    # данные файла. Ecли True, то в параметрах функции get_loaders придет
    # аргумент book, иначе пердварительного чтения не будет
    workbook_pre_reading = False

    default_import_logger_cls = ImportLogger
    separate_import_logger_cls = SeparateImportLogger

    separate_logs = False
    """Необходимо ли разделять сквозные логи на ошибки и предупреждения."""

    confirm_save_on_errors = False
    """Вызов окна подтверждения импорта при наличии ошибок."""

    def __init__(self):
        super().__init__()

        self.import_window_action = BaseImportWindowAction()
        self.import_action = BaseImportAction()
        self.import_with_confirm_action = ImportWithConfirmAction()
        self.actions.extend(
            [
                self.import_window_action,
                self.import_action,
                self.import_with_confirm_action,
            ]
        )

    def declare_context(self, action):
        """Объявлен параметр для пропуска записей с ошибками."""
        params = super().declare_context(action)

        if action in (self.import_action, self.import_with_confirm_action):
            params.update(
                {
                    'ignore_bad_rows': dict(type='boolean', default=False),
                    # ID компоненты окна импорта
                    'import_window_id': dict(type='str'),
                }
            )

        return params

    def _make_proxies_config(self, memory_file, file_name, initial_context, loaders=None):
        """Автогенерация прокси у загрузчиков для областей ячеек"""
        xls_loader = XLSLoader(memory_file)
        loaders = loaders or self.get_loaders()
        # только страницы, для которых определены загрузчики
        loaders = dict(  # имена сделаю большими и без пробелов
            (str(name).strip().upper(), loader_cls) for name, loader_cls in loaders.items()
        )
        sheets = (sheet for sheet in xls_loader._book.sheets() if sheet.name.strip().upper() in loaders)
        for sheet in sheets:
            loader_cls = loaders.get(sheet.name.strip().upper())
            # только если загрузчик имеет прокси, определяющие некую область
            if not hasattr(loader_cls, 'layout_proxies_template'):
                continue
            add_log = {}  # лог ошибок, связанных с добавлением прокси

            # Устарело, оставлено для проверки.
            # Было: "избавление от сгенерированных прокси предыдущего листа
            # при многолистовом импорте разных областей".
            # Сейчас для загрузки динамически генерируется наследник загрузчика
            # со своим атрибутом proxies, и в нем не должно быть
            # сгенерированных классов прокси.
            assert all((not getattr(proxy[1], 'was_fabricated', False) for proxy in loader_cls.proxies))
            # разбор шапок колонок, начиная со строки заголовков START_ROW
            start_row = loader_cls.xlsreader_extra.get(START_ROW, 0)
            head_data = [cell_val for cell_val in sheet.row_values(start_row)]
            for layout_str, ancestor_cls in getattr(loader_cls, 'layout_proxies_template', []):
                # сгенерированные прокси для этой области
                proxies = fabricate_proxies(ancestor_cls, layout_str, head_data)
                # дополнение загрузчика сгенерированными прокси
                for key, proxy in proxies:
                    if hasattr(loader_cls, 'add_proxy'):
                        loader_cls.add_proxy(key, proxy, add_log, initial_context)
        # будет еще одно чтение
        memory_file.seek(0)

    def get_loaders(self, request=None, context=None, book=None, **kwargs):
        """Получение постраничных загрузчиков."""
        assert self.loaders, 'Не определены прокси загрузки!'
        loaders = self.loaders.copy()

        return loaders

    def set_initial_context(self, request, context):
        """Метод позволяет изменять начальный контекст прокси загрузчика в зависимости от контекста."""
        initial_context = {}

        return initial_context

    def get_import_loader(self, request, context):
        """Возвращает инстанс импортёра."""

        _file = request.FILES.get('file_uploaded')
        file_name = get_request_params(request).get('uploaded')
        initial_context = self.set_initial_context(request, context)

        _kwargs = {
            'initial_context': initial_context,
        }
        if self.workbook_pre_reading:
            book = xlrd.open_workbook(file_contents=_file.read())
            _file.seek(0)
            _kwargs['book'] = book

        loaders = self.get_loaders(request, context, **_kwargs)

        # Создаем копии классов загрузчиков для текущего импорта.
        loaders = {
            name: type(
                loader_cls.__name__ + 'SafeCopy',
                (loader_cls,),
                {'proxies': copy(loader_cls.proxies)} if hasattr(loader_cls, 'proxies') else {},
            )
            if loader_cls
            else loader_cls
            for name, loader_cls in loaders.items()
        }

        # если загрузчик предполагает наличие прокси для областей ячеек
        # которые заранее невозможно задекларировать в описании
        self._make_proxies_config(_file, file_name, initial_context, loaders)

        ignore_bad_rows = context.ignore_bad_rows if self.confirm_save_on_errors else True
        result_logger_cls = self.separate_import_logger_cls if self.separate_logs else self.default_import_logger_cls
        # Загрузчик
        loader = ProxyLoader(
            loaders=loaders,
            _file=_file,
            file_name=file_name,
            context=initial_context,
            result_logger=result_logger_cls(ignore_bad_rows=ignore_bad_rows),
            separate_logs=self.separate_logs,
            ignore_bad_rows=ignore_bad_rows,
        )

        return loader

    def make_import(self, request, context):
        """Метод осуществляет импорт. Возвращает (лог, True/False)."""
        loader = self.get_import_loader(request, context)
        res = loader.load()

        return loader.message, res

    def get_import_window_params(self, params, request, context):
        """Параметры передаваемые окну импорта."""
        params['extensions'] = self.extensions

        return params

    def get_import_result_window_params(self, params, request, context):
        """Параметры передаваемые окну результата импорта."""
        params['title'] = self.result_window_title or self.title + ': проверка шаблона'

        return params

    def extend_menu(self, menu):
        """Размещение в меню."""
        return menu.SubMenu(
            'Администрирование', menu.SubMenu('Импорт', menu.Item(self.title, self.import_window_action))
        )


class BaseImportWindowAction(BaseWindowAction):
    """Экшн показа окна импорта."""

    perm_code = 'import'

    def create_window(self):
        self.win = self.parent.import_window()

    def set_window_params(self):
        super().set_window_params()

        params = self.win_params.copy()
        params['title'] = self.parent.title

        if not self.parent.confirm_save_on_errors:
            params['form_url'] = self.parent.import_action.get_absolute_url()
        else:
            params['form_url'] = self.parent.import_with_confirm_action.get_absolute_url()

        self.win_params = self.parent.get_import_window_params(params, self.request, self.context)

    def configure_window(self):
        pass


class BaseImportAction(BaseAction):
    """Экшн выполняющий импорт."""

    perm_code = 'import'

    def run(self, request, context):
        try:
            log_msg, success = self.parent.make_import(request, context)
        except xlrd.XLRDError:
            raise ApplicationLogicException(
                'Файл имеет неверный формат или поврежден! '
                'Пересохраните файл в формате '
                '"Microsoft Excel 97/2003 (.xls)"'
            )

        return multiline_text_window_result(success=success, data=log_msg, title=self.parent.title)


class ImportWithConfirmAction(BaseAction):
    """Экшн выполняющий импорт.

    При обнаружении ошибок в импорте, требует подтверждения
    пропуска строк с ошибками.
    """

    perm_code = 'import'
    result_window = ConfirmImportResultWindow

    def create_window(self, request, context, **params):
        """Создание окна результата логгера."""
        win = self.result_window()
        win.set_params(self.parent.get_import_result_window_params(params, request, context))

        return win

    def get_window_params_by_import_result(self, import_was_success, import_logger, request, context):
        """Формирует параметры окна результата из данных логгера."""
        return dict(
            result_text=import_logger.get_pretty_log(),
            import_window_id=context.import_window_id,
            hide_confirm_button=(
                context.ignore_bad_rows or import_was_success or import_logger.have_errors_in_all_rows()
            ),
            ignore_bad_rows=context.ignore_bad_rows,
            exit_from_import_on_close=import_was_success,
        )

    def run(self, request, context):
        """Выполнение импорта и формирование окна результата."""
        loader = self.parent.get_import_loader(request, context)

        try:
            loader.load()
        except xlrd.XLRDError:
            raise ApplicationLogicException(
                'Файл имеет неверный формат или поврежден! '
                'Пересохраните файл в формате '
                '"Microsoft Excel 97/2003 (.xls)"'
            )
        import_was_success = not loader.result_logger.has_error()
        params = self.get_window_params_by_import_result(import_was_success, loader.result_logger, request, context)
        win = self.create_window(request, context, **params)

        return OperationResult(success=import_was_success, code=win.get_script())
