import sys
from os.path import (
    normcase,
    realpath,
)

from pkg_resources import (
    working_set,
)


def get_installed_distributions():
    """Возвращает информацию об установленных в окружении пакетах.

    :rtype: list of :class:`~pkg_resources.Distribution`.
    """
    stdlib_pkgs = (
        'python',
        'wsgiref',
        'argparse',
    )

    # pylint: disable=not-an-iterable
    for dist in working_set:
        if dist.key not in stdlib_pkgs and normcase(realpath(dist.location)).startswith(realpath(sys.prefix)):
            yield dist
