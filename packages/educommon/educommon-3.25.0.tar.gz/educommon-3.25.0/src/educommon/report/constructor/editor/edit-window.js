{% load educommon %}
// {# ---------------------------------------------------------------------- #}
// Добавление CSS-классов для окон приложения.


win.on('beforeshow', function () {
    var cssStyleSheet = document.styleSheets[0];
    var cssRules = cssStyleSheet.cssRules;

    function insertRule(selector, rule) {
        for (var i = 0; i < cssRules.length; i++) {
            if (cssRules[i].selectorText == selector) {
                return;
            }
        }

        cssStyleSheet.insertRule(selector + ' ' + rule, cssRules.length);
    }

    insertRule(
        '.report-constructor-switch-visible',
        '{background-image: url(/static/m3/icons/eye.png) !important}'
    );
    insertRule(
        '.report-constructor-arrow-up',
        '{background-image: url(/static/m3/icons/arrow_up.png) !important}'
    );
    insertRule(
        '.report-constructor-arrow-down',
        '{background-image: url(/static/m3/icons/arrow_down.png) !important}'
    );
    insertRule(
        '.report-constructor-gray *',
        '{color: gray !important}'
    );
    insertRule(
        '.report-constructor-red *',
        '{color: red !important}'
    );
});


win.on('close', function () {
    var cssStyleSheet = document.styleSheets[0];
    var cssRules = cssStyleSheet.cssRules;

    for (var i = cssRules.length - 1; i >= 0; i--) {
        if (cssRules[i].selectorText.startsWith('.report-constructor-')) {
            cssStyleSheet.deleteRule(i);
        }
    }
});
// {# ---------------------------------------------------------------------- #}

var availableColumnsUrl = '{{ component.tab__columns.grid__available_columns.available_columns_url }}';
var dataSourceField = Ext.getCmp('{{ component.field__data_source_name.client_id }}');

var tabPanel = Ext.getCmp('{{ component.tab_panel.client_id }}');

var availableColumnsTree = Ext.getCmp('{{ component.tab__columns.grid__available_columns.client_id }}');
var availableColumnsSM = availableColumnsTree.getSelectionModel();
var addColumnButton = Ext.getCmp('{{ component.tab__columns.grid__available_columns.top_bar.button__add.client_id }}');

var reportColumnsTree = Ext.getCmp('{{ component.tab__columns.grid__report_columns.client_id }}');
var reportColumnsSM = reportColumnsTree.getSelectionModel();
var removeColumnButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__remove.client_id }}');
var switchColumnVisibilityButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__switch_visibility.client_id }}');
// Агрегаторы
// Промежуточный итог
var byValueCountButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__by_value_count.client_id }}');
var byValueSumButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__by_value_sum.client_id }}');
// Итог
var totalCountButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__total_count.client_id }}');
var totalUniqueCountButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__total_uniq_count.client_id }}');
var totalSumButton = Ext.getCmp('{{ component.tab__columns.grid__report_columns.top_bar.button__total_sum.client_id }}');

var filterGroupOperatorField = Ext.getCmp('{{ component.tab__filters.panel__operator.field__operator.client_id }}');
var filtersGrid = Ext.getCmp('{{ component.tab__filters.grid__filters.client_id }}');
var filtersGridStore = filtersGrid.getStore();
var filtersGridSM = filtersGrid.getSelectionModel();
var filtersGridCM = filtersGrid.getColumnModel();
var filtersGridExcludeColumn = filtersGridCM.columns.filter(
    function(column) {return column.dataIndex == 'exclude'}
).pop();
var filtersGridCaseSensitiveColumn = filtersGridCM.columns.filter(
    function(column) {return column.dataIndex == 'case_sensitive'}
).pop();
var deleteFilterButton = Ext.getCmp('{{ component.tab__filters.grid__filters.top_bar.button__delete.client_id }}');
var filterColumnField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__column.client_id }}');
var filterOperatorField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__operator.client_id }}');
var filterExcludeField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__exclude.client_id }}');
var caseSensitiveField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__case_sensitive.client_id }}');
var filterValueField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__value.client_id }}');
var filterCommentField = Ext.getCmp('{{ component.tab__filters.panel__filter_params.field__comment.client_id }}');
var filterParamsFields = [filterColumnField,
                          filterOperatorField,
                          filterExcludeField,
                          caseSensitiveField,
                          filterValueField,
                          filterCommentField];

