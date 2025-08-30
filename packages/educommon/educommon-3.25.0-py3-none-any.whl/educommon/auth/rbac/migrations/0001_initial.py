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
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'name',
                    models.CharField(unique=True, max_length=100, verbose_name='\u0418\u043c\u044f', db_index=True),
                ),
                (
                    'title',
                    models.CharField(
                        max_length=200,
                        null=True,
                        verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435',
                        blank=True,
                    ),
                ),
                (
                    'description',
                    models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True),
                ),
            ],
            options={
                'verbose_name': '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u044f',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'name',
                    models.CharField(
                        unique=True,
                        max_length=300,
                        verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435',
                        db_index=True,
                    ),
                ),
                (
                    'description',
                    models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True),
                ),
                (
                    'can_be_assigned',
                    models.BooleanField(
                        default=True,
                        verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0431\u044b\u0442\u044c \u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044e',
                    ),
                ),
            ],
            options={
                'verbose_name': '\u0420\u043e\u043b\u044c',
                'verbose_name_plural': '\u0420\u043e\u043b\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleParent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent', models.ForeignKey(related_name='+', to='rbac.Role', on_delete=models.CASCADE)),
                ('role', models.ForeignKey(related_name='+', to='rbac.Role', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': '\u0412\u043b\u043e\u0436\u0435\u043d\u043d\u0430\u044f \u0440\u043e\u043b\u044c',
                'verbose_name_plural': '\u0412\u043b\u043e\u0436\u0435\u043d\u043d\u044b\u0435 \u0440\u043e\u043b\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'permission',
                    models.ForeignKey(
                        verbose_name='\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435',
                        to='rbac.Permission',
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'role',
                    models.ForeignKey(
                        verbose_name='\u0420\u043e\u043b\u044c', to='rbac.Role', on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                'db_table': 'rbac_role_permissions',
                'verbose_name': '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u0440\u043e\u043b\u0438',
                'verbose_name_plural': '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u044f \u0440\u043e\u043b\u0435\u0439',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                (
                    'date_from',
                    models.DateField(
                        null=True,
                        verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b\u0430',
                        blank=True,
                    ),
                ),
                (
                    'date_to',
                    models.DateField(
                        null=True,
                        verbose_name='\u041a\u043e\u043d\u0435\u0446 \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b\u0430',
                        blank=True,
                    ),
                ),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
                (
                    'role',
                    models.ForeignKey(
                        verbose_name='\u0420\u043e\u043b\u044c', to='rbac.Role', on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                'verbose_name': '\u0420\u043e\u043b\u044c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
                'verbose_name_plural': '\u0420\u043e\u043b\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='rolepermission',
            unique_together=set([('role', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='roleparent',
            unique_together=set([('parent', 'role')]),
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(related_name='roles', through='rbac.RolePermission', to='rbac.Permission'),
            preserve_default=True,
        ),
    ]
