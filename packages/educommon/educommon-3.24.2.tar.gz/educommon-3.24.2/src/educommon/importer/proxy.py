import collections

import django
from django.db import (
    transaction,
)
from django.db.models import (
    Q,
)

from objectpack.exceptions import (
    ValidationError,
)

from educommon.importer.loggers import (
    ImportLogger,
)
from educommon.importer.XLSReader import (
    SUBTREE_CAN_BE_EMPTY,
    MaybeStringCell,
)
from educommon.m3 import (
    transaction_context,
)


class SafeDict(dict):
    @classmethod
    def _wrap(cls, value):
        if not value:
            if isinstance(value, dict):
                return cls()
            else:
                return value
        try:
            return cls(value)
        except TypeError:
            return value
        except ValueError:
            return value

    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, attr):
        return self._wrap(self[attr])

    def get(self, key, default=None):
        return self._wrap(dict.get(self, key, default))

    def pop(self, *args, **kwargs):
        try:
            return self._wrap(dict.pop(self, *args, **kwargs))
        except KeyError:
            return None

    def copy(self):
        return self._wrap(super().copy())


class ProxySaveError(Exception):
    pass


class ProxyCriticalError(Exception):
    """
    Рейзится если нужно прервать процесс загрузки КТП
    в произвольном месте, с выводом ошибки
    """


class ProxyWarning(Exception):
    """Исключение возникает, когда данные одного прокси не обработаны, но
    необходимо продолжить обработку строки в шаблоне."""


class _ImportProxy:
    """Прототип proxy для загрузки данных."""

    # описание ячеек
    cells_config = {
        # 'key': cell
        # 'subdict': {
        #    'key', cell
        # }
    }

    # шапки по-умолчанию
    default_headers = {
        # 'key': 'шапка'
    }

    @classmethod
    def _must_be_executed_anyway(cls, is_optional=False):
        """
        Метод возвращает признак того, должен ли вызываться proxy
        в том случае, когда для него нет данных (при принудительном вызове
        данные будут пусты)
        is_optional - флаг опциональности proxy с точки зрения loader`а
        """
        return not is_optional

    @classmethod
    def __make_config(cls, headers):
        """Создание конфигурации колонок для XLSLoader`а."""
        if headers:
            if isinstance(headers, str):
                # "шапки" могут быть переданы в виде форматирующей строки
                fmt, headers = headers, {}
                for key, val in cls.default_headers.items():
                    headers[key] = fmt % val
            else:
                _h = (cls.default_headers or {}).copy()
                _h.update(headers)
                headers = _h
        else:
            headers = cls.default_headers or {}

        # добавление "шапок" столбцов к конфигу ячеек
        def add_headers(src, path=''):
            result = {}
            for key, val in src.items():
                path_w_key = f'{path}__{key}' if path else key
                try:
                    val = add_headers(val, path_w_key)
                except AttributeError:
                    val = (headers[path_w_key], val)
                result[key] = val
            return result

        return add_headers(cls.cells_config)

    def __init__(self, key, context):
        """Проверка зависимостей.

        Если контекст не содержит требуемых данных, должно
        возбуждаться исключение AssertionError.
        """
        assert key
        self._key = key
        self._context = context

    def _load(self, data):
        """Загрузка данных из словаря data.

        Допустимое исключение - ProxySaveError.
        """
        raise NotImplementedError()


class ModelProxy(_ImportProxy):
    """Обёртка для импорта модели."""

    # модель
    model = None


class CacheProxy(_ImportProxy):
    """Обёртка для кэша объектов."""

    model = None

    # если задано сообщение, оно будет выведено в случае
    # неудачного поиска в базе. Если не задано - будет возвращено None
    msg_not_exist = None

    # если задано сообщение, оно будет выведено в случае нескольких подходящих
    # объектов в базе. Если не задано - будет возбуждено исключение
    msg_multiple = None

    def __init__(self, key, context):
        super().__init__(key, context)

        self._key = f'{self._key}_cache'
        self._cache = context.setdefault(self._key, {})

    def _make_identity(self, data):
        """Преобразование данных в параметры для get()."""
        return data

    def _load(self, data):
        """Возврат объекта из кэша, а если его там нет, то из базы."""

        def wrap_to_q(x):
            if isinstance(x, dict):
                return Q(**x)
            else:
                return x

        def default():
            try:
                obj = self.model.objects.get(wrap_to_q(self._make_identity(data)))
                obj._imported_object = True
                return obj

            except self.model.DoesNotExist:
                if self.msg_not_exist:
                    raise ProxySaveError(self.msg_not_exist)

            except self.model.MultipleObjectsReturned:
                if self.msg_multiple:
                    raise ProxySaveError(self.msg_multiple)
                raise

            return None

        cache_key = tuple(sorted(data.items(), key=lambda x: x[0]))
        if cache_key not in self._cache:
            self._cache[cache_key] = default()

        return self._cache[cache_key]