var sortingGrid = Ext.getCmp('{{ component.tab__sorting.grid__sorting.client_id }}');
var sortingGridStore = sortingGrid.getStore();
var sortingGridSM = sortingGrid.getSelectionModel();
var deleteSortButton = Ext.getCmp('{{ component.tab__sorting.grid__sorting.top_bar.button__delete.client_id }}');
var moveSortUpButton = Ext.getCmp('{{ component.tab__sorting.grid__sorting.top_bar.button__move_up.client_id }}');
var moveSortDownButton = Ext.getCmp('{{ component.tab__sorting.grid__sorting.top_bar.button__move_down.client_id }}');
var sortingColumnField = Ext.getCmp('{{ component.tab__sorting.panel__sorting_params.field__column.client_id }}');
var sortingDirectionField = Ext.getCmp('{{ component.tab__sorting.panel__sorting_params.field__direction.client_id }}');
var sortingParamsFields = [sortingColumnField,
                           sortingDirectionField];

var OPERATOR_IS_NULL = {{ component.constants.IS_NULL }};
var OPERATOR_IN = {{ component.constants.IN }};
var OPERATOR_BETWEEN = {{ component.constants.BETWEEN }};
var VALID_OPERATORS = {{ component.constants.VALID_OPERATORS|jsonify }};
var OPERATOR_CHOICES = {{ component.constants.OPERATOR_CHOICES|jsonify }};
var DIRECTION_CHOICES = {{ component.constants.DIRECTION_CHOICES|jsonify }};
var tplEditWindowReadOnly = {{ component.read_only|jsonify }};

// {# ---------------------------------------------------------------------- #}

// {# Автоматическое изменение размеров панели с вкладками при изменении #}
// {# размеров окна работает только если параметр autoWidth отключен. #}
// {# I ♥ ExtJS!!! #}
tabPanel.autoWidth = false;  // {# не устанавливается из Python. I ♥ M3!!! #}


// {# Запрет изменения чек-бокса в колонке "Учет регистра". #}
function processEvent(name, e, grid, rowIndex, colIndex) {
    if (name != 'mousedown') {
        return Ext.grid.ActionColumn.superclass.processEvent.apply(
            this, arguments
        );
    }
}
filtersGridCaseSensitiveColumn.processEvent = processEvent;
filtersGridExcludeColumn.processEvent = processEvent;
// {# ---------------------------------------------------------------------- #}


function dataSourceChangeHandler() {
    var dataSourceName = dataSourceField.getValue();
    var loaderParams = availableColumnsTree.loader.baseParams;

    if (dataSourceName) {
        loaderParams.data_source_name = dataSourceName;

        availableColumnsTree.loader.dataUrl = availableColumnsUrl;
        availableColumnsTree.loader.load(
            availableColumnsTree.root,
            function (node) {
                node.loadComplete();
                node.expand();
            }
        );
    } else {
        availableColumnsTree.loader.dataUrl = undefined;
        availableColumnsTree.root.removeAll();
    }

    reportColumnsTree.root.removeAll();
    filtersGridStore.removeAll();
    filterColumnField.store.removeAll();
    sortingGridStore.removeAll();
    sortingColumnField.store.removeAll();
}

dataSourceChangeHandler();
dataSourceField.on('change', dataSourceChangeHandler);


availableColumnsTree.loader.on('beforeload', function(loader, node) {
    loader.baseParams.parent_column_name = node.attributes.full_name;
});


// {# Деактивирует кнопку добавления колонки в отчет, если не выбрана или режим read_only #}
availableColumnsSM.on('selectionchange', function(sm, node) {
    addColumnButton.setDisabled(!node || node.hasChildNodes() || tplEditWindowReadOnly);
});


//{# Деактивирует кнопку удаления колонки из отчета, если не выбрана или режим read_only #}
reportColumnsSM.on('selectionchange', function(sm, node) {
    removeColumnButton.setDisabled(!node || tplEditWindowReadOnly);

    if (node && !tplEditWindowReadOnly) {
        switchColumnVisibilityButton.setVisible(node.isLeaf());
        switchColumnVisibilityButton.setText(
            node.attributes.visible ? 'Не отображать в отчете' : 'Отображать'
        );
    } else {
        switchColumnVisibilityButton.setVisible(false);
    }
});


