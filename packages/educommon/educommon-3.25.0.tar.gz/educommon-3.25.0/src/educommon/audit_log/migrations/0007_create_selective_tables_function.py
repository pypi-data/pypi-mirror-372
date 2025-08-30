from django.conf import (
    settings,
)
from django.db import (
    connections,
    migrations,
)


def drop_select_table_function(apps, schema_editor):
    """Удаляется функция из БД."""
    if schema_editor.connection.alias != settings.DEFAULT_DB_ALIAS:
        return

    cursor = connections[settings.DEFAULT_DB_ALIAS].cursor()
    cursor.execute(
        '\n'.join(
            (
                'SELECT',
                "audit.drop_functions_by_name('set_for_selective_tables_triggers');",
            )
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('audit_log', '0006_auto_20200806_1707'),
    ]

    operations = [
        migrations.RunPython(
            code=migrations.RunPython.noop,  # Убрано в версии 3.3.0
            reverse_code=drop_select_table_function,
        ),
    ]
