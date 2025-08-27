from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0008_auto_20170407_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporttemplate',
            name='include_available_units',
            field=models.BooleanField(default=False, verbose_name='Отображать данные по дочерним организациям'),
        ),
    ]
