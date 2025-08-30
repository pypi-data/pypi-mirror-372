from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='Действует с'),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='по'),
        ),
    ]
