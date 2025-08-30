from django.conf import (
    settings,
)
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ResetPasswords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'code',
                    models.CharField(
                        unique=True,
                        max_length=32,
                        verbose_name='\u041a\u043e\u0434 \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f',
                    ),
                ),
                (
                    'date',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0431\u0440\u043e\u0441\u0430 \u043f\u0430\u0440\u043e\u043b\u044f',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                'verbose_name': '\u0421\u0431\u0440\u043e\u0448\u0435\u043d\u043d\u044b\u0439 \u043f\u0430\u0440\u043e\u043b\u044c',
                'verbose_name_plural': '\u0421\u0431\u0440\u043e\u0448\u0435\u043d\u043d\u044b\u0435 \u043f\u0430\u0440\u043e\u043b\u0438',
            },
            bases=(models.Model,),
        ),
    ]
