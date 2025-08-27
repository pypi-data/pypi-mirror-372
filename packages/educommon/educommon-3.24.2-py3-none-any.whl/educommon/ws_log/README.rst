Приложение "Логирование запросов"
=================================

Предусловия
-----------

Ранее, в каждом из приложениий (ЭК, ЭШ и др.), использовался свой пак для
логирования запросов СМЭВ, но этот пак был практически один в один у всех
приложений, поэтому было принято решение разместить общий код пака в
приложении educommon.

Использование
--------------

1. Сначала нужно переопределить пак логов СМЭВ ``SmevLogPack`` из
``educommon/ws_log/actions.py``, переопределив в нем метод
``get_list_window_params`` и передав в params по ключу
``settings_report_window_url`` - url экшена окна настройки печати логов
СМЭВ(Это экшен пака, который мы будет переопределять следующим).

.. code-block:: python

  class SLPack(SmevLogPack):
      """Переопределенный пак логирования запросов СМЭВ."""

      def get_list_window_params(self, params, request, context):
          params = super(SLPack, self).get_list_window_params(
              params, request, context)
          smev_report_pack = ControllerCache.find_pack(
              'ssuz.webservice.report.SLPrintReportPack')

          params['settings_report_window_url'] = (
              smev_report_pack.report_window_action.get_absolute_url())

          return params

2. А затем нужно переопределить пак печати логов СМЭВ. Переопределяем метод
``set_report_window_params`` пака ``SmevLogPrintReportPack`` , передав в
params по ключу ``institute_pack`` - пак выбора учреждения (Это нужно потому,
что во всех продуктах разные модели и потому получить эти данные из
educommon пока нельзя). Если нужно чтобы в поле выбора учреждения по-умолчанию
отображалось некое учреждение(например из виджета), нужно определить
``institute`` в params, передав по этому ключу значение - объект модели
Учрежедение.

.. code-block:: python

  from educommon.ws_log.report import SmevLogPrintReportPack


  class SLPrintReportPack(SmevLogPrintReportPack):
      """Пак печати логов СМЭВ."""

      def set_report_window_params(self, params, request, context):
          params = super(SmevLogPrintReportPack, self)
         .set_report_window_params(
              params, request, context)

          # Пак выбора учреждений
          params['institute_pack'] = 'ssuz.unit.actions.UnitPack'
          params['institute'] = request.current_unit.obj

          return params

3. Зарегистрировать переопределенные паки в app_meta.

.. code-block:: python

  def register_actions():
      """Регистрация экшенов."""

      ssuz.urls.action_controller.packs.extend([
          actions.SLPack(),
          actions.SLProviderPack(),
          report.SLPrintReportPack()
      ])

Логирование
-----------

Для логирования запросов был определен менеджер логгеров для приложений
веб-сервисов ``educommon.ws_log.utils.LoggerManager``.
Список путей до логгеров принимается из ``educommon.ws_log.config.loggers``

Для существующих веб-сервисов был определен логгер по умолчанию:
``educommon.ws_log.base.DefaultWsApplicationLogger``.

Если необходимо логировать запросы в другую БД, или необходимо реализовать
сохранение отличное от стандартного, то возможно определить свой класс
логгера. В качестве родительского класса нужно указать:
``educommon.ws_log.base.BaseWsApplicationLogger``. В качестве имени класса
необходимо использовать ``WsApplicationLogger``. Так же, для инстанса
класса ``spyne.Application`` в атрибуте ``name`` необходимо указать путь до
модуля ``logger.py``.

.. code-block:: python

  class WsApplicationLogger(BaseWsApplicationLogger):

      """Класс для логирования запросов к сервисам Example."""

      log_model = ('some_app', 'ServiceLogModelName')

      @staticmethod
      def collect_log_data(ctx):
          log_record = ctx.transport.req['log_record']
          if ctx.descriptor and ctx.descriptor.service_class:
              method_info = ctx.descriptor.service_class.METHOD_VERBOSE_NAMES[
                  ctx.method_name
              ]
              log_record.method_code = ctx.method_name
              log_record.method_name = method_info['method_verbose_name']
          else:
              log_record.method_code = ctx.method_request_string