// {# Возвращает полное наименование узла с учетом иерархии. #}
function getFullTitle(node, delimiter) {
    if (delimiter === undefined) {
        delimiter = ' → ';
    }

    if (node.parentNode && node.parentNode.parentNode) {
        return (
            getFullTitle(node.parentNode) + delimiter + node.attributes.title
        );
    } else {
        return node.attributes.title;
    }
}


// {# TODO: Скорее всего функции addColumnToReport и removeColumnFromReport #}
// {# TODO: можно объединить в одну. #}

// {# Переносит колонку из грида доступных колонок в грид колонок отчета. #}
function addColumnToReport() {
    var node = availableColumnsSM.getSelectedNode();
    if (!node) {
        Ext.Msg.alert('Внимание!', 'Выберите колонку для добавления в отчет.');
        return;
    }

    if (node.hasChildNodes()) {
        Ext.Msg.alert(
            'Внимание!',
            'Добавлять в отчет можно только колонки без вложенных колонок.'
        );
        return;
    }

    var fullTitle = getFullTitle(node);
    var root = availableColumnsTree.root;
    var nodesHierarchy = [];
    for (var n = node; n !== root; n = n.parentNode) {
        nodesHierarchy.unshift(n);
    }

    var targetNode = reportColumnsTree.root;
    for (var i = 0; i < nodesHierarchy.length; i++) {
        var n = targetNode.findChild('name', nodesHierarchy[i].attributes.name);
        if (!n) {
            n = new Ext.tree.TreeNode(nodesHierarchy[i].attributes);
            n.attributes.visible = true;
            n.attributes.visible_title = 'Да';
            targetNode.appendChild(n);
            targetNode.expand();
        }
        targetNode = n;
    }

    node.remove();

    // {# Удаление пустых узлов. #}
    nodesHierarchy.reverse();
    for (var i = 1; i < nodesHierarchy.length; i++) {
        var n = nodesHierarchy[i];
        if (!n.hasChildNodes()) {
            n.remove();
        }
    }
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление колонки в комбо-бокс на панели с параметрами фильтра. #}

    filterColumnField.store.add(new filterColumnField.store.recordType({
        name: node.attributes.full_name,
        title: fullTitle
    }));
    filterColumnField.store.sort('title', 'ASC');
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление колонки в комбо-бокс на панели с параметрами сортировки. #}

    sortingColumnField.store.add(new sortingColumnField.store.recordType({
        name: node.attributes.full_name,
        title: fullTitle
    }));
    sortingColumnField.store.sort('title', 'ASC');
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
}


