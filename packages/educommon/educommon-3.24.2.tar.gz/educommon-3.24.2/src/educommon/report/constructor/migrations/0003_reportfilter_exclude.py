from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0002_report_filters'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportfilter',
            name='exclude',
            field=models.BooleanField(default=False, verbose_name='Исключать записи, удовлетворяющие условию'),
        ),
    ]
