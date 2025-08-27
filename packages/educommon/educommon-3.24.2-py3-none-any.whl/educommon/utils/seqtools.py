from itertools import (
    chain,
    islice,
)
from typing import (
    Iterable,
)


def make_chunks(
    iterable: Iterable,
    size: int,
    is_list: bool = False,
):
    """Эффективный метод нарезки итерабельного объекта на куски."""
    iterator = iter(iterable)

    for first in iterator:
        yield (
            list(chain([first], islice(iterator, size - 1))) if is_list else chain([first], islice(iterator, size - 1))
        )
