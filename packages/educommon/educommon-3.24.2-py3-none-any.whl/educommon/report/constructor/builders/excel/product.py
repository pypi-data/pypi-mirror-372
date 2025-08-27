from datetime import (
    date,
    datetime,
    time,
)
from functools import (
    partial,
)
from itertools import (
    chain,
    product,
)

from educommon.report.constructor.builders.excel._base import (
    ReportBuilderBase,
    is_block,
)
from educommon.report.constructor.builders.excel._header import (
    HierarchicalHeaderMixin,
)
from educommon.utils.misc import (
    cached_property,
)


class _Cell:
    """Класс для хранения значения ячейки отчета и порядкового номера ячейки.

    Позволяет сортировать ячейки в соответстии с их порядковым номером.
    """

    def __init__(self, index, value):
        self.index = index
        self.value = value

    def __lt__(self, other):
        return self.index < other.index


def _join(simple_data, block_indexes, block_row_data):
    """Объединяет данные основной записи и данные строки блока"""

    # Проставление порядковых номеров
    block_row_data = tuple(_Cell(index, data) for index, data in zip(block_indexes, block_row_data))

    # Объединение данных блока и данных записи + упорядочивание.
    block_row_data = sorted(simple_data + block_row_data)

    # Преобразование данных в "плоский" кортеж (удаление вложенных кортежей).
    return tuple(
        chain(*((cell.value if isinstance(cell.value, (tuple, list)) else (cell.value,)) for cell in block_row_data))
    )


class ReportBuilder(HierarchicalHeaderMixin, ReportBuilderBase):
    """Построитель отчета в формате Excel без объединения ячеек.

    В случае, если столбцы формируемого отчета связаны отношением один ко
    многим (обратные связи), формируется декартово произведение связанных
    записей как при объединении таблиц в SQL.
    """

    @cached_property
    def _data_cell_style(self):
        result = self._workbook.add_format()

        result.set_border()
        result.set_text_wrap()
        result.set_align('vcenter')

        return result

    @staticmethod
    def _data_to_rows(data):
        """Возвращает данные отчета в виде декартова произведения.

        В зависимости от значения аргумента :arg:`data` выполняет следующие
        преобразования данных:

            * *Блоки записей*: для каждой записи блока рекурсивно вызывает
              функцию :meth:`_data_to_rows`, полученные строки объединяет в
              новый блок и возвращает его в качестве результата. Записи
              полученного блока не будут содержать вложенных блоков.
            * *Записи*: Если в записи есть вложенные блоки, то вычисляется
              декартово произведение записей вложенных блоков и данных самой
              записи. Результат возвращается в виде блока записей.
        """
        if is_block(data):
            return tuple(chain(*(ReportBuilder._data_to_rows(row) for row in data)))

        else:
            # Все вложенные блоки записи нужно преобразовать к плоской
            # структуре, чтобы они содержали только данные (без вложенных
            # блоков). Т.е. в итоге не должно быть многоуровневой вложенности.
            data = tuple(ReportBuilder._data_to_rows(cell) if is_block(cell) else cell for cell in data)

            # После того, как избавились от вложенных блоков, нужно вычислить
            # декартово произведение данной записи и вложенных в неё блоков.
            # Для этого нужно разделить все данные в записи на простые данные и
            # вложенные блоки. Затем записи вложенных блоков перемножить между
            # собой. В результате получим набор записей
            simple_indexes = []  # индексы ячеек с данными
            block_indexes = []  # индексы ячеек с вложенными блоками
            for index, cell in enumerate(data):
                store = block_indexes if is_block(cell) else simple_indexes
                store.append(index)

            simple_data = tuple(_Cell(index, data[index]) for index in simple_indexes)
            blocks_data = product(*(cell_data for cell_data in data if is_block(cell_data)))

            join = partial(_join, simple_data, block_indexes)
            return tuple(map(join, blocks_data))

    def _flush_data(self):
        rows_data = self._data_to_rows(self._data)

        for row_number, row in enumerate(rows_data, self._header_row_count):
            for column_number, cell_data in enumerate(row):
                if isinstance(cell_data, (date, time, datetime)):
                    style = None
                else:
                    style = self._data_cell_style

                self._worksheet.write(row_number, column_number, cell_data, style)
