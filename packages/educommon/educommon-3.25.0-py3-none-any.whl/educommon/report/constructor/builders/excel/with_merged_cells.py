"""Реализация построителя отчетов."""

from datetime import (
    date,
    datetime,
    time,
)

from educommon.report.constructor.builders.excel._base import (
    ReportBuilderBase,
)
from educommon.report.constructor.builders.excel._header import (
    HierarchicalHeaderMixin,
)
from educommon.utils.misc import (
    cached_property,
)


class Frame:
    def __init__(self, worksheet, top, left, style):
        self._worksheet = worksheet
        self._top = top
        self._left = left
        self._style = style

        self._current_row = 0
        self._current_column = 0

        self._written_rows = 0
        self._written_columns = 0

    @property
    def written_rows(self):
        """Количество строк, записанных в текущей области."""
        return self._written_rows

    @property
    def written_columns(self):
        """Количество колонок, записанных в текущей области."""
        return self._written_columns

    def _nested_frame(self):
        """Создаёт вложенную область отчёта относительно текущей позиции."""
        return Frame(
            worksheet=self._worksheet,
            top=self._top + self._current_row,
            left=self._left + self._current_column,
            style=self._style,
        )

    def new_row(self):
        """Переходит к следующей строке отчёта."""
        self._current_row = self._top + self._written_rows
        self._current_column = self._left

    def _write_cell(self, cell_data, height):
        """Записывает одну ячейку с возможным объединением по вертикали."""
        assert height > 0, height

        if isinstance(cell_data, (date, time, datetime)):
            style = None
        else:
            style = self._style

        top = self._top + self._current_row
        left = self._left + self._current_column
        if height > 1:
            self._worksheet.merge_range(top, left, top + height - 1, left, cell_data, style)
        else:
            self._worksheet.write(
                top,
                left,
                cell_data,
                style,
            )
        self._written_rows = max(height, self._written_rows)
        self._current_column += 1
        self._written_columns += 1

    def _write_block(self, data, row_height=None):
        """Записывает блок строк (вложенных списков) в область отчёта."""
        block_rows = block_columns = 0

        for row_data in data:
            block_frame = self._nested_frame()
            block_frame.write(row_data)
            block_frame.new_row()

            block_rows += block_frame.written_rows
            block_columns = max(block_columns, block_frame.written_columns)

            self._current_row += block_frame.written_rows

        if row_height is not None and block_rows < row_height:
            # Блок не полностью заполняет строку по высоте. Из-за этого
            # появляются необрамленные ячейки. Чтобы этого не было, нужно
            # записать пустые значения в оставшиеся ячейки.
            for _ in range(row_height - block_rows):
                for column in range(block_columns):
                    top = self._top + self._current_row
                    left = self._left + self._current_column + column

                    self._worksheet.write_blank(top, left, None, self._style)

                self._current_row += 1

        self._current_row = 0
        self._written_rows = max(self._written_rows, block_rows)

        self._current_column += block_columns
        self._written_columns += block_columns

    @staticmethod
    def _get_row_height(record_data):
        """Определяет высоту строки с учётом вложенных данных."""
        # Возвращает количество строк, занимаемое записью (с учетом вложенных
        # блоков).

        def get_row_height(cell_data):
            # Возвращает количество строк, которое необходимо
            if isinstance(cell_data, list):
                return max(1, sum(get_row_height(data) for data in cell_data if isinstance(data, list)))
            else:
                return 1

        return max(map(get_row_height, record_data))

    def _write_row(self, data):
        """Записывает одну логическую строку, содержащую ячейки и/или вложенные блоки."""
        row_height = self._get_row_height(data)

        for cell_data in data:
            if isinstance(cell_data, list):
                self._write_block(cell_data, row_height)
            else:
                self._write_cell(cell_data, row_height)

    def write(self, data):
        """Записывает данные в область отчёта: строку, блок или одну ячейку."""
        if all(isinstance(d, list) for d in data):
            self._write_block(data)
        elif isinstance(data, list):
            self._write_row(data)
        else:
            self._write_cell(data, height=1)


class ReportBuilder(HierarchicalHeaderMixin, ReportBuilderBase):
    """Построитель отчетов, основанных на пользовательских шаблонах."""

    @cached_property
    def _data_cell_style(self):
        result = self._workbook.add_format()

        result.set_border()
        result.set_text_wrap()
        result.set_align('vcenter')

        return result

    def _flush_data(self):
        data_frame = Frame(
            self._worksheet,
            top=self._header_row_count,
            left=0,
            style=self._data_cell_style,
        )
        data_frame.write(self._data)
