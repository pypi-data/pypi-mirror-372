/*
 * {# Подтверждение для окна связанных объектов. #}
 */
function confirmDelete(){
    var params = win.actionContextJson;
    params['delete_check_confirmed'] = true;
    Ext.Ajax.request({
        url: '{{ component.pack_action_url }}',
        method: 'POST',
        params: params,
        success: function(res, opt) {
            win.close(true);
            var viewWin = smart_eval(res.responseText);
        },
        failure: function(){
            uiAjaxFailMessage();
        },
        callback: function() {
            Ext.getBody().unmask();
            {% if component.grid_id %}
            // Если указан id грида - перезагружаем его стор
            var grid = Ext.getCmp('{{ component.grid_id }}');
            if (grid) {
                grid.store.reload();
            }
            {% endif %}
        }
    });
}
