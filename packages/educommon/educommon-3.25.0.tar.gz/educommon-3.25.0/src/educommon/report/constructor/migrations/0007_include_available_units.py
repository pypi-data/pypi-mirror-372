import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0006_reportsorting'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportsorting',
            options={'ordering': ('index',), 'verbose_name': 'Сортировка', 'verbose_name_plural': 'Сортировка'},
        ),
        migrations.AddField(
            model_name='reporttemplate',
            name='include_available_units',
            field=models.BooleanField(default=False, verbose_name='Отображать данные по дочерним учреждениям'),
        ),
        migrations.AlterField(
            model_name='reportfilter',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(blank=True, null=True, verbose_name='Значение'),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name='reportsorting',
            name='column',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sorting',
                to='report_constructor.ReportColumn',
                verbose_name='Колонка',
            ),
        ),
    ]
