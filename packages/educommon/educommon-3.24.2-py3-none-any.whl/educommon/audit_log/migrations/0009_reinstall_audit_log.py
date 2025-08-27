from django.db import (
    migrations,
)

from educommon.audit_log.utils.operations import (
    ReinstallAuditLog,
)


class Migration(migrations.Migration):
    dependencies = [
        ('audit_log', '0008_table_logged'),
    ]

    operations = [
        ReinstallAuditLog(),
    ]