class ContextAdapterProxy(_ImportProxy):
    """Прокси для преобразования контекста."""

    @classmethod
    def _must_be_executed_anyway(cls, is_optional=False):
        """Данный прокси вызывается всегда, т.к. обычно не требует данных."""
        return True

    @classmethod
    def make_copier(cls, src_key):
        """Конструирует простой копирующий адаптер.

        При загрузке извлекает значение по ключу src_key из контекста и возвращает его.
        """

        class SimpleCopyingAdepter(cls):
            def _load(self, data):
                return self._context[src_key]

        return SimpleCopyingAdepter

    @classmethod
    def make_mover(cls, src_key):
        """Конструирует простой копирующий адаптер.

        При загрузке извлекает значение по ключу src_key из контекста и возвращает его,
        а значение контекста по ключу заменяется на None.
        """

        class SimpleCopyingAdepter(cls):
            def _load(self, data):
                result = self._context[src_key]
                self._context[src_key] = None
                return result

        return SimpleCopyingAdepter

    @classmethod
    def make_setter(cls, value):
        """Конструирует адаптер, который просто возвращает указанное значение."""

        class SimpleCopyingAdepter(cls):
            def _load(self, data):
                return value

        return SimpleCopyingAdepter


class LayoutModelProxy(ModelProxy):
    """Прокси для загрузки области данных."""

    # словари будут сгенерированы в api
    cells_config, default_headers = None, None

    # Модель объектов используемая в строке заголовков
    layout_header_model = None
    # Хранилище объектов строки заголовков
    layout_header = {}
    # Конфигурация областей ячеек, за которые отвечает этот прокси
    # Области не должны пересекаться!
    # -- example -- #
    layouts_config = {
        # имя области
        'classyear': {
            # начальная колонка
            'start_col': 1,
            # до последней записи в строке заголовков
            'end_col': None,
            # тип ячейки для этой области
            'cell_type': MaybeStringCell(),
            # отдельные прокси для каждого столбца области
            'use_separated_proxy': True,
        },
    }

    @staticmethod
    def create_header(proxy, context):
        """Построение кэша объектов, используемых в заголовках области.

        Вызывается при добавлении в лоадер.
        """
        raise NotImplementedError()


