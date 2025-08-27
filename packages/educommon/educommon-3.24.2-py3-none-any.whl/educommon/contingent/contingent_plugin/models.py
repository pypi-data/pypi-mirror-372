from django import (
    VERSION,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db import (
    models,
)
from m3_django_compat.models import (
    GenericForeignKey,
)


class ContingentModelChanged(models.Model):
    """Данные об измененных моделях."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        unique_together = ('content_type', 'object_id')


class ContingentModelDeleted(models.Model):
    """Данные об удалённых объектах моделей."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # В этом поле хранятся рассчитанные данные для выгрузки в КО
    # для полей удалаяемых объектов моделей в json-формате
    data = models.TextField('Данные об удалённом объекте')

    class Meta:
        unique_together = ('content_type', 'object_id')


# поскольку нам надо убедиться что миграция contingent_plugin должна
# быть пройдена раньше чем остальные, изменяем план миграций,
# но обязательно надо учесть зависимость самой миграции от contenttypes
if VERSION >= (1, 10):
    from django.db.models.signals import (
        pre_migrate,
    )
    from django.dispatch.dispatcher import (
        receiver,
    )

    @receiver(pre_migrate)
    def correct_migration_plan(plan, **kwargs):
        """Изменяет план выполения миграций"""
        value = False
        index = 0
        for ind, migration_tuple in enumerate(plan):
            if (migration_tuple[0].name == '0001_initial') and (migration_tuple[0].app_label == 'contingent_plugin'):
                value = migration_tuple

            if (migration_tuple[0].name == '0002_remove_content_type_name') and (
                migration_tuple[0].app_label == 'contenttypes'
            ):
                index = ind
        if value:
            plan.remove(value)
            if index:
                plan.insert(index + 1, value)
            else:
                plan.insert(0, value)