// {# Переносит колонку из грида колонок отчета в грид доступных колонок. #}
function removeColumnFromReport() {
    var node = reportColumnsSM.getSelectedNode();
    if (!node) {
        Ext.Msg.alert('Внимание!', 'Выберите колонку для добавления в отчет.');
        return;
    }

    // {# Восстановление всех родительских узлов в гриде доступных колонок. #}
    var nodesHierarchy = [];
    for (var n = node; n !== reportColumnsTree.root; n = n.parentNode) {
        nodesHierarchy.unshift(n);
    }

    if (node.attributes.is_fake!=true) {
        // {# Переносим если колонка доступна. #}
        var targetNode = availableColumnsTree.root;
        for (var i = 0; i < nodesHierarchy.length; i++) {
            var n = targetNode.findChild('name', nodesHierarchy[i].attributes.name);
            if (!n) {
                n = new Ext.tree.TreeNode(nodesHierarchy[i].attributes);
                targetNode.appendChild(n);
            }
            targetNode = n;
        }

        // {# Восстановление поддерева выбранного узла. #}
        function move(fromNode, toNode) {
            for (var i = 0; i < fromNode.childNodes.length; i++) {
                var fn = fromNode.childNodes[i];
                var tn = new Ext.tree.TreeNode(fn.attributes);

                toNode.appendChild(tn);

                if (fn.hasChildNodes()) {
                    move(fn, tn);
                }
            }

            if (fromNode.hasChildNodes()) {
                fromNode.removeAll();
            }
            fromNode.remove();
        }

        move(node, targetNode);
    } else {
        // {# Удаляем если колонка недоступна. #}
        if (node.hasChildNodes()) {
            node.removeAll();
        }
        node.remove();
    }
    // {# Удаление пустых узлов. #}
    nodesHierarchy.reverse();
    for (var i = 1; i < nodesHierarchy.length; i++) {
        var n = nodesHierarchy[i];
        if (!n.hasChildNodes()) {
            n.remove();
        }
    }
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Удаление колонки из комбо-бокса на панели с параметрами фильтра. #}
    var i = filterColumnField.store.find('name', node.attributes.full_name);
    if (i != -1) {
        filterColumnField.store.removeAt(i);
    }

    // {# Удаление фильтров для колонки. #}
    filtersGridStore.query('column', node.attributes.full_name).each(
        function(record) {
            if (filtersGridSM.getSelected() === record) {
                filtersGridSM.fireEvent(
                    'rowdeselect',
                    filtersGridSM,
                    filtersGridStore.indexOf(record),
                    record
                );
            }
            filtersGridStore.remove(record);
        }
    );
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Удаление колонки из комбо-бокса на панели с параметрами сортировки. #}
    var i = sortingColumnField.store.find('name', node.attributes.full_name);
    if (i != -1) {
        sortingColumnField.store.removeAt(i);
    }

    // {# Удаление параметров сортировки для удаляемой колонки. #}
    sortingGridStore.query('column', node.attributes.full_name).each(
        function(record) {
            if (sortingGridSM.getSelected() === record) {
                sortingGridSM.fireEvent(
                    'rowdeselect',
                    sortingGridSM,
                    sortingGridStore.indexOf(record),
                    record
                );
            }
            sortingGridStore.remove(record);
        }
    );
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
}


function gridDoubleClickHandler(handler, node) {
    if (node.leaf) {
        handler();
    } else if (node.isExpanded()) {
        node.collapse();
    } else {
        node.expand();
    }
}
availableColumnsTree.on(
    'dblclick', gridDoubleClickHandler.bind(this, addColumnToReport)
);
reportColumnsTree.on(
    'dblclick', gridDoubleClickHandler.bind(this, removeColumnFromReport)
);


// {# Включает/отключает отображение колонки в отчете. #}
function switchColumnVisibility() {
    var node = reportColumnsSM.getSelectedNode();
    if (!node) {
        Ext.Msg.alert('Внимание!', 'Выберите колонку для добавления в отчет.');
        return;
    }

    node.attributes.visible = !node.attributes.visible;
    if (node.attributes.visible) {
        node.attributes.visible_title = 'Да';
        node.ui.removeClass('report-constructor-gray');
    } else {
        node.attributes.visible_title = 'Нет';
        node.ui.addClass('report-constructor-gray');
    }

    // Это безобразие здесь лишь потому, что не смог найти способа нормально
    // обновить данные в гриде :(
    node.ui.getEl().children[0].children[2].children[0].textContent = (
        node.attributes.visible_title
    );

    switchColumnVisibilityButton.setText(
        node.attributes.visible ? 'Не отображать в отчете' : 'Отображать'
    );

}


