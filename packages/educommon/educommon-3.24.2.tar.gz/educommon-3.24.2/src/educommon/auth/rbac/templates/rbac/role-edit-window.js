{% load educommon %}
{% include 'rbac/role-add-window.js' %}

var roleId = {% if component.role %}{{ component.role.id }}{% else %}null{% endif %};

var canBeAssignedField = Ext.getCmp('{{ component.field__can_be_assigned.client_id }}');

var partitionsGrid = Ext.getCmp('{{ component.grid__partitions.client_id }}');
var partitionsStore = partitionsGrid.getStore();
var partitionsSM = partitionsGrid.getSelectionModel();

var permissionsGrid = Ext.getCmp('{{ component.grid__permissions.client_id }}');
var permissionsStore = permissionsGrid.getStore();
var permissionsSM = permissionsGrid.getSelectionModel();

var resultPermissionsTab = Ext.getCmp('{{ component.tab__result_permissions.client_id }}');
var resultPermissionsTree = Ext.getCmp('{{ component.tab__result_permissions.tree__result_permissions.client_id }}');
var resultPermissionsSM = resultPermissionsTree.getSelectionModel();

var rolePermissions = {{ component.permission_ids }};

var canEdit = {{ component.can_edit }};

if (canBeAssignedField.label) {
    canBeAssignedField.label.setWidth(225);
}

function columnRenderer(value, metaData, record, rowIndex, colIndex, store) {
    if (rolePermissions.indexOf(record.id) == -1) {
        metaData.attr = 'style="color: #777;"';
    }
    return value;
}

function permissionsGridUpdate() {
    if (partitionsSM.hasSelection()) {
        var partitionId = partitionsSM.getSelected().json.id;
        permissionsStore.setBaseParam('partition_id', partitionId);
        permissionsStore.lastOptions = null;
        permissionsStore.reload();
    } else {
        permissionsStore.setBaseParam('partition_id', null);
        permissionsStore.removeAll();
        permissionsGrid.getSelectionModel().unlock();
    }
}

partitionsSM.on('selectionchange', permissionsGridUpdate);
partitionsStore.on('load', permissionsGridUpdate);

permissionsSM.on('rowselect', function (sm, rowIndex, record) {
    if (rolePermissions.indexOf(record.id) == -1) {
        rolePermissions.push(record.id);
    }
});

permissionsSM.on('rowdeselect', function (sm, rowIndex, record) {
    if (rolePermissions.indexOf(record.id) != -1) {
        rolePermissions.splice(rolePermissions.indexOf(record.id), 1);
    }
});

permissionsStore.on('load', function (store, records, options) {
    var selectedRecords = [];

    for (var i = 0; i < records.length; i++) {
        var record = records[i];

        record.set('dependencies', Ext.util.JSON.decode(
            record.get('dependencies')
        ).join('<br/>'));
        record.commit();

        if (rolePermissions.indexOf(record.id) != -1) {
            selectedRecords.push(record);
        }
    }

    permissionsSM.suspendEvents();
    permissionsSM.selectRecords(selectedRecords);

   if (!canEdit) {
        permissionsGrid.getSelectionModel().lock();
    }
    permissionsSM.resumeEvents();
});

win.on('beforesubmit', function(action) {
    action.params['permissions'] = rolePermissions.join(',');
});
/* ------------------------------------------------------------------------- */
// Отображение текстового описания разрешения при наведении курсора мыши.


function showPermissionDescription() {
    var description = this.get('description');
    var panel = Ext.getCmp('{{ component.panel__description.client_id }}');
    panel.update(description ? description.replace(/\n/g, '<br/>') : '');
}


function hidePermissionDescription() {
    var panel = Ext.getCmp('{{ component.panel__description.client_id }}');
    panel.update('');
}


permissionsStore.on('load', function(store, records) {
    for (var i = 0; i < records.length; i++) {
        var record = records[i];
        var rowElement = Ext.get(permissionsGrid.view.getRow(i));

        rowElement.on('mouseenter', showPermissionDescription, record);
        rowElement.on('mouseleave', hidePermissionDescription, record);
    }
});
/* ------------------------------------------------------------------------- */
// Работа с зависимостями между разрешениями.


// Загрузка разрешений при активации вкладки.
resultPermissionsTab.on('activate', function() {
    var baseParams = resultPermissionsTree.loader.baseParams;
    var role_permissions = baseParams['role_permissions'] || [];

    var lastOptions = resultPermissionsTree.loader.lastOptions;
    if (
        lastOptions === undefined ||
        lastOptions.length != rolePermissions.length ||
        !rolePermissions.some(function(value) {
            return lastOptions.indexOf(value) != -1;
        })
    ) {
        if (roleId) {
            baseParams['{{ component.roles_pack.id_param_name }}'] = roleId;
        }
        resultPermissionsTree.loader.lastOptions = rolePermissions.slice();

        baseParams['role_permissions'] = rolePermissions.join(',');

        resultPermissionsTab.el.mask('Загрузка данных...');

        Ext.Ajax.request({
            url: '{{ component.result_action_url }}',
            method: 'POST',
            params: baseParams,
            success: function (response, options) {
                try {
                    resultPermissionsTree.root.removeAll();

                    var data = Ext.util.JSON.decode(response.responseText);
                    var permSources = {{ component.perm_sources|jsonify }};

                    for (var partitionTitle in data) {
                        var partitionNode = new Ext.tree.TreeNode({
                            title: partitionTitle
                        });
                        resultPermissionsTree.root.appendChild(partitionNode);

                        for (var groupTitle in data[partitionTitle]) {
                            var groupNode = new Ext.tree.TreeNode({
                                title: groupTitle
                            });
                            partitionNode.appendChild(groupNode);

                            var permsData = data[partitionTitle][groupTitle];
                            for (var i = 0; i < permsData.length; i++) {
                                permNode = new Ext.tree.TreeNode({
                                    title: permsData[i].title,
                                    description: permsData[i].description,
                                    source: permSources[permsData[i].source],
                                });
                                groupNode.appendChild(permNode);
                            }
                        }
                    }

                    resultPermissionsTree.root.cascade(function(node) {
                        node.expand()
                    });
                }
                finally {
                    resultPermissionsTab.el.unmask();
                }
            },
            failure: function (response, options) {
                resultPermissionsTab.el.unmask();

                uiAjaxFailMessage(response, options);
            }
        });
    }
});


// Отображение текстового описания разрешения при наведении курсора мыши.
function showResultPermissionDescription(sm, node) {
    var panel = Ext.getCmp('{{ component.tab__result_permissions.panel__description.client_id }}');

    if (node) {
        panel.update(
            node.attributes.description ?
            node.attributes.description.replace(/\n/g, '<br/>') : ''
        );
    } else {
        panel.update(
            'Для отображения описания разрешения выделите соответствующее ' +
            'разрешение...'
        );
    }
}
resultPermissionsSM.on('selectionchange', showResultPermissionDescription);
showResultPermissionDescription(resultPermissionsSM);
/* ------------------------------------------------------------------------- */
