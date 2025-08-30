import django.db.models.deletion
from django import (
    VERSION,
)
from django.conf import (
    settings,
)
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    # из-за отсутвия функционала для исправления плана миграций в Django
    # версий младше чем 1.10,здесь решается вопрос загрузки contingent_plugin
    # первым в списке выполняемых миграций. Начиная с версии 1.10 данный
    # способ не подходит ввиду ввода проверки на корректность плана миграций
    if VERSION < (1, 10):
        run_before = [(app_name.split('.')[-1], '__first__') for app_name in settings.PROJECT_APPS]

    operations = [
        migrations.CreateModel(
            name='ContingentModelChanged',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                (
                    'content_type',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contingentmodelchanged',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
