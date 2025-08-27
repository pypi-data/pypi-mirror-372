{# подключение шаблона базового окна #}
{% include 'tabbed-window.js' %}


// {# отложенная загрузка данных в гриды #}
(function (){

  var tabGrids = {{ component.lazy_grids|safe }};

  Ext.iterate(tabGrids, function (tabId, gridIds) {

    function loadGridData() {

      Ext.each(gridIds, function (gridId) {
        Ext.getCmp(gridId).store.load();
      });
    }

    var tab = Ext.getCmp(tabId);
    tab.on('activate', loadGridData, tab, {single: true});
  });

})();