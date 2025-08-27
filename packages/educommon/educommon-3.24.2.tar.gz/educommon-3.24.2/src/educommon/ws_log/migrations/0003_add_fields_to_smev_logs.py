from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('ws_log', '0002_auto_20160628_1334'),
    ]

    operations = [
        # Добавляет новые поля
        migrations.AddField(
            model_name='smevlog',
            name='consumer_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Наименование потребителя'),
        ),
        migrations.AddField(
            model_name='smevlog',
            name='consumer_type',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, 'Юридическое лицо'), (1, 'Физическое лицо')],
                default=1,
                null=True,
                verbose_name='Потребитель сервиса (физ.лицо, юр.лицо)',
            ),
        ),
        migrations.AddField(
            model_name='smevlog',
            name='source',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, 'ЕПГУ'), (1, 'РПГУ'), (2, 'Межведомственное взаимодействие')],
                default=None,
                null=True,
                verbose_name='Источник взаимодействия',
            ),
        ),
        migrations.AddField(
            model_name='smevlog',
            name='target_name',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='Наименование электронного сервиса Системы, к которому было обращение',
            ),
        ),
        # Переименовывает поле error в result.
        migrations.RenameField('SmevLog', 'error', 'result'),
    ]
