from django.db import (
    migrations,
)

from educommon.audit_log.utils.operations import (
    ReinstallAuditLog,
)


class Migration(migrations.Migration):
    dependencies = [
        ('audit_log', '0004_reinstall_audit_log'),
    ]

    operations = [
        ReinstallAuditLog(),
        migrations.AlterModelOptions(
            name='auditlog',
            options={
                'verbose_name': '\u0417\u0430\u043f\u0438\u0441\u044c \u0436\u0443\u0440\u043d\u0430\u043b\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439',
                'verbose_name_plural': '\u0417\u0430\u043f\u0438\u0441\u0438 \u0436\u0443\u0440\u043d\u0430\u043b\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439',
            },
        ),
    ]
