from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0004_reportfilter_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportcolumn',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Видимость колонки в отчете'),
        ),
    ]