class MultiProxyLoader:
    """Прокси загрузки нескольких моделей."""

    # начальный контекст импорта
    initial_context = {}

    # proxy моделей в порядке приоритета
    proxies = [
        # (ключ_контекста, класс_обёртки)
    ]

    # словарь донастройки "шапок" под конкретный случай
    headers = {
        # 'ключ_контекста': { словарь заголовков } | строка форматирования
    }

    # конфигурация опциональности проксей
    optionals = {}

    # строка форматирования сообщений об ошибках
    error_format = None

    # настройки для xlsreader
    xlsreader_extra = {
        # XLSReader.START_ROW: 5,
    }

    # откат загрузки всего листа при ошибке хотя бы в одной строке
    rollback_all = False

    # методы, помеченные декоратором delay_in_situations('import'),
    # будут ожидать завершения транзакций импорта
    default_delay_situation = 'import'  # по-умолчанию

    LOAD_ERROR_MSG = 'Лист не был загружен!'

    @classmethod
    def make_header_context(cls, header_data, context):
        """Преобразование данных шапки.

        При возвращении непустого списка ошибок - прекращение загрузки листа.
        """
        header_context = {}
        errors = []

        return header_context, errors

    @classmethod
    def load_rows(cls, header_data, rows_data, parse_log, log, context, warning_log=None, result_logger=None):
        """Загрузка строк листа.

        Логи разделены с целью дать возможность потомку принять решение
        о дальнейшей загрузке, если были ошибки парсинга ячеек

        :param dict parse_log: лог парсинга типов ячеек
        :param dict log: сквозной лог импорта
        :param dict warning_log: лог с предупреждениями импорта
        :param result_logger: общий логгер в который записывается вся инф-ия
        :type result_logger:
            educommon.importer.loggers.BaseImportLogger or None
        """
        # Заглушка, т.к. result_log должен быть обязательным параметром
        if result_logger is None:
            result_logger = ImportLogger()
        # Флаг игнорирует строки с ошибками и сохраняет валидные данные.
        ignore_bad_rows = context['ignore_bad_rows']
        xls_pos = context['XLS_POS']
        log.update(parse_log)

        # обработчик данных шапки листа
        transaction.enter_transaction_management()
        try:
            header_context, errors = cls.make_header_context(header_data, context)

        except Exception:
            transaction.rollback()
            raise

        if errors:
            # были ошибки в шапке листа, дальше лист не грузится
            row_info = rows_data[0][xls_pos]
            sheet = row_info[0]
            result_logger.on_header_errors(sheet, errors)
            errors.append(cls.LOAD_ERROR_MSG)
            log[row_info] = errors
            transaction.rollback()
        else:
            # Управление транзакцией листа с откладыванием действий (сигналов),
            # помеченных декоратором @delay_in_situations(delay_situation).
            # Определение ситуаций.
            if context:
                delay_situation = context.get('delay_situation', cls.default_delay_situation)
            else:
                delay_situation = cls.default_delay_situation

            # "внешняя" транзакция
            with transaction_context.TransactionCM(delay_situation) as outer_t:
                _errors = []  # построчные ошибки на листе
                for row in rows_data:
                    # менеджер делает сейвпоинты и комитить их по выходу
                    # (если все ок) автоматически
                    with transaction_context.SavePointCM() as inner_t:
                        proxyloader = cls()
                        proxyloader._context.update(header_context)
                        if context:
                            proxyloader._context.update(context)

                        try:
                            errors, warnings = proxyloader.load(row)
                            result_logger.on_row_processed(row[xls_pos])
                            result_logger.on_row_errors(row[xls_pos], errors, warnings)
                        except ProxyCriticalError as err:
                            log.setdefault(row[xls_pos], []).extend([str(err)])
                            _errors.append(str(err))
                            result_logger.on_row_errors(row[xls_pos], [str(err)])

                            # XXX при данном эксепшене нужно предотвратить
                            # повторное выполнение load, поэтому откатываем
                            # НЕ через raise или inner_t.rollback
                            transaction.savepoint_rollback(inner_t._sid)
                            # откатываем внешний блок
                            transaction.rollback(outer_t._using)
                            transaction.leave_transaction_management(using=outer_t._using)
                            break

                        if warnings:
                            # предупреждения выводятся отдельно
                            if warning_log is not None:
                                warning_log.setdefault(row[xls_pos], []).extend(warnings)
                            else:
                                log.setdefault(row[xls_pos], []).extend(warnings)

                        # предусмотренные ошибки, а все непредвиденные всплывут
                        if errors:  # предвиденные складываем
                            _errors.append(errors)  # в ошибки листа
                            # и в общий лог
                            log.setdefault(row[xls_pos], []).extend(errors)
                            # откатываем вложенную транзакцию (всю строку)
                            # если это не загрузчик прокси с областями
                            if not hasattr(proxyloader, 'layout_proxies_template'):
                                inner_t.rollback()
                                result_logger.on_row_save_rollback(row[xls_pos])
                        else:
                            result_logger.on_row_save(row[xls_pos])
                # если были ошибки и нужно откатить всё
                # FIXME: Если rollback_all == True, то независимо от флага
                # FIXME: игнора, будет происходить откат
                if _errors and (cls.rollback_all or not ignore_bad_rows):
                    log.setdefault(row[xls_pos][:2] + ('',), []).extend(
                        [
                            cls.LOAD_ERROR_MSG,
                        ]
                    )
                    outer_t.rollback()
                    result_logger.on_save_rollback()

    if django.VERSION[:2] >= (1, 6):
        # Для Django >= 1.6 метод загрузки строк переписан
        # с использованием transaction.atomic
        @classmethod
        @transaction.atomic
        def load_rows(cls, header_data, rows_data, parse_log, log, context, warning_log=None, result_logger=None):
            """Загрузка строк листа.

            Логи разделены с целью дать возможность потомку принять решение
            о дальнейшей загрузке, если были ошибки парсинга ячеек.

            :param dict parse_log: лог парсинга типов ячеек
            :param dict log: сквозной лог импорта
            :param dict warning_log: лог с предупреждениями импорта
            :param result_logger: общий логгер в который записывается вся
                инф-ия
            :type result_logger:
                educommon.importer.loggers.BaseImportLogger or None
            """
            # Заглушка, т.к. result_log должен быть обязательным параметром
            if result_logger is None:
                result_logger = ImportLogger()
            # Флаг игнорирует строки с ошибками и сохраняет валидные данные.
            ignore_bad_rows = context['ignore_bad_rows']
            xls_pos = context['XLS_POS']
            log.update(parse_log)
            rows_errors = []  # построчные ошибки на листе

            def add_log(row, items):
                if items:
                    log.setdefault(row[xls_pos], []).extend(items)

            def add_warn(row, items):
                if items:
                    if warning_log is not None:
                        warning_log.setdefault(row[xls_pos], []).extend(items)
                    else:
                        add_log(row, items)

            # обработчик данных шапки листа
            header_context, header_errors = cls.make_header_context(header_data, context)

            if header_errors:
                # были ошибки в шапке листа, дальше лист не грузится
                add_log(rows_data[0], header_errors + [cls.LOAD_ERROR_MSG])
                sheet = rows_data[0][xls_pos][0]
                result_logger.on_header_errors(sheet, header_errors)
                transaction.set_rollback(True)

                return

            @transaction.atomic
            def load_one_row(row):
                proxyloader = cls()
                proxyloader._context.update(header_context or {})
                proxyloader._context.update(context or {})

                errors, warnings = proxyloader.load(row)
                add_warn(row, warnings)
                add_log(row, errors)
                result_logger.on_row_processed(row[xls_pos])
                result_logger.on_row_errors(row[xls_pos], errors, warnings)

                if errors:
                    # FIXME: Следующее условие является костылем и в идеале
                    # его вообще не должно быть - транзакия просто должна
                    # откатываться без каких либо проверок.
                    # Если это не загрузчик прокси с областями
                    if not hasattr(proxyloader, 'layout_proxies_template'):
                        # откатываем транзакцию (всю строку)
                        transaction.set_rollback(True)
                        result_logger.on_row_save_rollback(row[xls_pos])
                else:
                    result_logger.on_row_save(row[xls_pos])

                return errors

            for row in rows_data:
                try:
                    rows_errors.extend(load_one_row(row))
                except ProxyCriticalError as err:
                    rows_errors.append(str(err))
                    add_log(row, [str(err)])
                    result_logger.on_critical_error(row[xls_pos], str(err))
                    break

            # если были ошибки и нужно откатить всё
            # FIXME: Если rollback_all == True, то независимо от флага
            # FIXME: игнора, будет происходить откат
            if result_logger.has_error() and (cls.rollback_all or not ignore_bad_rows):
                key = row[xls_pos][:2] + ('',)
                log.setdefault(key, []).extend([cls.LOAD_ERROR_MSG])

                transaction.set_rollback(True)
                result_logger.on_save_rollback()

    @classmethod
    def make_config(cls):
        """Создание конфигурации для XLSLoader`а."""

        def prepare_headers(raw_headers):
            """Подготовка заголовка.

            Если на входе строка, она оборачивается в словарь-подобный объект,
            который на любой ключ возвращает эту строку.
            Если на входе словарь - он остаётся словарём.
            """
            if isinstance(raw_headers, str):

                class StrAsDict:
                    def __init__(self, value):
                        self._value = value

                    def __getitem__(self, key):
                        return self._value

                    def get(self, key, default=None):
                        if isinstance(default, dict):
                            return self
                        return self._value

                return StrAsDict(raw_headers)

            return raw_headers

        def make_subconfig(headers, options):
            def inner(item):
                # получаем подопции
                key, value = item
                if not isinstance(options, bool):
                    sub_options = options.get(key, False)
                else:
                    sub_options = options

                # устанавливаем признак опциональности поддерева конфига
                # если подопции выродились в булев флаг
                if sub_options is True:
                    sub_config = {SUBTREE_CAN_BE_EMPTY: True}
                else:
                    sub_config = {}

                try:
                    # пробуем построить конфиг для proxy
                    sub_config.update(value._ImportProxy__make_config(headers.get(key)))
                except AttributeError:
                    # заменяем подопции на {} если они к данному
                    # моменту выродились в булев флаг
                    sub_options = (isinstance(sub_options, bool) and {}) or sub_options

                    # строим конфиг для поддерева
                    sub_config.update(
                        dict(
                            map(
                                make_subconfig(
                                    prepare_headers(headers.get(key, {})),
                                    sub_options,
                                ),
                                value,
                            )
                        )
                    )

                return (key, sub_config)

            return inner

        # начальный вызов
        result = cls.xlsreader_extra.copy()
        result.update(
            dict(
                map(
                    make_subconfig(
                        prepare_headers(cls.headers),
                        cls.optionals,
                    ),
                    cls.proxies,
                )
            )
        )
        return result

    def __init__(self, context=None):
        """Загрузка строки данных."""
        self._context = {
            'error_format': self.error_format,
        }
        self._context.update(self.initial_context.copy() or {})
        self._context.update((context or {}).copy())
        self._context = SafeDict(self._context)
        self._set_validators()

    def _set_validators(self):
        """Устанавливает валидаторы, которые будут применяться при загрузке."""
        self._validators = []

    def _validate(self, data):
        """Применяет валидаторы ко входным данным.

        :param data: словарь входных данных
        :return: два списка, список ошибок и список предупреждений.
        """
        errors, warnings = [], []
        for validator in self._validators:
            validator(data, errors, warnings)

        return errors, warnings

    def load(self, data):
        errors, warnings = self._validate(data)

        def load_to_proxy(context, options, data, key, proxy):
            # проверка на принадлежность proxy к потомкам ImportProxy
            try:
                is_single_proxy = issubclass(proxy, _ImportProxy)
            except TypeError:
                is_single_proxy = False

            # проверка на принадлежность proxy к прокси для области ячеек
            try:
                is_layout_proxy = issubclass(proxy, LayoutModelProxy)
            except TypeError:
                is_layout_proxy = False

            # получение подопций
            sub_options = options.get(key, False)
            if is_single_proxy:
                # признак обязательности выполнения
                anyway = proxy._must_be_executed_anyway(sub_options is True)
                # извлечение порции данных, если proxy они требуются
                if not bool(proxy.cells_config):
                    # конфига нет (напр. proxy это adapter)
                    if anyway:
                        sub_data = SafeDict()
                    else:
                        # прокси опционален и конфига нет - пропускаем
                        return True
                else:
                    if key not in data:
                        if not anyway:
                            # данных нет и proxy опционален - пропускаем
                            return True
                    # получаем поддерево данных
                    sub_data = SafeDict(data.get(key, {}))

                # загрузка через proxy
                try:
                    context[key] = proxy(key, context)._load(sub_data)
                except ProxyWarning as err:
                    # Записать в лог и продолжить загрузку строки
                    warnings.append((context.error_format or '{}').format(str(err)))
                    raise
                except (ProxySaveError, ValidationError) as err:
                    # такая ошибка складывается в лог
                    errors.append((context.error_format or '{}').format(str(err)))
                    if not is_layout_proxy:
                        # если обычный прокси, вся строка пропускается
                        return False
                except (ProxyCriticalError, AssertionError):
                    # AssertionError - откатит всю загрузку
                    # ProxyCriticalError - откатит с выводом сообщения
                    raise
            else:
                # --- загрузка через подцепочку proxy ---
                # получаем подконтекст и поддерево данных
                sub_context = context.copy()
                sub_data = data.get(key, {})
                # если подцепочка опциональна - пропускаем её всю
                if sub_options is True:
                    if not sub_data:
                        return True
                sub_data = SafeDict(sub_data)
                # получаем подопции
                if isinstance(sub_options, bool):
                    sub_options = collections.defaultdict(lambda: sub_options)
                for sub_key, sub_proxy in proxy:
                    if not load_to_proxy(sub_context, sub_options, sub_data, sub_key, sub_proxy):
                        return False
                # из подконтекста атрибут с тем же ключем помещается в контекст
                context[key] = sub_context[key]
            return True

        for key, proxy in self.proxies:
            if errors:
                break
            try:
                proxy_result = load_to_proxy(self._context, self.optionals, data, key, proxy)
            except ProxyWarning:
                continue
            else:
                if not proxy_result:
                    break

        return errors, warnings


