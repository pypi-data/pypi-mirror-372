var grid = Ext.getCmp('{{ component.grid.client_id }}');

grid.on('rowdblclick', viewTask);

function viewTask(e){
    var mask = new Ext.LoadMask(win.getEl());
    if (grid.selModel.hasSelection()){
        Ext.Ajax.request({
            url: '{{ component.view_url }}',
            params: {
                '{{ component.grid.row_id_name }}': grid.selModel.getSelected().id
            },
            success: function(response){
                mask.show();
                var viewWin = smart_eval(response.responseText);
                viewWin.on('close', function(){ mask.hide() });
            },
            failure: function(response, request) {
                uiAjaxFailMessage.apply(this, arguments);
            }
        });
    }
}
