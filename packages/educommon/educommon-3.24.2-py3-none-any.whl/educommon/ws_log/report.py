from m3 import (
    ApplicationLogicException,
)

from educommon.report import (
    AbstractReportBuilder,
)
from educommon.report.actions import (
    CommonReportPack,
)
from educommon.report.reporter import (
    SimpleReporter,
)
from educommon.ws_log.models import (
    SmevLog,
)
from educommon.ws_log.provider import (
    SmevLogDataProvider,
)
from educommon.ws_log.ui import (
    SmevLogReportWindow,
)


class SmevLogReportBuilder(AbstractReportBuilder):
    """Билдер отчёта "Логи СМЭВ"."""

    def __init__(self, provider, adapter, report, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.provider = provider
        self.adapter = adapter
        self.report = report
        self.params = kwargs.get('params', {})

    def build(self):
        """Строит отчет, заполняя секции шаблона из данных провайдера."""
        self.header_section = self.report.get_section('header')
        self.row_section = self.report.get_section('row')

        self.header_section.flush({'institute_name': self.params['institute_name']})

        smev_logs = self.provider.smev_logs_data.extra(select={'date': 'DATE(time)'}).values(
            'date', 'consumer_type', 'consumer_name', 'source', 'result'
        )

        sources = dict(SmevLog.SOURCE_TYPES)
        consumers = dict(SmevLog.CONSUMER_TYPES)

        for index, smev_log in enumerate(smev_logs, 1):
            smev_log['index'] = index
            smev_log['source'] = sources.get(smev_log['source'], '')
            smev_log['consumer_type'] = consumers.get(smev_log['consumer_type'], '')

            if not smev_log['result']:
                smev_log['result'] = 'Успешно'

            self.row_section.flush(smev_log)


class SmevLogReporter(SimpleReporter):
    """Строитель отчёта "Логи СМЭВ"."""

    extension = '.xlsx'
    template_file_path = './templates/report/smev_logs.xlsx'
    data_provider_class = SmevLogDataProvider
    builder_class = SmevLogReportBuilder


class SmevLogPrintReportPack(CommonReportPack):
    """Пак печати отчета "Логи СМЭВ"."""

    title = 'Логи СМЭВ'
    report_window = SmevLogReportWindow
    reporter_class = SmevLogReporter

    is_async = True

    extend_menu = extend_desktop = None

    def declare_context(self, action):
        context = super().declare_context(action)

        if action is self.report_action:
            context.update(
                institute_name={'type': 'str'},
                date_begin={'type': 'date'},
                date_end={'type': 'date'},
            )

        return context

    def get_provider_params(self, request, context):
        return self.context2dict(context)

    def get_builder_params(self, request, context):
        result = self.context2dict(context)
        result['title'] = self.title
        return result

    def check_report_params(self, request, context):
        """
        Проверка передаваемых параметров для формирования отчёта.

        :raise: ApplicationLogicException
        """
        if context.date_begin > context.date_end:
            raise ApplicationLogicException('Дата по не может быть меньше чем Дата с!')
