var mask = new Ext.LoadMask(win.getEl());
var grid_panel = Ext.getCmp('{{ component.grid_panel.client_id }}');
var filter_panel = Ext.getCmp('{{ component.filter_cnt.client_id }}');

grid_panel.on('reloadgrid', function(params) {
    win.actionContextJson = Ext.applyIf(win.actionContextJson, params);
});

var reloadGrid = function(){
    grid_panel.fireEvent('reloadgrid', win.actionContextJson);
};

{% block content %}
{% endblock %}