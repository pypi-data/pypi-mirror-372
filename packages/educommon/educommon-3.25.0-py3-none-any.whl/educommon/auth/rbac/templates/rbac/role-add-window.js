var canBeAssignedField = Ext.getCmp('{{ component.field__can_be_assigned.client_id }}');
var userTypesField = Ext.getCmp('{{ component.field__user_types.client_id }}');

canBeAssignedField.on('check', function (cmp, checked) {
    if (!checked) {
        userTypesField.clearValue();
    }
    userTypesField.setDisabled(!checked)
});
