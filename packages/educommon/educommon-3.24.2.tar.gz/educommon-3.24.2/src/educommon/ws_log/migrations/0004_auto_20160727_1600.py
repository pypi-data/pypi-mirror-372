from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0003_add_fields_to_smev_logs'),
    ]

    operations = [
        migrations.RunSQL(
            """ALTER TABLE ws_log_smevprovider ALTER COLUMN source
            TYPE smallint USING (source::smallint);""",
            reverse_sql=(
                """ALTER TABLE ws_log_smevprovider ALTER COLUMN source
            TYPE varchar(100) USING (source::varchar(100));"""
            ),
        ),
        migrations.AlterField(
            model_name='smevprovider',
            name='source',
            field=models.PositiveSmallIntegerField(
                choices=[(0, 'ЕПГУ'), (1, 'РПГУ'), (2, 'Межведомственное взаимодействие')],
                default=0,
                verbose_name='Источник взаимодействия',
            ),
        ),
    ]
