//{# Отправляет запрос для получения окна настройки печати логов СМЭВ. #}
function printSmevLogsReport() {

    Ext.Ajax.request({
        url: '{{ component.settings_report_window_url }}',
        method: 'POST',
        params: {},
        success: function (response, options) {
            smart_eval(response.responseText);
        },
        failure: function (response, options) {
            uiAjaxFailMessage(response, options);
        }
    })
}
