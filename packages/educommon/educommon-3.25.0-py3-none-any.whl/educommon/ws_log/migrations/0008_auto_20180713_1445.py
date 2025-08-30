from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0007_auto_20180607_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smevlog',
            name='source',
            field=models.PositiveSmallIntegerField(
                default=None,
                null=True,
                verbose_name='Источник взаимодействия',
                blank=True,
                choices=[
                    (0, 'ЕПГУ'),
                    (1, 'РПГУ'),
                    (2, 'Межведомственное взаимодействие'),
                    (3, 'Барс-Образование'),
                    (4, 'Концентратор'),
                    (5, 'МФЦ'),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='smevprovider',
            name='source',
            field=models.PositiveSmallIntegerField(
                verbose_name='Источник взаимодействия',
                choices=[
                    (0, 'ЕПГУ'),
                    (1, 'РПГУ'),
                    (2, 'Межведомственное взаимодействие'),
                    (3, 'Барс-Образование'),
                    (4, 'Концентратор'),
                    (5, 'МФЦ'),
                ],
            ),
        ),
    ]
