from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0006_auto_20170327_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smevlog',
            name='source',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, 'ЕПГУ'), (1, 'РПГУ'), (2, 'Межведомственное взаимодействие'), (3, 'Барс-Образование')],
                default=None,
                null=True,
                verbose_name='Источник взаимодействия',
            ),
        ),
        migrations.AlterField(
            model_name='smevprovider',
            name='source',
            field=models.PositiveSmallIntegerField(
                choices=[(0, 'ЕПГУ'), (1, 'РПГУ'), (2, 'Межведомственное взаимодействие'), (3, 'Концентратор')],
                verbose_name='Источник взаимодействия',
            ),
        ),
    ]
