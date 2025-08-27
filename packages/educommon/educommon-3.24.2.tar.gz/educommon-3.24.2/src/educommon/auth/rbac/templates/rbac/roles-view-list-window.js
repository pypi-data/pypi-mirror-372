var rolesGrid = Ext.getCmp('{{ component.grid.client_id }}');
var gridLoader = rolesGrid.getLoader();
var rolesSM = rolesGrid.getSelectionModel();
// Если была выбрана дочерняя роль, то после нажатия "Обновить"
// выбранный элемент остается в SelectionModel.
// Аналогичное поведение при редактировании и добавлении дочерней роли.
gridLoader.on('load', function () {
    rolesSM.clearSelections();
});
