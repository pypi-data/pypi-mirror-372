var grid = Ext.getCmp('{{ component.grid.client_id }}');

function revokeTask() {
  var mask = new Ext.LoadMask(win.getEl());
  mask.show();

  if (grid.selModel.hasSelection()) {
    var selections = grid.selModel.getSelections(),
      ids = [];
    for (var i = 0, len = selections.length; i < len; i++) {
      ids.push(selections[i].id);
    }

    Ext.Ajax.request({
      url: '{{ component.revoke_url }}',
      params: {
        async_task_ids: ids.join()
      },
      success: function(response) {
        var result = JSON.parse(response.responseText);
        if (result.success) {
          grid.getStore().reload();
        } else {
          Ext.Msg.show({
            title: 'Внимание',
            msg: result.message,
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.WARNING
          });
        }
        mask.hide();
      },
      failure: function(response, request) {
        uiAjaxFailMessage.apply(this, arguments);
        mask.hide();
      }
    });
  } else {
    mask.hide();
    Ext.Msg.show({
      title: 'Внимание!',
      msg: 'Элемент не выбран!',
      icon: Ext.Msg.QUESTION,
      buttons: Ext.Msg.OK
    });
  }
  store = grid.getStore();
  store.reload();
}
