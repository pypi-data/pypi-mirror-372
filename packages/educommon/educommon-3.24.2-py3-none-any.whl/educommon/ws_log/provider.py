import datetime

from educommon.report import (
    AbstractDataProvider,
)
from educommon.ws_log.models import (
    SmevLog,
)


class SmevLogDataProvider(AbstractDataProvider):
    """Провайдер данных отчета "Логи СМЭВ"."""

    def init(self, **params):
        super().init(**params)

        self.date_begin = params['date_begin']
        self.date_end = params['date_end']

    def get_smev_logs_data(self):
        """Возвращает логи СМЭВ на отрезок времени."""
        return SmevLog.objects.filter(
            time__range=(
                datetime.datetime.combine(self.date_begin, datetime.time.min),
                datetime.datetime.combine(self.date_end, datetime.time.max),
            ),
        )

    def load_data(self):
        self.smev_logs_data = self.get_smev_logs_data()