// {# Подготовка параметров запроса на создание/изменение шаблона отчета. #}
win.on('beforesubmit', function(submit) {
    // {# Добавление в параметры запроса списка колонок отчета. #}
    function getColumns(node) {
        var result = [];
        for (var i = 0; i < node.childNodes.length; i++) {
            var n = node.childNodes[i];
            if (n.hasChildNodes()) {
                Array.prototype.push.apply(result, getColumns(n));
            } else {
                result.push({
                    accessor_name: n.attributes.full_name,
                    visible: n.attributes.visible,
                    by_value: n.attributes.by_value,
                    total: n.attributes.total
                });
            }
        }

        return result;
    }

    submit.params.columns = Ext.util.JSON.encode(
        getColumns(reportColumnsTree.root)
    );
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление в параметры запроса информации о фильтрах отчета. #}

    var groupOperator = filterGroupOperatorField.getValue();
    var filtersData = filtersGridStore.data.items;
    if (groupOperator || filtersData.length > 0) {
        if (!groupOperator && filtersData.length > 1) {
            Ext.Msg.alert(
                'Ошибка в параметрах шаблона',
                'Необходимо указать условие объединения фильтров.'
            );
            return false;
        }

        if (!filtersData.every(function(record) {
            return !!record.get('column') && !!record.get('operator');
        })) {
            Ext.Msg.alert(
                'Ошибка в параметрах шаблона',
                'Параметры фильтров указаны некорректно.'
            );
            return false;
        }

        var filters = {};
        filters[groupOperator] = filtersData.map(function(record) {
            var operator = record.get('operator');

            if (operator == OPERATOR_IN || operator == OPERATOR_BETWEEN) {
                var values = record.get('values').split('|');
            } else {
                var values = [record.get('values')];
            }

            return {
                column: record.get('column'),
                operator: record.get('operator'),
                exclude: record.get('exclude'),
                case_sensitive: record.get('case_sensitive'),
                values: values,
                comment: record.get('comment')
            }
        });
        submit.params.filters = Ext.util.JSON.encode(filters);
    }
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление в параметры запроса информации о фильтрах отчета. #}

    var sortingData = sortingGridStore.data.items;
    if (!sortingData.every(function(record) {
        return !!record.get('column') && !!record.get('direction');
    })) {
        Ext.Msg.alert(
            'Ошибка в параметрах шаблона',
            'Параметры сортировки указаны некорректно.'
        );
        return false;
    }

    submit.params.sorting = Ext.util.JSON.encode(
        sortingData.map(function(record) {
            return {
                column: record.get('column'),
                direction: record.get('direction'),
            }
        }
    ));
});
// {# ---------------------------------------------------------------------- #}
// {# Заполнение колонок шаблона, которые были созданы ранее. #}


function findNode(rootNode, fullName) {
    var nodeNames = fullName.split('.');

    while (rootNode && nodeNames.length > 0) {
        rootNode = rootNode.findChild('name', nodeNames.shift());
    }

    return rootNode;
}


function initColumn(columnData, parentNode) {
    var node = new Ext.tree.TreeNode({
        name: columnData.name,
        data_type: columnData.data_type,
        full_name: columnData.full_name,
        title: columnData.title,
        leaf: columnData.leaf,
        visible: columnData.visible,
        is_fake: columnData.is_fake,
        visible_title: columnData.visible_title,
        by_value: columnData.by_value,
        by_value_title: columnData.by_value_title,
        total: columnData.total,
        total_title: columnData.total_title
    });

    parentNode.appendChild(node);

    for (var i = 0; i < columnData.nested.length; i++) {
        initColumn(columnData.nested[i], node);
    }

    var node = findNode(availableColumnsTree.root, columnData.full_name);
    if (node && !node.hasChildNodes()) {
        node.remove();
    }
}


function onWindowShow() {
    var reportTemplateColumns = {{ component.columns|jsonify }};

    for (var i = 0; i < reportTemplateColumns.length; i++) {
        initColumn(reportTemplateColumns[i], reportColumnsTree.root);
    }

    reportColumnsTree.root.cascade(function(node) {
        node.expand();
        if (node.attributes.is_fake==true && node.leaf==true){
            node.ui.addClass('report-constructor-red');
        }
    });

    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление колонки в комбо-бокс на панели с параметрами фильтра. #}

    reportColumnsTree.root.cascade(function(node) {
        if (node.isLeaf()) {
            var hierarchy = [];
            node.bubble(function(n) {
                if (n !== reportColumnsTree.root) {
                    hierarchy.unshift(n.attributes.title);
                }
            });
            filterColumnField.store.add(
                new filterColumnField.store.recordType({
                    name: node.attributes.full_name,
                    title: hierarchy.join(' → ')
                })
            );
        }
    });
    filterColumnField.store.sort('title', 'ASC');
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление фильтров шаблона в грид фильтров. #}

    var filterParams = {{ component.filters|jsonify }};
    if (filterParams && filterParams.length) {
        // {# В UI поддерживаем только одноуровневые выражения. #}
        filterParams = filterParams[0];

        var mainOperator = Object.keys(filterParams)[0];
        filterGroupOperatorField.setValue(mainOperator);

        var reportTemplateFilters = filterParams[mainOperator];
        reportTemplateFilters.map(function(params) {
            filtersGridStore.add(new filtersGridStore.recordType({
                column: params.column,
                operator: params.operator,
                exclude: params.exclude,
                case_sensitive: params.case_sensitive,
                values: params.values.join('|'),
                comment: params.comment
            }));
        });
    }
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}
    // {# Добавление параметров сортировки в окно. #}

    var sortingParams = {{ component.sorting|jsonify }};

    if (sortingParams && sortingParams.length) {
        sortingParams.map(function(params) {
            sortingGridStore.add(new sortingGridStore.recordType({
                column: params.column,
                direction: params.direction
            }));
        });
    }

    reportColumnsTree.root.cascade(function(node) {
        if (node.isLeaf()) {
            sortingColumnField.store.add(
                new sortingColumnField.store.recordType({
                    name: node.attributes.full_name,
                    title: getFullTitle(node)
                })
            );
        }
    });
    // {# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#}

    win.un('show', onWindowShow);
}
win.on('show', onWindowShow);