class LayoutProxyLoader(MultiProxyLoader):
    """Загрузчик, умеющий генерировать себе прокси по размеченной области."""

    # список кортежей шаблонов для прокси, определяющих область данных листа,
    # которыми будет дополнен основной список proxies
    layout_proxies_template = []
    # лог неуспешного встраивания прокси
    add_proxy_log = {}

    @classmethod
    def add_proxy(cls, key, proxy, add_log, context):
        """Встраивание прокси для области в список задекларированных прокси."""

        # обновим копию начального контекста загрузчика контекстом из api
        loader_context = cls.initial_context.copy()
        loader_context.update(context)

        # определение объектов, соответствующих заголовкам колонок области
        try:
            header_info = proxy.create_header(proxy, loader_context)
            proxy.header_object = header_info.get(key)
            cls.proxies.append((key, proxy))
        except ProxySaveError as err:
            # логируем ошибку, чтобы вывалить ее в конце
            cls.add_proxy_log = add_log
            cls.add_proxy_log.setdefault(key, str(err))

    @classmethod
    def load_rows(cls, header_data, rows_data, parse_log, log, context, warning_log=None):
        super().load_rows(header_data, rows_data, parse_log, log, context)

        if cls.add_proxy_log:
            log.setdefault(rows_data[0][context['XLS_POS']], []).extend(list(cls.add_proxy_log.values()))


