from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0005_auto_20161130_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smevprovider',
            name='service_address_status_changes',
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name='Адрес сервиса изменения статуса'
            ),
        ),
    ]
