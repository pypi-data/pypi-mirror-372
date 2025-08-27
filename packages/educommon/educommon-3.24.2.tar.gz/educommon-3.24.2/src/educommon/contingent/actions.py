"""Паки справочников контингента."""

from django.db.models import (
    Q,
)

from objectpack.actions import (
    ObjectPack,
)

from educommon.contingent.catalogs import (
    OkoguVirtualModel,
    OksmVirtialModel,
)


class OkoguPack(ObjectPack):
    """Пак, предоставляющий средства для просмотра справочника ОКОГУ."""

    title = 'ОКОГУ'

    model = OkoguVirtualModel

    columns = [
        dict(
            data_index='id',
            header='Код',
            width=1,
            searchable=True,
        ),
        dict(
            data_index='full_name',
            header='Полное наименование',
            width=3,
            searchable=True,
        ),
        dict(
            data_index='short_name',
            header='Сокращенное наименование',
            width=2,
            searchable=True,
        ),
    ]
    list_sort_order = ('id',)
    column_name_on_select = 'full_name'

    def configure_grid(self, grid):
        """Конфигурирование грида.

        Добавляется css класс для переноса строк в ячейках грида
        """
        super().configure_grid(grid)

        grid.cls = 'word-wrap-grid'  # перенос строк в ячейках грида


class OKSMPack(ObjectPack):
    """Справочник ОКСМ."""

    title = 'Справочник ОКСМ'
    model = OksmVirtialModel
    read_only = True
    list_sort_order = ['shortname']
    column_name_on_select = 'shortname'

    columns = [
        {
            'data_index': 'shortname',
            'header': 'Краткое наименование страны',
            'sortable': True,
            'searchable': True,
            'width': 2,
        },
        {
            'data_index': 'code',
            'header': 'Код',
            'sortable': True,
            'searchable': True,
            'width': 1,
        },
        {
            'data_index': 'alpha_3',
            'header': 'Буквенный код',
            'sortable': True,
            'searchable': True,
            'width': 1,
        },
        {
            'data_index': 'full_name',
            'header': 'Полное наименование',
            'sortable': True,
            'searchable': True,
            'width': 3,
        },
    ]

    def get_rows_query(self, request, context):
        """
        Метод выполняет фильтрацию QuerySet.

        Исключается отображение РФ.
        """
        records = super().get_rows_query(request, context)

        return records.exclude(code=OksmVirtialModel.rf_code)

    def apply_search(self, query, request, context):
        """Поиск по краткому наименованию или коду."""
        query = super(OKSMPack, self).apply_search(query, request, context)

        if hasattr(context, 'filter'):
            query = query.filter(Q(shortname__icontains=context.filter) | Q(code=context.filter))

        return query
