(function() {
    var panel = {{ self.cmp_code|safe }};
    panel.filters = {
        {% for ctl in self.filters %}
        '{{ ctl.name }}': Ext.getCmp('{{ ctl.client_id }}'),
        {% endfor %}
    };
    // {# начальные значения фильтрующих полей #}
    panel.params = {
        {% for ctl in self.filters %}
        '{{ ctl.name }}': panel.filters['{{ ctl.name }}'].getValue(),
        {% endfor %}
    };
    panel.updateParams = function(){
        // {# принудительный сбор данных с фильтрующих полей панели #}
        for (fieldName in this.filters){
            this.params[fieldName] = this.filters[fieldName].getValue();
        }
    }

    // {# фабрика стандартных подписчиков #}
    function makeSimpleHandler(ctl, name) {
        return function() {
            panel.params[name] = ctl.getValue();
            panel.fireEvent("changed", panel.params);
        };
    };

    // {# установка подписчиков, определяемых на сервере #}
    {% for ctl in self.filters %}
    {% for evt in ctl.events %}
    panel.filters['{{ ctl.name }}'].on(
        '{{ evt.0 }}',
        {{ evt.1 }}(panel.filters['{{ ctl.name }}'], '{{ ctl.name }}')
    );
    {% endfor %}
    {% endfor %}

    {% block content %}
    {% endblock %}

    return panel
})()
