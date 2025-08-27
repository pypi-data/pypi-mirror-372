from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('rbac', '0002_model_modifier_metaclass_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Видимость пользователям'),
        ),
    ]
