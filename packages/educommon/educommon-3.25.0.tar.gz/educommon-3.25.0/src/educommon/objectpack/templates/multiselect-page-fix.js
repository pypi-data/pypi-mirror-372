/*  {% comment %}
 *
 *  Фикс, для грида с колонкой чекбоксов, исправляющий сброс
 *  чекбоксов при переходе на другую страницу в гриде и добавляющий
 *  возможность выбрать элементы на всех страницах сразу
 *
 *
 *  Для использования в шаблоне окна с гридом необходимо указать:
 *    {% include "ui-js/multiselect-page-fix.js" %}
 *    а затем выполнить applyMultiSelectFix(gridVariableName)
 *      где gridVariableName - имя переменной, в которой хранится грид
 *
 *  Фикс основывается на шаблоне objectpack/templates/multi-select-window.js,
 *  отличительная особенность в том, что фикс реализован в виде функции и может
 *  быть применен к нескольким гридам на одном окне.
 *
 *  {% endcomment %}
 */

function applyMultiSelectFix(grid) {

    Ext.apply(grid, {

        initMultiSelect:function() {
            var mask = new Ext.LoadMask(this.body);
            var store = this.getStore();
            this.checkedItems = {};
            this.mask = mask;
            this.allRecordsStore = new Ext.data.Store({
                model: store.model,
                recordType: store.recordType,
                proxy: store.proxy,
                reader: store.reader,
                sortInfo: store.sortInfo
            });
            this.isAllRecordsSelected = false;
            this.checkBoxSelectTooltip = "Отменить выбор записей на всех страницах";
            this.checkBoxDeSelectTooltip = "Выбрать записи на всех страницах";

            this.on('headerclick', this.onChangeAllRecordsSelection, this);
            this.getStore().on('load', this.onGridStoreLoad, this);
            this.getSelectionModel().on('rowselect', this.onCheckBoxSelect, this);
            this.getSelectionModel().on('rowdeselect', this.onCheckBoxDeselect, this);
            this.allRecordsStore.on('loadexception', function(){mask.hide();}, this);
            this.allRecordsStore.on('load', this.onAllStoreLoad, this);
            this.on('beforedeleterequest', this.modifyDeleteRequest, this);
        },

        onAllStoreLoad: function(store, records, options){
            pageCount = Math.ceil(
                store.getTotalCount()/this.getBottomToolbar().pageSize
            );
            var message=String.format(
                'Выбрано {0} элементов на {1} страницах',
                store.getTotalCount(),
                pageCount
            );
            store.each(function(record){
                grid.checkedItems[record.id] = record;
            });
            Ext.Msg.show({title: 'Внимание', msg: message, buttons: Ext.Msg.OK,
                icon: Ext.MessageBox.INFO});
            this.mask.hide();
        },

        onGridStoreLoad:function(store, records, options) {
            var i = 0, j = 0, recordsToSelect = [];
            var headerCell = this.getView().getHeaderCell(0);
            for (;i < records.length;i++) {
                if (this.checkedItems[records[i].data.id]) {
                    recordsToSelect.push(records[i]);
                }
            }
            headerCell.title = this.checkBoxDeSelectTooltip;
            this.getSelectionModel().selectRecords(recordsToSelect);
            if (this.isAllRecordsSelected){
                this.selectAllRecordsCheckBox();
            }
        },

        onCheckBoxSelect:function(selModel, rowIndex, record) {
            if (!this.checkedItems[record.data.id] ) {
                this.checkedItems[record.data.id] = record.copy();
            }
        },

        onCheckBoxDeselect:function(selModel, rowIndex, record) {
            if (this.checkedItems[record.id]) {
                delete this.checkedItems[record.id];
                this.isAllRecordsSelected = false;
                this.deselectAllRecordsCheckBox();
            }
        },

        onChangeAllRecordsSelection:function(grid, columnIndex, event) {
            var headerCell = grid.getView().getHeaderCell(0);
            if (columnIndex != 0)
                return;
            if (this.isAllRecordsCheckBoxSelected()){
                this.selectAllRecords();
                this.isAllRecordsSelected = true;
                headerCell.firstChild.title = this.checkBoxSelectTooltip;
            } else {
                this.deselectAllRecords();
                headerCell.firstChild.title = this.checkBoxDeSelectTooltip;
            }
        },

        deselectAllRecordsCheckBox:function(){
            var headerCell = this.getView().getHeaderCell(0);
            headerCell.firstChild.classList.remove('x-grid3-hd-checker-on');
            headerCell.firstChild.title = this.checkBoxDeSelectTooltip;
        },

        selectAllRecordsCheckBox:function(){
            var headerCell = this.getView().getHeaderCell(0);
            headerCell.firstChild.classList.add('x-grid3-hd-checker-on');
            headerCell.firstChild.title = this.checkBoxSelectTooltip;
        },

        isAllRecordsCheckBoxSelected:function(){
            var headerCell = this.getView().getHeaderCell(0);
            return Array.from(
                headerCell.firstChild.classList.values()
            ).includes('x-grid3-hd-checker-on');
        },

        deselectAllRecords: function(){
            this.checkedItems = [];
            win.actionContextJson['selected_ids'] = [];
        },

        selectAllRecords: function(){
            this.allRecordsStore.baseParams = Ext.applyIf(
                {start: 0, limit:0},
                this.getStore().baseParams
            );
            this.allRecordsStore.reload();
            this.mask.show();
        },

        modifyDeleteRequest: function(scope, req){
            req['params'][scope.rowIdName] = this.getCheckedIdsString();
        },

        getCheckedIds: function (){
            return Object.keys(this.checkedItems)
        },

        getCheckedIdsString: function () {
            return this.getCheckedIds().join(',');
        },

        getCheckedArray: function () {
            var checkedArray = [];
            var checked = this.checkedItems;
            this.getCheckedIds().forEach(function (rec_id) {
                rec_id = parseInt(rec_id);
                checkedArray.push(checked[rec_id])
            });
            return checkedArray;
        }
    });

    grid.initMultiSelect()
}
