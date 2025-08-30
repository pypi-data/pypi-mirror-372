from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0009_auto_20180405_0642'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportcolumn',
            name='by_value',
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(1, 'Количество'), (2, 'Сумма')], null=True, verbose_name='Промежуточный итог'
            ),
        ),
        migrations.AddField(
            model_name='reportcolumn',
            name='total',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, 'Количество'), (2, 'Сумма'), (3, 'Количество уникальных')],
                null=True,
                verbose_name='Итог',
            ),
        ),
    ]
