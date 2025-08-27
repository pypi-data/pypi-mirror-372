from django.db import (
    migrations,
)

from educommon.audit_log.utils.operations import (
    ReinstallAuditLog,
)


class Migration(migrations.Migration):
    dependencies = [
        ('audit_log', '0003_logproxy'),
    ]

    operations = [ReinstallAuditLog()]
