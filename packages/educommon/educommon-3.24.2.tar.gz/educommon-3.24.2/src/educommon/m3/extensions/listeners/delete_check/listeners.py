from collections import (
    defaultdict,
)

from django.dispatch import (
    Signal,
)
from m3.actions import (
    OperationResult,
)

from objectpack.actions import (
    ObjectDeleteAction,
)
from objectpack.models import (
    ModelProxy,
)

from educommon.m3.extensions.listeners.delete_check.mixins import (
    CascadeDeleteMixin,
)
from educommon.m3.extensions.listeners.delete_check.ui import (
    CancelConfirmWindow,
)
from educommon.utils.db import (
    get_non_block_relations,
    get_related_instances_proxy,
)


class DeleteCheck:
    """Проверяет объекты перед удалением на наличие зависимостей.

    В случае, если в системе есть объекты, зависимые от удаляемого объекта и
    не отмеченные для каскадного удаления через cascade_delete_objects, то
    отменяет удаление и выводит окно с предупреждением и списком зависимых
    объектов.
    Если в системе есть только зависимые объекты, помеченные
    cascade_delete_objects, то выводится сообщение с кнопкой Удалить, для
    удаления и связанных объектов.

    Для добавления объектов, которые *неявно* зависят от удаляемых, необходимо
    подписаться на сигнал ``DeleteCheck.collect_implicit``.
    """

    #: Сигнал отправляемый после сборки зависимых объектов
    #:
    #: :param objects_to_delete: Удаляемые объекты.
    #: :type objects_to_delete: django.db.models.query.QuerySet
    #: :param related_objects: Словарь, сопоставляющий удаляемые
    #:     и зависимые объекты.
    #: :type related_objects: collections.defaultdict
    collect_implicit = Signal()

    def _get_message(self, objects):
        """Возвращает сообщение в правильном склонении."""
        return ('объекта' if len(objects) == 1 else 'объектов', 'него' if len(objects) == 1 else 'них')

    def _setup_window(self, objects, related_objects, blocked=True, grid_id=None):
        """Возвращает окно с сообщением о связанных объектах.

        :param objects: удаляемые объекты
        :param related_objects: связанные объекты
        :param bool blocked: режим показа окна блокирующее/не блокирующее
        :param str grid_id: id грида, из которого происходит удаление
        :return: CancelConfirmWindow
        """
        if blocked:
            title = 'Удаление {} невозможно, т.к. на {} есть ссылки:'.format(*self._get_message(objects))
        else:
            title = 'При удалении {} будут удалены следующие связи:'.format(self._get_message(objects)[0])

        win = CancelConfirmWindow()
        win.set_params(
            dict(
                title=title,
                objects=objects,
                related_objects=related_objects,
                blocked=blocked,
                grid_id=grid_id,
            )
        )
        win.pack_action_url = self.action.get_absolute_url()

        return win

    def _get_objects(self, context):
        """Получает удаляемые объекты из контекста."""
        model = self.action.parent.model
        if issubclass(model, ModelProxy):
            model = model.model

        object_ids = getattr(context, self.action.parent.id_param_name)

        return model.objects.filter(pk__in=object_ids)

    def before(self, request, context):
        """Обрабатывает удаление с проверкой на наличие связанных объектов.

        Если удаление невозможно или требует подтверждения, формирует окно
        с предупреждением или подтверждением.
        """
        if not isinstance(self.action, ObjectDeleteAction):
            return

        # Удаляемые объекты
        objects = self._get_objects(context)

        if not objects:
            return

        if hasattr(self.action.parent, 'skip_field'):

            def skip_function(field):
                return self.action.parent.skip_field(field) or CascadeDeleteMixin.skip_field(field)
        else:
            skip_function = CascadeDeleteMixin.skip_field

        # Прерываем проверки, если пользователь подтвердил удаление связей
        if getattr(context, 'delete_check_confirmed', False):
            return

        # Объекты, зависящие от удаляемых
        related_objects = defaultdict(list)

        # Проверка блокирующих удаление связей
        for obj in objects:
            for related_obj in get_related_instances_proxy(obj, skip_function):
                key = '.'.join(
                    (
                        related_obj._meta.app_label,
                        related_obj._meta.object_name,
                    )
                )
                related_objects[key].append(related_obj)
        self.collect_implicit.send(self.action.parent.model, objects_to_delete=objects, related_objects=related_objects)

        if related_objects:
            win = self._setup_window(objects, related_objects)
        else:
            # Проверка не блокирующих удаление связей
            for obj in objects:
                related_objects.update(get_non_block_relations(obj))
            win = self._setup_window(objects, related_objects, blocked=False, grid_id=getattr(context, 'grid_id', None))

        if not related_objects:
            return

        win.action_context = context
        return OperationResult(
            success=False,
            code=win.get_script(),
        )
