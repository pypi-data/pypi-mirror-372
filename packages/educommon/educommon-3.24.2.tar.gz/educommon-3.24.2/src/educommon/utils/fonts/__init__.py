"""Средства для работы со шрифтами."""

import os.path

from PIL import (
    ImageFont,
)


# Мнемоники для шрифтов
ARIAL = 1
TAHOMA = 2
CALIBRI = 3


_FONT_FILES = {
    code: os.path.join(os.path.dirname(__file__), file_name)
    for code, file_name in (
        (ARIAL, 'Arial.ttf'),
        (CALIBRI, 'Calibri.ttf'),
        (TAHOMA, 'Tahoma.ttf'),
    )
}


def get_font(font, size=10):
    """Возвращает шрифт указанного семейства.

    :param int font: Поддерживаемое модулем семейство шрифтов.
    :param int size: Размер шрифта.

    :rtype: :class:`PIL.ImageFont.FreeTypeFont`
    """
    assert font in _FONT_FILES, font

    file_path = _FONT_FILES[font]

    return ImageFont.truetype(file_path, size, encoding='utf-8')


def _split_word(font, word, max_width):
    """Разбивает слово на две части.

    Причем первая часть слова содержит наибольшее количество символов
    шрифта font от начала слова, которое умещается в max_width пикселей.

    :param font: Шрифт.
    :type font: :class:`PIL.ImageFont.FreeTypeFont`

    :param str word: Слово, которое требуется разбить.
    :param int max_width: Максимальная длина строки в пикселях.

    :rtype: tuple: (<Часть слова, умещающаяся в max_width>, <остаток>).
    """

    def _split_index(index, max_index=None):
        """Рекурсивно разбивает слово на две части.

        :param int index: Индекс текущего символа.
        :param int max_index: Индекс символа, до которого ширина строки
                              больше максимальной.
        """
        index = int(index)
        assert index > 0, 'Ширины строки не хватает, чтобы поместить один символ'

        # определяем ширину слова в пикселях
        width, _ = font.getsize(word[:index])

        if width > max_width:
            if index == max_index:
                # Если индексы равны, значит предыдущее условие было
                # width < max_width, а предыдущий index на единицу меньше.
                return index - 1

            # Искомый index в интервале: [1; index).
            # Берем его середину.
            return _split_index(index // 2, index)

        elif width < max_width:
            if max_index is None:
                # Нас обманули, слово влазит в одну строку.
                return index

            # Искомый index в интервале: [index; max_index).
            # Берем его середину.
            # Если центрального элемента нет, берем ближний справа,
            # иначе рекурсия не завершится.
            diff = max_index - index
            index += diff // 2 + diff % 2
            return _split_index(index, max_index)

        return index

    idx = _split_index(len(word))
    return word[:idx], word[idx:]


def split_text(text, font, max_width):
    """Разбивает текст на строки с учетом максимальной ширины строки.

    Разбиение осуществляется по словам. Если очередное слово не входит в
    строку, то выполняется перенос строки.

    :param unicode text: Текст, подлежащий разбиению на строки.

    :param font: Шрифт.
    :type font: :class:`PIL.ImageFont.FreeTypeFont`

    :param int max_width: Максимальная длина строки в пикселях.

    :rtype: list
    """
    words = text.split(' ')
    string = []
    strings = [string]
    while words:
        string.append(words[0])
        width, _ = font.getsize(' '.join(string))
        if width >= max_width:
            if len(string) == 1:
                word, tail = _split_word(font, words[0], max_width)
                if len(tail) > 0:
                    words[0] = tail
                else:
                    words.pop(0)
                string[0] = word
            else:
                string.pop()
            string = []
            strings.append(string)
        else:
            words.pop(0)
    return tuple(' '.join(s) for s in strings if s)