// {# Удаляет из загруженных колонок те, которые уже добавлены в шаблон. #}
availableColumnsTree.loader.on('load', function(loader, loadedNode) {
    // {# Узел в дереве колонок отчёта, соответствущий загружаемому #}
    var reportColumnNode;
    if (loadedNode.attributes.full_name) {
        reportColumnNode = findNode(
            reportColumnsTree.root, loadedNode.attributes.full_name
        );
    } else {
        reportColumnNode = reportColumnsTree.root;
    }

    if (reportColumnNode) {
        reportColumnNode.eachChild(function(node) {
            if (node.attributes.leaf) {
                var n = loadedNode.findChild(
                    'full_name', node.attributes.full_name
                );
                if (n)
                    n.remove();
            }
        });
    }
});
//{# ----------------------------------------------------------------------- #}

//{# Обработчик Drag'n'Drop #}
function onBeforeDrop(dropObj){
    var selModel = dropObj.source.tree.getSelectionModel(),
        selected = selModel.getSelectedNode(),
        target = dropObj.target,
        append = (dropObj.point==='append');
    dropObj.dropStatus = selected.parentNode === target.parentNode && !append;
    return dropObj.dropStatus
}
//{# ----------------------------------------------------------------------- #}


// {# При деактивации полей в Python нет кнопки отображения выпадающего #}
// {# списка вариантов. #}
filterColumnField.disable();
filterOperatorField.disable();


function setFieldValue(field, value) {
    if (field instanceof Ext.form.Checkbox) {
        field.originalValue = !!value;
        field.setValue(!!value);
    } else if (value) {
        var oldValue = field.getValue();
        field.originalValue = value;
        field.setValue(value);
        field.fireEvent('change', field, value, oldValue);
    } else if (field instanceof Ext.form.ComboBox) {
        field.originalValue = '';
        field.clearValue();
    } else {
        field.originalValue = null;
        field.setValue(null);
    }
}


filtersGridSM.on('rowselect', function(sm, rowIndex, record) {
    // Деактивируем кнопку удаления фильтра если режим read_only
    deleteFilterButton.setDisabled(tplEditWindowReadOnly);

    filterParamsFields.forEach(function(field) {
        setFieldValue(field, record.get(field.name));
        field.enable();
    });
});
filtersGridSM.on('rowdeselect', function(sm, rowIndex, record) {
    deleteFilterButton.disable();

    filterParamsFields.forEach(function(field) {
        if (field.isValid()) {
            var oldValue = record.get(field.name);
            var newValue = field.getValue();
            if (oldValue != newValue && (!!oldValue || !!newValue)) {
                record.set(field.name, newValue);
            }
            setFieldValue(field, null);
        }
        field.disable();
    });
});


function onFilterParamChange(field, newValue, oldValue) {
    var record = filtersGridSM.getSelected();
    if (record) {
        if (record.get(field.name) != newValue) {
            record.set(field.name, newValue);
        }
    }
}
filterParamsFields.forEach(function(field) {
    field.on('change', onFilterParamChange);
});


