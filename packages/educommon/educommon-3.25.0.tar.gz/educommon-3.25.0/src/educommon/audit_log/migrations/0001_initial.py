from django.contrib.postgres.fields.hstore import (
    HStoreField,
)
from django.db import (
    migrations,
    models,
)

from educommon.django.db.migration.operations import (
    CreateSchema,
)


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        CreateSchema('audit', aliases=('default',)),
        migrations.CreateModel(
            name='PostgreSQLError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'user_id',
                    models.IntegerField(
                        null=True,
                        verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                    ),
                ),
                ('ip', models.GenericIPAddressField(null=True, verbose_name='IP \u0430\u0434\u0440\u0435\u0441')),
                (
                    'time',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430, \u0432\u0440\u0435\u043c\u044f'
                    ),
                ),
                (
                    'level',
                    models.CharField(
                        max_length=50,
                        verbose_name='\u0423\u0440\u043e\u0432\u0435\u043d\u044c \u043e\u0448\u0438\u0431\u043a\u0438',
                    ),
                ),
                (
                    'text',
                    models.TextField(
                        verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043e\u0448\u0438\u0431\u043a\u0438'
                    ),
                ),
            ],
            options={
                'db_table': 'audit"."postgresql_errors',
                'verbose_name': '\u041e\u0448\u0438\u0431\u043a\u0430 PostgreSQL',
                'verbose_name_plural': '\u041e\u0448\u0438\u0431\u043a\u0438 PostgreSQL',
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'user_id',
                    models.IntegerField(
                        null=True,
                        verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                        db_index=True,
                    ),
                ),
                (
                    'user_type_id',
                    models.IntegerField(
                        null=True,
                        verbose_name='\u0422\u0438\u043f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
                        db_index=True,
                    ),
                ),
                ('ip', models.GenericIPAddressField(null=True, verbose_name='IP \u0430\u0434\u0440\u0435\u0441')),
                (
                    'time',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='\u0414\u0430\u0442\u0430, \u0432\u0440\u0435\u043c\u044f',
                        db_index=True,
                    ),
                ),
                (
                    'object_id',
                    models.IntegerField(
                        verbose_name='\u041e\u0431\u044a\u0435\u043a\u0442 \u043c\u043e\u0434\u0435\u043b\u0438',
                        db_index=True,
                    ),
                ),
                ('data', HStoreField(null=True, verbose_name='\u041e\u0431\u044a\u0435\u043a\u0442')),
                (
                    'changes',
                    HStoreField(null=True, verbose_name='\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f'),
                ),
                (
                    'operation',
                    models.SmallIntegerField(
                        verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435',
                        choices=[
                            (1, '\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435'),
                            (2, '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435'),
                            (3, '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435'),
                        ],
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'name',
                    models.CharField(
                        max_length=250, verbose_name='\u0418\u043c\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u044b'
                    ),
                ),
                (
                    'schema',
                    models.CharField(
                        max_length=250,
                        verbose_name='\u0421\u0445\u0435\u043c\u0430 \u0442\u0430\u0431\u043b\u0438\u0446\u044b',
                    ),
                ),
            ],
            options={
                'verbose_name': '\u041b\u043e\u0433\u0438\u0440\u0443\u0435\u043c\u0430\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u0430',
                'verbose_name_plural': '\u041b\u043e\u0433\u0438\u0440\u0443\u0435\u043c\u044b\u0435 \u0442\u0430\u0431\u043b\u0438\u0446\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together=set([('name', 'schema')]),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='table',
            field=models.ForeignKey(
                verbose_name='\u0422\u0430\u0431\u043b\u0438\u0446\u0430',
                to='audit_log.Table',
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
