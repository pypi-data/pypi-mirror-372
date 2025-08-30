from educommon.utils.fonts import (
    ARIAL,
    get_font,
    split_text,
)


# Высота и ширина символа "0" шрифта по умолчанию в xlwt.
DEFAULT_CHAR_SIZE = 256


def cm_to_inch(value):
    """Переводит значение из сантиметров в дюймы."""
    return value / 2.54


def inch_to_cm(value):
    """Переводит значение из дюймов в сантиметры."""
    return value * 2.54


def get_cell_bounds(section, row_index, column_index):
    """Возвращает границы ячейки, находящейся на пересечении строки и столбца.

    .. note::

       Индексы строк и колонок начинаются с нуля.

    :param section: Секция, в которой находится строка.
    :type section: :class:`simple_report.xls.section.Section`

    :param int row_index: Индекс строки в таблице excel.

    :param int column_index: Индекс столбца в таблице excel.

    :returns: Кортеж из четырех целых чисел: верхней строки, нижней строки,
        левой колонки и правой колонки.
    :rtype: tuple
    """
    merged_ranges = section.writer.wtsheet.merged_ranges
    for first_row, last_row, first_column, last_column in merged_ranges:
        if first_row <= row_index <= last_row and first_column <= column_index <= last_column:
            return first_row, last_row, first_column, last_column

    return row_index, row_index, column_index, column_index


def get_cell_width(section, row_index, column_index):
    """Возвращает ширину ячейки с учётом объединения.

    .. note ::

       Ширина ячейки определяется, как 1/256 от ширины символа "0" первого
       попавшегося шрифта в файле, т.е. единицы изменения достаточно условны.

    .. note::

       Индексы строк и колонок начинаются с нуля.

    :param section: Секция, в которой находится строка.
    :type section: :class:`simple_report.xls.section.Section`

    :param int row_index: Индекс строки в таблице excel.

    :param int column_index: Индекс столбца в таблице excel.

    :rtype: int
    """
    _, _, first_column, last_column = get_cell_bounds(section, row_index, column_index)
    return sum(section.writer.wtsheet.col(i).width for i in range(first_column, last_column + 1))


def get_cell_height(section, row_index, column_index):
    """Возвращает высоту ячейки с учётом объединения.

    .. note::

       Индексы строк и колонок начинаются с нуля.

    :param section: Секция, в которой находится строка.
    :type section: :class:`simple_report.xls.section.Section`

    :param int row_index: Индекс строки в таблице excel.

    :param int column_index: Индекс столбца в таблице excel.

    :returns: Высоту ячейки в `твипах <https://goo.gl/hfUW7x>`_.
    :rtype: int
    """
    first_row, last_row, _, _ = get_cell_bounds(section, row_index, column_index)
    return sum(section.writer.wtsheet.row(i).height for i in range(first_row, last_row + 1))


def adjust_row_height(section, row_idx, col_idx, text, font, adjusted_row_index=None):
    """Увеличивает высоту строки, если необходимо.

    Высота строки устанавливается такая, чтобы текст `text`
    поместился в ячейку с индексами `row_idx`, `col_idx`.

    Можно применять для нескольких ячеек одной строки. Тогда строке будет
    установлена максимальная высота.

    .. note::

       Индексы строк и колонок начинаются с нуля.

    :param section: Секция, в которой находится строка.
    :type section: :class:`simple_report.xls.section.Section`

    :param int row_idx: Индекс строки в таблице excel.

    :param int col_idx: Индекс столбца в таблице excel.

    :param str text: Строка, которая будет записана в ячейку.

    :param font: Шрифт.
    :type font: :class:`PIL.ImageFont.FreeTypeFont`

    :param int adjusted_row_index: Номер строки, размер которой будет увеличен.
        Если не указывается (``None``), то высота всех строк объединенной
        ячейки будет увеличена равномерно. Номер указывается относительно
        ячейки, нумерация начинается с нуля.
    """

    def get_text_height(column_width):
        """Вычисляет высоту строки отчета в зависимости от текста."""
        # Т.к. высота и ширина ячейки измеряется в единицах относительно
        # дефолтного шрифта, берем его параметры.
        normal_font = get_font(ARIAL, 10)

        # Количество символов "0", которое входит в одну ячейку без переносов.
        # DEFAULT_CHAR_SIZE * 0.8 определяет ширину отступов слева и справа (в
        # сумме, а не каждого отступа по отдельности). Источник точной
        # информации об отступах в ячейке найти не удалось.
        width_in_chars = int(column_width - DEFAULT_CHAR_SIZE * 0.8) // DEFAULT_CHAR_SIZE

        str_width_px, str_height_px = normal_font.getsize('0' * width_in_chars)

        # Определяем коэффициент масштабирования высоты шрифта к дефолтному.
        _, choosen_font_height_px = font.getsize('0')
        height_scale = (choosen_font_height_px * 1.0) / str_height_px

        rows_count = len(split_text(text, font, str_width_px))

        height = int(rows_count * height_scale * DEFAULT_CHAR_SIZE)

        return height

    first_row, last_row, first_column, last_column = get_cell_bounds(section, row_idx, col_idx)

    merged = first_row != last_row or first_column != last_column

    cell_width = get_cell_width(section, row_idx, col_idx)
    cell_height = get_cell_height(section, row_idx, col_idx)

    # Высотя ячейки, в которой поместится указанный текст.
    text_height = get_text_height(cell_width)

    # Разница между текущей высотой ячейки и необходимой для размещения текста
    # высотой.
    height_delta = max(0, text_height - cell_height)

    def add_row_height(row, height):
        row.height_mismatch = True
        row.height += height

    if height_delta > 0:
        if merged:
            row_count = last_row - first_row + 1
            if adjusted_row_index is None:
                # Равномерное увеличение высоты строк
                for r in range(first_row, last_row + 1):
                    row = section.writer.wtsheet.row(r)
                    add_row_height(row, height_delta // row_count)
            else:
                assert adjusted_row_index > row_count, (adjusted_row_index, row_count)
                row = section.writer.wtsheet.row(first_row + adjusted_row_index)
                add_row_height(row, height_delta)
        else:
            row = section.writer.wtsheet.row(row_idx)
            add_row_height(row, height_delta)


def adjust_row_height_arial(section, row_idx, col_idx, text, font_size=10, adjusted_row_index=None):
    """Устанавливает высоту строки автоматически.

    Высота строки устанавливается такая, чтобы текст text
    поместился в ячейку с индексами row_idx, col_idx.

    Расчет ведется для шрифта Arial, и соответствует отображению ячеек в
    MS Excel.

    :param section: Секция, в которой находится строка
    :type section: :class:`simple_report.xls.section.Section`
    :param int row_idx: Индекс строки в таблице excel
    :param int col_idx: Индекс столбца в таблице excel
    :param str text: Строка, которая будет записана в ячейку
    :param int font_size: Размер шрифта в пунктах
    :param int adjusted_row_index: Номер строки, размер которой будет увеличен.
        Если не указывается (``None``), то высота всех строк объединенной
        ячейки будет увеличена равномерно. Номер указывается относительно
        ячейки, нумерация начинается с нуля.
    """
    font = get_font(ARIAL, font_size)
    adjust_row_height(section, row_idx, col_idx, text, font, adjusted_row_index)
