from m3_django_compat import (
    get_model,
)

from educommon.utils.storage import (
    AbstractInstanceDataStorage,
)


ContingentModelDeleted = get_model('contingent_plugin', 'ContingentModelDeleted')


class ContingentDeletedInstancesDataStorage(AbstractInstanceDataStorage):
    """Класс для сохранения данных объекта модели для Контингента.

    Предполагается использование объекта этого класса вместе с классом
    PreDeletionDataSavingObserver.

    На вход ожидается реестр моделей и их обработчиков.
    Задача обработчиков - вернуть данные для удаляемого объекта модели,
    которые надо сохранить, (скорее всего строку со словарём в json формате
    с параметрами для будущей выгрузки в Контингент)
    или None, если для данного объекта ничего сохранять не надо.

    Важно учесть, что если есть сигналы pre_delete, которые удаляют связанные
    объекты для осуществления нормального удаления объекта, то они могут
    удалить важные данные. Возможно подобные удаления надо совершать в
    методе delete_some_objects_after_saving текущего класса.
    """

    @staticmethod
    def _get_instance_content_type(instance):
        """Возвращает ContentType для объекта модели.

        :param instance: Объект модели или модель

        :rtype: ContentType
        """
        ContentType = get_model('contenttypes', 'ContentType')

        return ContentType.objects.get_for_model(instance)

    def _is_instance_already_saved(self, instance, **kwargs):
        """Проверяет, сохранён ли уже объект как удалённый."""
        return ContingentModelDeleted.objects.filter(
            content_type=self._get_instance_content_type(instance),
            object_id=instance.pk,
        ).exists()

    def _save_instance_data(self, instance, **kwargs):
        """Сохраняет данные удаляемого объекта в модель ContingentModelDeleted."""
        instance_data = self._get_instance_data(instance)
        if instance_data is not None:
            ContingentModelDeleted.objects.get_or_create(
                content_type=self._get_instance_content_type(instance),
                object_id=instance.pk,
                data=instance_data,
            )

    def delete_some_objects_after_saving(self, instance, **kwargs):
        """Удаление объектов моделей, мешающих удалению объекта instance.

        Их удаление может выполняться в сигналах, но в этом случае они
        срабатывают раньше и удаляют нужные данные.
        Метод имеет те же параметры, что save.
        """
        pass

    def save(self, instance, **kwargs):
        """Сохраняет данные и вызывает удаление зависимостей после сохранения."""
        super().save(instance, **kwargs)

        self.delete_some_objects_after_saving(instance, **kwargs)
