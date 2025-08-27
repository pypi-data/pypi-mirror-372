import datetime

import django.core.validators
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('audit_log', '0005_postgresql_error'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postgresqlerror',
            name='time',
            field=models.DateTimeField(
                auto_now_add=True,
                validators=[django.core.validators.MinValueValidator(datetime.datetime(1900, 1, 1, 0, 0))],
                verbose_name='Дата, время',
            ),
        ),
    ]
