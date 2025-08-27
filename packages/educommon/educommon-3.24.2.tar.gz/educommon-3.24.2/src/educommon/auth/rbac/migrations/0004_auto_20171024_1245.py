import django.db.models.deletion
import django.db.models.manager
import m3_django_compat
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('rbac', '0003_permission_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleUserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'role',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='+',
                        to='rbac.Role',
                        verbose_name='Роль',
                    ),
                ),
                (
                    'user_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='+',
                        to='contenttypes.ContentType',
                        verbose_name='Тип пользователя',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Тип пользователя роли',
                'verbose_name_plural': 'Типы пользователей ролей',
            },
        ),
        migrations.AlterModelManagers(
            name='userrole',
            managers=[
                ('objects', m3_django_compat.Manager()),
                ('actual_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='user_types',
            field=models.ManyToManyField(
                related_name='_role_user_types_+',
                through='rbac.RoleUserType',
                to='contenttypes.ContentType',
                verbose_name='Может быть назначена',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='roleusertype',
            unique_together=set([('role', 'user_type')]),
        ),
    ]
