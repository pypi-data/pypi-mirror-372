import datetime

from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SmevLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'service_address',
                    models.CharField(blank=True, max_length=250, null=True, verbose_name='Адрес сервиса'),
                ),
                ('method_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Код метода')),
                (
                    'method_verbose_name',
                    models.CharField(blank=True, max_length=250, null=True, verbose_name='Наименование метода'),
                ),
                ('request', models.TextField(blank=True, null=True, verbose_name='SOAP запрос')),
                ('response', models.TextField(blank=True, null=True, verbose_name='SOAP ответ')),
                ('error', models.TextField(blank=True, null=True, verbose_name='Возникшая ошибка')),
                ('time', models.DateTimeField(default=datetime.datetime.now, verbose_name='Время СМЭВ запроса')),
                (
                    'interaction_type',
                    models.PositiveSmallIntegerField(
                        choices=[(0, 'СМЭВ'), (1, 'Не СМЭВ')], default=0, verbose_name='Вид взаимодействия'
                    ),
                ),
                (
                    'direction',
                    models.SmallIntegerField(
                        choices=[(1, 'Входящие запросы'), (0, 'Исходящие запросы')], verbose_name='Направление запроса'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Лог запросов СМЭВ',
                'verbose_name_plural': 'Логи запросов СМЭВ',
            },
        ),
        migrations.CreateModel(
            name='SmevProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mnemonics', models.CharField(max_length=100, verbose_name='Мнемоника')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес СМЭВ')),
                ('source', models.CharField(max_length=100, verbose_name='Источник взаимодействия')),
                (
                    'entity',
                    models.CharField(blank=True, max_length=255, null=True, verbose_name='Наименование юр.лица'),
                ),
            ],
            options={
                'verbose_name': 'Поставщик СМЭВ',
                'verbose_name_plural': 'Поставщики СМЭВ',
            },
        ),
    ]
