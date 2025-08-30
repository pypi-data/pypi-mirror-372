from typing import (
    Dict,
)

from educommon.audit_log.models import (
    AuditLog,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)


# Маппинг операции из audit_log
LOG_OPERATION_MAP: Dict[str, EntityLogOperation] = {
    AuditLog.OPERATION_CREATE: EntityLogOperation.CREATE,
    AuditLog.OPERATION_UPDATE: EntityLogOperation.UPDATE,
    AuditLog.OPERATION_DELETE: EntityLogOperation.DELETE,
}
