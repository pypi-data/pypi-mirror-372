import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0005_reportcolumn_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportSorting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'direction',
                    models.PositiveSmallIntegerField(
                        choices=[(1, 'По возрастанию'), (2, 'По убыванию')], verbose_name='Направление сортировки'
                    ),
                ),
                ('index', models.PositiveSmallIntegerField(verbose_name='Порядковый номер')),
                (
                    'column',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='report_constructor.ReportColumn',
                        verbose_name='Колонка',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Сортировка',
                'verbose_name_plural': 'Сортировка',
            },
        ),
    ]
