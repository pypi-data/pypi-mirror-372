"""Средства управления доступом на основе ролей (RBAC).

.. note::
   RBAC - Role Based Access Control.
"""

from django import (
    VERSION as _django_version,
)


assert _django_version >= (1, 8), "{} app doesn't support Django {}.{}.".format(__name__, *_django_version[:2])
