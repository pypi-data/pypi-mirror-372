import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('contingent_plugin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContingentModelDeleted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('data', models.TextField(verbose_name='Данные об удалённом объекте')),
                (
                    'content_type',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contingentmodeldeleted',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
