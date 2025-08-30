var description_fld = Ext.getCmp('{{ component.description_fld.client_id }}');

if (description_fld) {
    new Ext.ToolTip({
        target: description_fld.getEl().getAttribute('id'),
        dismissDelay: 0,
        html: description_fld.getValue()
    });
}