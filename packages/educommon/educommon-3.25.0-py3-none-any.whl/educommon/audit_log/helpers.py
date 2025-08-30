from collections.abc import (
    Iterable,
)
from typing import (
    TYPE_CHECKING,
    Iterable as IterableType,
    List,
    Union,
)

from educommon.audit_log.models import (
    Table,
)


if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )


def get_models_table_ids(models: Union['Model', IterableType['Model']]) -> List[int]:
    """Возвращает перечень id таблиц из AuditLog соответствующих указанным моделям."""
    if not isinstance(models, Iterable):
        models = (models,)

    table_ids = Table.objects.filter(
        name__in=(model._meta.db_table for model in models),
    ).values_list('id', flat=True)

    return table_ids
