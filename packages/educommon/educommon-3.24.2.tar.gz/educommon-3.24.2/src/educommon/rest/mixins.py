from m3.actions.results import (
    PreJsonResult,
)

from objectpack.actions import (
    BaseAction,
)


class BaseRestAction(BaseAction):
    """Базовый экшен для экшенов REST."""


class ListModelMixin:
    """Примесь для REST паков, обработка запросов метода GET.

    Получения списка объектов.
    """

    def __init__(self):
        super().__init__()

        if not hasattr(self, 'get_action'):
            self.get_action = GetAction()
            self.actions.append(self.get_action)

    def list(self, request, context):
        """Метод отвечает за обработку запроса методом GET.

        Получение списка объектов.
        """
        raise NotImplementedError


class RetrieveModelMixin:
    """Примесь для REST паков, обработка запросов метода GET.

    Получение конкретно объекта по context.id.
    """

    def __init__(self):
        super().__init__()

        if not hasattr(self, 'get_action'):
            self.get_action = GetAction()
            self.actions.append(self.get_action)

    def retrieve(self, request, context):
        """Метод отвечает за обработку запроса методом GET.

        Получение конкретного объекта по context.id.
        """
        raise NotImplementedError


class GetAction(BaseRestAction):
    """Экшен обработки запроса методом GET.

    Делегирует обработку методам пака.
    """

    url = '/get'

    def run(self, request, context):
        if not request.object_id and hasattr(self.parent, 'list'):
            result = self.parent.list(request, context)
        else:
            result = self.parent.retrieve(request, context)
        return result


class CreateModelMixin:
    """Примесь для REST паков, обработка запросов методом POST."""

    def __init__(self):
        super().__init__()

        self.post_action = PostAction()
        self.actions.append(self.post_action)

    def create(self, request, context):
        """Метод отвечает за создание объекта."""
        raise NotImplementedError


class PostAction(BaseRestAction):
    """Экшен обработки запроса методом POST.

    Делегирует обработку методам пака.
    """

    url = '/post'

    def run(self, request, context):
        result = self.parent.create(request, context)
        return PreJsonResult(result)


class UpdateModelMixin:
    """Примесь для REST паков, обработка запросов методом PUT и PATCH."""

    def __init__(self):
        super().__init__()

        self.put_action = PutAction()
        self.patch_action = PatchAction()
        self.actions.extend([self.put_action, self.patch_action])

    def update(self, request, context):
        """Метод отвечает за изменение объекта."""
        raise NotImplementedError


class PutAction(BaseRestAction):
    """Экшен обработки запроса методом PUT.

    Делегирует обработку методам пака.
    """

    url = '/put'

    def run(self, request, context):
        result = self.parent.update(request, context)
        return PreJsonResult(result)


class PatchAction(BaseRestAction):
    """Экшен обработки запроса методом PATCH.

    Делегирует обработку методам пака.
    """

    url = '/patch'

    def run(self, request, context):
        result = self.parent.update(request, context)
        return PreJsonResult(result)


class DestroyModelMixin:
    """Примесь для REST паков, обработка запросов методом DELETE."""

    def __init__(self):
        super().__init__()

        self.delete_action = DeleteAction()
        self.actions.append(self.delete_action)

    def destroy(self, request, context):
        """Метод отвечает за удаление объекта."""
        raise NotImplementedError


class DeleteAction(BaseRestAction):
    """Экшен обработки запроса методом PATCH.

    Делегирует обработку методам пака.
    """

    url = '/delete'

    def run(self, request, context):
        result = self.parent.destroy(request, context)
        return PreJsonResult(result)
