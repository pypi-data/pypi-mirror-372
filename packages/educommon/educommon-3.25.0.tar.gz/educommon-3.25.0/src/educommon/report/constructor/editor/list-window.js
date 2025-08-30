var grid = Ext.getCmp('{{ component.grid.client_id }}');
var gridStore = grid.getStore();
var gridSM = grid.getSelectionModel();
var buildButton = Ext.getCmp('{{ component.grid.top_bar.button__build.client_id }}');


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
        '.icon-page { ',
        'background-image:url(../icons/page.png) !important;' +
        'background-repeat: no-repeat;' +
        '}'
    );
    insertRule(
        '.icon-page-delete { ',
        'background-image:url(../icons/page_delete.png) !important;' +
        'background-repeat: no-repeat;}'
    );
});


function switchBuildButton(selectionModel, record) {
    if(gridSM.getCount() == 1){
        buildButton.setDisabled(!gridSM.getSelected().json.valid);
    }
}
gridStore.on('load', switchBuildButton);

/*{# Отображает иконку страницы доступности для каждой записи. #}*/
function pageDeleteRenderer(value, metaData, record, rowIndex, colIndex, store) {

    if (record.json.valid == false) {
        metaData.css += 'icon-page-delete';
        metaData.attr = 'ext:qtip="Некоторые колонки шаблона неактуальны, ' +
            'требуется редактирование"';
    } else {
        metaData.css += 'icon-page';
        metaData.attr = '';
    }
    return value;
}

gridSM.on('selectionchange', switchBuildButton);

function buildReport() {
    if (gridSM.hasSelection()) {
        if (gridSM.getCount() > 1) {
            Ext.Msg.alert(
                'Сборка отчета',
                'Должен быть выбран только один элемент.'
            );
        } else if(gridSM.getSelected().json.valid!=true){
            Ext.Msg.show({
               title:'Сборка отчета',
               msg: 'Некоторые колонки шаблона неактуальны, требуется ' +
               'редактирование',
               buttons: Ext.MessageBox.OK,
               icon: Ext.MessageBox.ERROR
            });
        } else {
            var mask = new Ext.LoadMask(win.body);
            mask.show();

            var record = gridSM.getSelected();
            var params = {m3_window_id: win.id};
            params[grid.rowIdName] = record.id;

            Ext.Ajax.request({
                url: '{{ component.build_action_url }}',
                params: params,
                success: function(response, options) {
                    try {
                        smart_eval(response.responseText);
                    } finally {
                        mask.hide();
                    }
                },
                failure: function() {
                    uiAjaxFailMessage.apply(this, arguments);
                    mask.hide();
                }
            });
        }
    }
}