filterColumnField.on('change', function(field, newValue, oldValue) {
    if (!newValue)
        return;

    var columnNode = findNode(reportColumnsTree.root, newValue);
    if (!columnNode)
        return;

    var validOperators = VALID_OPERATORS[columnNode.attributes.data_type];
    if (!validOperators)
        return;

    var store = filterOperatorField.getStore();
    store.removeAll();
    for (var i = 0; i < OPERATOR_CHOICES.length; i++) {
        var operator = OPERATOR_CHOICES[i][0];
        if (validOperators.indexOf(operator) != -1) {
            var displayText = OPERATOR_CHOICES[i][1];

            var params = {};
            params[filterOperatorField.valueField] = operator;
            params[filterOperatorField.displayField] = displayText;
            store.add(new store.recordType(params));
        }
    }
});


// {# Подсказка для поля "Значение" при использовании оператора #}
// {# "Равно одному из". #}
filterOperatorField.on('change', function(field, newValue, oldValue) {
    var text;

    filterValueField.enable()

    switch (newValue) {
        case OPERATOR_IS_NULL:
            filterValueField.setValue(null);
            filterValueField.disable();
            text = 'Для оператора "Пусто" не предусмотрено значения';
            break;

        case OPERATOR_IN:
            text = 'Для разделения значений используйте символ |';
            break;

        case OPERATOR_BETWEEN:
            text = (
                'Для разделения минимального и максимального значений ' +
                'используйте символ |'
            );
            break;
    }

    if (text) {
        Ext.QuickTips.register({
            target: filterValueField,
            text: text
        });
    } else {
        Ext.QuickTips.unregister(filterValueField);
    }
});
win.on('beforeclose', function() {
    Ext.QuickTips.unregister(filterValueField);
});


function setFiltersTitleColumns(record) {
    var i = filterColumnField.store.find('name', record.get('column'));
    if (i != -1) {
        var r = filterColumnField.store.getAt(i);
        record.set('column_title', r.get('title'));
    } else {
        record.set('column_title', null);
    }

    var operator = record.get('operator');
    var operatorTitle = null;
    for (var j = 0; j < OPERATOR_CHOICES.length; j++) {
        if (operator == OPERATOR_CHOICES[j][0]) {
            operatorTitle = OPERATOR_CHOICES[j][1];
            break;
        }
    }
    record.set('operator_title', operatorTitle);
}
filtersGridStore.on('add', function(store, records, index) {
    records.forEach(setFiltersTitleColumns);
});
filtersGridStore.on('update', function(store, record, operation) {
    if (operation == Ext.data.Record.EDIT) {
        setFiltersTitleColumns(record);
    }
});


function addFilter() {
    filtersGridStore.add(new filtersGridStore.recordType({}));
    filtersGridSM.selectLastRow();
}


function deleteFilter() {
    var record = filtersGridSM.getSelected();
    if (record) {
        filtersGridStore.remove(record);

        filterParamsFields.forEach(function(field) {
            setFieldValue(field, null);
            field.disable();
        });
    }
}
// {# ---------------------------------------------------------------------- #}
// {# Сортировка #}


// {# При деактивации полей в Python нет кнопки отображения выпадающего #}
// {# списка вариантов. #}
sortingColumnField.disable();
sortingDirectionField.disable();


function addSort() {
    sortingGridStore.add(new sortingGridStore.recordType({}));
    sortingGridSM.selectLastRow();
}


function deleteSort() {
    var record = sortingGridSM.getSelected();
    if (record) {
        sortingGridStore.remove(record);

        sortingParamsFields.forEach(function(field) {
            setFieldValue(field, null);
            field.disable();
        });
    }
}


// {# Меняет местами записи в сторе. #}
function swapRecords(store, record1, record2) {
    var rowIndex1 = store.indexOf(record1);
    var rowIndex2 = store.indexOf(record2);

    store.remove(record1);
    store.remove(record2);

    if (rowIndex1 < rowIndex2) {
        store.insert(rowIndex1, record2);
        store.insert(rowIndex2, record1);
    } else {
        store.insert(rowIndex2, record1);
        store.insert(rowIndex1, record2);
    }
}


// {# Обработчик нажатия кнопки "Переместить вверх". #}
function moveSortUp() {
    var record1 = sortingGridSM.getSelected();
    var rowIndex1 = sortingGridStore.indexOf(record1);
    var record2 = sortingGridStore.getAt(rowIndex1 - 1);

    swapRecords(sortingGridStore, record1, record2);

    sortingGridSM.selectRow(rowIndex1 - 1);
}


