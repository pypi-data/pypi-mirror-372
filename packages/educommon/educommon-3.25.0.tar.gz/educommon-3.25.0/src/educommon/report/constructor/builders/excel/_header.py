from educommon.utils.misc import (
    cached_property,
)


class HierarchicalHeaderMixin:
    """Класс-примесь к построителям отчетов для формирования заголовка."""

    @cached_property
    def __column_descriptors(self):
        result = []

        for report_column in self._report_columns:
            if not report_column.visible:
                continue

            accessor_name = report_column.name
            descriptor = self._data_source.get_column_descriptor(accessor_name)
            root = descriptor.root
            if root not in result:
                result.append(root)

        return tuple(result)

    def __get_header_row_count(self):
        # Определение количества строк, занимаемых заголовком.

        if not self.__column_descriptors:
            return 0

        def get_row_count(root_descriptors):
            # Возвращает количество строк, занимаемое заголовком.
            return max(
                (1 + get_row_count(descriptor.children) if descriptor.children else 1)
                for descriptor in root_descriptors
            )

        return get_row_count(self.__column_descriptors)

    @cached_property
    def __header_cell_style(self):
        result = self._workbook.add_format()

        result.set_bold()
        result.set_border()
        result.set_align('center')
        result.set_align('vcenter')
        result.set_text_wrap()

        return result

    def _flush_header(self):
        # Определение размеров ячеек заголовка.
        self._header_row_count = self.__get_header_row_count()

        def set_rows_count(descriptor, level=0):
            if descriptor.children:
                descriptor.height = 1
                for child in descriptor.children:
                    set_rows_count(child, level + 1)
            else:
                descriptor.height = self._header_row_count - level

        def set_column_count(descriptor):
            if descriptor.children:
                descriptor.width = sum(set_column_count(child) for child in descriptor.children)
            else:
                descriptor.width = 1

            return descriptor.width

        for descriptor in self.__column_descriptors:
            set_rows_count(descriptor)
            set_column_count(descriptor)
        # ---------------------------------------------------------------------
        # Запись данных заголовка

        row_cursors = [0] * self._header_row_count

        def flush(descriptors):
            for descriptor in descriptors:
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Определение верхней строки и левого столбца ячейки.

                row_number = descriptor.level
                column_number = row_cursors[row_number]
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Запись данных ячейки в отчет.

                if descriptor.width == 1 and descriptor.height == 1:
                    self._worksheet.write(
                        row_number,
                        column_number,
                        descriptor.title,
                        self.__header_cell_style,
                    )
                else:
                    self._worksheet.merge_range(
                        row_number,
                        column_number,
                        row_number + descriptor.height - 1,
                        column_number + descriptor.width - 1,
                        descriptor.title,
                        self.__header_cell_style,
                    )
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Вычисление следующей позиции курсора в строке.

                for i in range(descriptor.height):
                    row_cursors[descriptor.level + i] += descriptor.width
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Запись ячеек заголовка для вложенных столбцов.

                if descriptor.children:
                    flush(descriptor.children)
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        flush(self.__column_descriptors)

        self._worksheet.freeze_panes(self._header_row_count, 0)
