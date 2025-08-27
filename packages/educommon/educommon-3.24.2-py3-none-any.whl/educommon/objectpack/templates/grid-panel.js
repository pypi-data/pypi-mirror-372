(function() {
    var panel = {{ self.cmp_code|safe }};
    // {# Запрашивает грид и размещает на панели #}
    // {# Есть возможность подписаться на beforereload (должен возвращать true / false) #}
    // {# По окончанию размещения грида файрится afterreload #}
    function reloadGridHandler(params) {
        var mask = new Ext.LoadMask(Ext.getBody());
        if (panel.fireEvent('beforereload', params)) {
            Ext.Ajax.request({
                url: panel.grid_url,
                method: 'POST',
                params: Ext.applyIf(params),
                success: function(res, opt) {
                    mask.hide();
                    var grid = smart_eval(res.responseText);
                    panel.removeAll();
                    if (grid) {
                        var store = grid.getStore();
                        store.on('beforeload', function(){mask.show()});
                        store.on('load', function(){mask.hide()});
                        store.baseParams = opt.params;
                        panel.add(grid);
                        panel.doLayout();
                    }
                    panel.fireEvent('afterreload', grid);
                },
                failure: function(){
                    mask.hide();
                }
            });
        }
    }
    panel.on('reloadgrid', reloadGridHandler);
    {% block content %}{% endblock content %}
    return panel
})()

