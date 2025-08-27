// fix для грида
{% include component.multiselect_page_fix %}
// функции окна из objectpack
{% include "multi-select-window.js" %}


var grid = Ext.getCmp('{{ component.grid.client_id }}');


applyMultiSelectFix(grid);
/*
 * {# Вместо выбранных записей из SelectionModel текущей страницы #}
 * {# отправляются записи из массива для всех страниц. #}
 */

function selectValue() {

    function showSelectRecordMessage() {
        Ext.Msg.show({
           title: 'Выбор элемента',
           msg: 'Выберите элемент из списка',
           buttons: Ext.Msg.OK,
           icon: Ext.MessageBox.INFO
        });
    }

    var records = grid.getCheckedArray();

    if (records.length === 0) {
        showSelectRecordMessage();
        return;
    }

    var win = Ext.getCmp('{{ component.client_id }}');

    {% if component.callback_url %}
        Ext.Ajax.request({
            url: "{{ component.callback_url }}",
            success: function(res,opt) {
                result = Ext.util.JSON.decode(res.responseText)
                if (!result.success){
                    Ext.Msg.alert('Ошибка', result.message)
                }
                else {
                    win.fireEvent('closed_ok', ids);
                    win.close();
                }
            }
            ,params: Ext.applyIf(
                {id: ids},
                {% if component.action_context %}
                    {{component.action_context.json|safe}}
                {% endif %}
            )
            ,failure: function(response, opts){
                uiAjaxFailMessage();
            }
        });
    {% else %}
        win.fireEvent('closed_ok', records);
        win.close();
    {% endif %}
}
