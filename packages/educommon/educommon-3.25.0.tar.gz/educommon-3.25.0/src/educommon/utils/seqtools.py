from collections import (
    defaultdict,
    namedtuple,
)
from itertools import (
    chain,
    islice,
)
from typing import (
    Iterable,
    Union,
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


# Именованный кортеж содержащий результат работы функции топологической сортировки
Results = namedtuple('Results', ['sorted', 'cyclic'])


def topological_sort(
    dependency_pairs: Iterable[Union[str, tuple[str, str]]],
):
    """Сортировка по степени зависимости.

    print( topological_sort('aa'.split()) )
    print( topological_sort('ah bg cf ch di ed fb fg hd he ib'.split()) )
    Спасибо Raymond Hettinger
    https://bugs.python.org/file48361/topological_sort.py
    """
    num_heads = defaultdict(int)  # num arrows pointing in
    tails = defaultdict(list)  # list of arrows going out
    heads = []  # unique list of heads in order first seen

    for h, t in dependency_pairs:
        num_heads[t] += 1
        if h in tails:
            tails[h].append(t)
        else:
            tails[h] = [t]
            heads.append(h)
    ordered = [h for h in heads if h not in num_heads]
    for h in ordered:
        for t in tails[h]:
            num_heads[t] -= 1
            if not num_heads[t]:
                ordered.append(t)
    cyclic = [n for n, heads in num_heads.items() if heads]

    return Results(ordered, cyclic)