// {# Обработчик нажатия кнопки "Переместить вниз". #}
function moveSortDown() {
    var record1 = sortingGridSM.getSelected();
    var rowIndex1 = sortingGridStore.indexOf(record1);
    var record2 = sortingGridStore.getAt(rowIndex1 + 1);

    swapRecords(sortingGridStore, record1, record2);

    sortingGridSM.selectRow(rowIndex1 + 1);
}


sortingGridSM.on('rowselect', function(sm, rowIndex, record) {
    // Деактивируем кнопки если режим read_only
    deleteSortButton.setDisabled(tplEditWindowReadOnly);
    moveSortUpButton.setDisabled((rowIndex == 0) || tplEditWindowReadOnly);
    moveSortDownButton.setDisabled((rowIndex == sortingGridStore.getCount() - 1) || tplEditWindowReadOnly);

    sortingParamsFields.forEach(function(field) {
        setFieldValue(field, record.get(field.name));
        field.enable();
    });
});
sortingGridSM.on('rowdeselect', function(sm, rowIndex, record) {
    deleteSortButton.disable();
    moveSortUpButton.disable();
    moveSortDownButton.disable();

    sortingParamsFields.forEach(function(field) {
        if (field.isValid()) {
            var oldValue = record.get(field.name);
            var newValue = field.getValue();
            if (oldValue != newValue && (!!oldValue || !!newValue)) {
                record.set(field.name, newValue);
            }
            setFieldValue(field, null);
        }
        field.disable();
    });
});


function onSortingParamChange(field, newValue, oldValue) {
    var record = sortingGridSM.getSelected();
    if (record) {
        var recordValue = record.get(field.name);
        if (recordValue != newValue) {
            record.set(field.name, newValue);
        }
    }
}
sortingParamsFields.forEach(function(field) {
    field.on('change', onSortingParamChange);
});


function setSortingTitleColumns(record) {
    reportColumnsTree.root.cascade(function(node) {
        if (node.attributes.full_name == record.get('column')) {
            record.set('column_title', getFullTitle(node));
        }
    });

    var direction = record.get('direction');
    var directionTitle = null;
    for (var j = 0; j < DIRECTION_CHOICES.length; j++) {
        if (direction === DIRECTION_CHOICES[j][0]) {
            directionTitle = DIRECTION_CHOICES[j][1];
            break;
        }
    }
    record.set('direction_title', directionTitle);
}
sortingGridStore.on('add', function(store, records, index) {
    records.forEach(setSortingTitleColumns);
});
sortingGridStore.on('update', function(store, record, operation) {
    if (operation == Ext.data.Record.EDIT) {
        setSortingTitleColumns(record);
    }
});
//{# ----------------------------------------------------------------------- #}
// {# Работа с агрегаторами #}
// {# Устанавливает соответствующий тип итога для колонки. #}
function setColumnAggregator(aggregator_type, code, name) {
    var node = reportColumnsSM.getSelectedNode(),
        title = aggregator_type+'_title',
        column_map = {
            'by_value': 4,
            'total': 6
        };

    if (!node || !node.leaf) {
        Ext.Msg.alert('Внимание!', 'Выберите колонку для добавления в отчет.');
        return;
    }
    if (!node.attributes.visible) {
        Ext.Msg.alert('Внимание!', 'Выбранная колонка должна отображаться в отчете.');
        return;
    }
    node.attributes[aggregator_type] = code;
    node.attributes[title] = name;

    // Причины такого решения аналогичны функции switchColumnVisibility
    node.ui.getEl().children[0].children[column_map[aggregator_type]].children[0].textContent = (
        node.attributes[title]
    );
}

function setByValueCountAggregator() {
    setColumnAggregator('by_value', 1, 'Количество');
}
function setByValueSumAggregator() {
    setColumnAggregator('by_value', 2, 'Сумма');
}
function setByValueNoneAggregator() {
    setColumnAggregator('by_value', null, '');
}

function setTotalCountAggregator() {
    setColumnAggregator('total', 1, 'Количество');
}
function setTotalSumAggregator() {
    setColumnAggregator('total', 2, 'Сумма');
}
function setTotalCountUniqueAggregator() {
    setColumnAggregator('total', 3, 'Количество уникальных');
}
function setTotalNoneAggregator() {
    setColumnAggregator('total', null, '');
}
