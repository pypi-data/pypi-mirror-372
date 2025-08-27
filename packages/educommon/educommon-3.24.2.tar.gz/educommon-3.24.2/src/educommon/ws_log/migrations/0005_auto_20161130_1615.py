import datetime

from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0004_auto_20160727_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smevlog',
            name='consumer_type',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, 'Юридическое лицо'), (1, 'Физическое лицо')],
                default=1,
                null=True,
                verbose_name='Потребитель сервиса',
            ),
        ),
        migrations.AlterField(
            model_name='smevlog',
            name='result',
            field=models.TextField(blank=True, null=True, verbose_name='Результат'),
        ),
        migrations.AlterField(
            model_name='smevlog',
            name='target_name',
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name='Наименование электронного сервиса'
            ),
        ),
        migrations.AlterField(
            model_name='smevlog',
            name='time',
            field=models.DateTimeField(db_index=True, default=datetime.datetime.now, verbose_name='Время СМЭВ запроса'),
        ),
        migrations.AlterField(
            model_name='smevprovider',
            name='source',
            field=models.PositiveSmallIntegerField(
                choices=[(0, 'ЕПГУ'), (1, 'РПГУ'), (2, 'Межведомственное взаимодействие')],
                verbose_name='Источник взаимодействия',
            ),
        ),
    ]
