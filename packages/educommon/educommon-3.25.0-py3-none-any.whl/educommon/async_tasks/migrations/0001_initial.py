from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncTaskMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'description',
                    models.CharField(
                        max_length=400,
                        null=True,
                        verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u0447\u0438',
                        blank=True,
                    ),
                ),
                (
                    'location',
                    models.CharField(
                        max_length=400, verbose_name='\u041f\u0443\u0442\u044c \u043a\u043b\u0430\u0441\u0441\u0430'
                    ),
                ),
            ],
            options={
                'verbose_name': '\u0414\u0430\u043d\u043d\u044b\u0435 \u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u043e\u0439 \u0437\u0430\u0434\u0430\u0447\u0438',
                'verbose_name_plural': '\u0414\u0430\u043d\u043d\u044b\u0435 \u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u0447',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AsyncTaskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u0422\u0438\u043f')),
            ],
            options={
                'verbose_name': '\u0422\u0438\u043f \u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u0447',
                'verbose_name_plural': '\u0422\u0438\u043f\u044b \u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u0447',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RunningTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('task_id', models.CharField(max_length=36, verbose_name='ID \u0437\u0430\u0434\u0430\u0447\u0438')),
                (
                    'status',
                    models.SmallIntegerField(
                        default=1,
                        db_index=True,
                        verbose_name='\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u0447\u0438',
                        choices=[
                            (1, '\u041d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043d\u043e'),
                            (2, '\u0412 \u043e\u0447\u0435\u0440\u0435\u0434\u0438'),
                            (3, '\u0412\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442\u0441\u044f'),
                            (
                                4,
                                '\u0423\u0441\u043f\u0435\u0448\u043d\u043e \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0430',
                            ),
                            (5, '\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0430'),
                            (6, '\u041e\u0448\u0438\u0431\u043a\u0430'),
                            (7, '\u041f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u043a'),
                            (8, '\u0418\u0433\u043d\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0430'),
                            (9, '\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u0430'),
                        ],
                    ),
                ),
                (
                    'queued_on',
                    models.DateTimeField(
                        null=True,
                        verbose_name='\u0421\u0442\u0430\u0440\u0442 \u0437\u0430\u0434\u0430\u0447\u0438',
                        db_index=True,
                    ),
                ),
                (
                    'content_type',
                    models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
                ),
                (
                    'task_meta',
                    models.ForeignKey(
                        verbose_name='\u0414\u0430\u043d\u043d\u044b\u0435 \u0437\u0430\u0434\u0430\u0447\u0438',
                        blank=True,
                        to='async.AsyncTaskMeta',
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
                (
                    'task_type',
                    models.ForeignKey(
                        default=1,
                        verbose_name='\u0422\u0438\u043f \u0437\u0430\u0434\u0430\u0447\u0438',
                        to='async.AsyncTaskType',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                'verbose_name': '\u0410\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430',
                'verbose_name_plural': '\u0410\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u044b\u0435 \u0437\u0430\u0434\u0430\u0447\u0438',
            },
            bases=(models.Model,),
        ),
    ]