def _fabricate_proxy(AncestorCls, name, cells_config, default_headers):
    """Изготовление прокси области (для загрузчика) по шаблону-прокси и по заданным извне настройкам ячеек.

    :param AncestorCls: класс-предок, описывающий области и метод загрузки
    :param name: str - имя области
    :param cells_config: dict,
    :param default_headers: dict - описание ячеек области
    """

    cls = type(
        name.capitalize(),
        (AncestorCls,),
        {
            'was_fabricated': True,  # для фильтраци при добавлении в загрузчик
            'cells_config': cells_config,
            'default_headers': default_headers,
            # соответствие {модель: (ключ, строка)} для дальнейшего парсинга
            'layout_header': dict([(AncestorCls.layout_header_model, (k, v)) for k, v in default_headers.items()]),
        },
    )

    return name, cls


def fabricate_proxies(AncestorCls, layout_name, head_data):
    """Создает настройки ячеек для области и возвращает список кортежей сгенерированных прокси для загрузчика.

    :param AncestorCls: класс-предок, описывающий области и метод загрузки
    :param layout_name: str - имя области
    :param head_data: list - список строк, определяющий заголовки столбцов
    """
    proxies = []
    params = None
    cells_config, default_headers = {}, {}
    # TODO проверку на пересечение областей
    # конфиг области
    layout_conf = AncestorCls.layouts_config.get(layout_name)
    # использовать отдельные прокси для каждого столбца
    use_separated_proxy = layout_conf.get('use_separated_proxy', False)
    # заголовки колонок этой области
    cols = head_data[layout_conf.get('start_col') : layout_conf.get('end_col')]
    for idx, col_name in enumerate(cols):
        key = f'{layout_name}{idx}'
        if use_separated_proxy:
            cells_config = {key: layout_conf.get('cell_type')}
            default_headers = {key: col_name}
        else:
            cells_config.update({key: layout_conf.get('cell_type')})
            default_headers.update({key: col_name})
        params = (AncestorCls, key, cells_config, default_headers)
        if use_separated_proxy:
            # генерация отдельного прокси для столбца
            proxies.append(_fabricate_proxy(*params))
    if not use_separated_proxy and params:
        # либо генерация одного прокси для всех столбцов
        proxies.append(_fabricate_proxy(*params))

    return proxies
