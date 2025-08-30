{% include 'rbac/roles-view-list-window.js' %}

var topBar = Ext.getCmp('{{ component.grid.top_bar.client_id }}'),
    addMenu = topBar.items.items[{{ component.grid.add_menu_index }}],
    addNewChildButton = addMenu.menu.items.items[{{ component.grid.new_child_index }}],
    addToRoleButton = addMenu.menu.items.items[{{ component.grid.add_to_role_index }}],
    editRoleButton = Ext.getCmp('{{ component.grid.top_bar.button_edit.client_id }}'),
    deleteMenu = topBar.items.items[{{ component.grid.delete_menu_index }}],
    deleteFromRoleButton = deleteMenu.menu.items.items[{{ component.grid.delete_from_role_index }}];

function setDisabledControls(isDisabled) {
    addNewChildButton.setDisabled(isDisabled);
    addToRoleButton.setDisabled(isDisabled);
    editRoleButton.setDisabled(isDisabled);
    deleteMenu.setDisabled(isDisabled);
}

// Т.к. при открытии окна у нас нет ни одного выбранного элемента
win.on('show', function () {
    setDisabledControls(true);
});

// Если была выбрана дочерняя роль, то после нажатия "Обновить"
// выбранный элемент остается в SelectionModel.
// Аналогичное поведение при редактировании и добавлении дочерней роли.
gridLoader.on('load', function () {
    rolesSM.clearSelections();
});

rolesSM.on('selectionchange', function (sm, node) {
    setDisabledControls(!node);
    deleteFromRoleButton.setDisabled(!node || node.parentNode === rolesGrid.root);
});

function addRoleToRole(roleId, parentId) {
    Ext.Ajax.request({
        url: '{{ component.pack.add_role_to_role_action.absolute_url }}',
        params: {
            '{{ component.pack.id_param_name }}': roleId,
            'parent_id': parentId,
        },
        success: function (response, options) {
            smart_eval(response.responseText);
            rolesGrid.refreshStore();
        },
        failure: function (response, options) {
            uiAjaxFailMessage();
        }
    });
}

function topBarAddToRole() {
    var selectedNode = rolesSM.getSelectedNode();

    if (selectedNode) {
        var roleId = selectedNode.id;

        Ext.Ajax.request({
            url: '{{ component.pack.add_role_to_role_window_action.absolute_url }}',
            params: {
                '{{ component.pack.id_param_name }}': roleId,
                'select_mode': true,
            },
            success: function (response, options) {
                var selectWindow = smart_eval(response.responseText);
                selectWindow.on('closed_ok', function (parentId, displayText) {
                    addRoleToRole(roleId, parentId);
                });
            },
        });
    } else {
        Ext.Msg.alert('Добавить в роль', 'Элемент не выбран');
    }
}

function topBarDeleteFromRole() {
    var selectedNode = rolesSM.getSelectedNode();

    if (selectedNode && selectedNode.parentNode) {
        var roleId = selectedNode.id;
        var parentId = selectedNode.parentNode.id;

        Ext.Ajax.request({
            url: '{{ component.pack.delete_role_from_role_action.absolute_url }}',
            params: {
                '{{ component.pack.id_param_name }}': roleId,
                'parent_id': parentId,
            },
            success: function (response, options) {
                smart_eval(response.responseText);
                rolesGrid.refreshStore();
            },
            failure: function (response, options) {
                uiAjaxFailMessage();
            }
        });
    } else {
        Ext.Msg.alert('Удалить из роли', 'Элемент не выбран');
    }
}
