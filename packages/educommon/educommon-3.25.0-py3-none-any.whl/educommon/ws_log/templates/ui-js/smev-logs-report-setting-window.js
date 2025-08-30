//{# Обработчик события отправки формы, по нажатию кнопки "Сформировать" #}
function submitForm(button, event, baseParams) {
    var instituteField = Ext.getCmp('{{ component.field_institute.client_id }}'),
        dateBeginField = Ext.getCmp('{{ component.field_date_begin.client_id }}'),
        dateEndField = Ext.getCmp('{{ component.field_date_end.client_id }}');

    baseParams = win.actionContextJson || {};

    //{# Добавляем параметры, для отправки формы настройки печати логов СМЭВ #}
    baseParams['institute_name'] = instituteField.lastSelectionText;

    if (dateBeginField.getValue() > dateEndField.getValue()) {
        Ext.Msg.alert(
                'Внимание!',
                'Дата по не может быть меньше чем Дата с'
            );
            return false;
    }
    baseParams['date_begin'] = dateBeginField.getValue();
    baseParams['date_end'] = dateEndField.getValue();

    win.submitForm(button, event, baseParams);
}
