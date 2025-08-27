from inspect import (
    isclass,
)

from django.template.context import (
    RequestContext,
)
from m3_django_compat import (
    get_template,
)


class HtmlPageComponent:
    """Компонент HTML-страницы.

    Компонент имеет свой шаблон Django, умеет компилировать себя в HTML-код.
    Использование компонент для формирования элементов HTML-страниц позволяет
    работать с элементами страниц как с объектами.
    """

    id = None
    """Идентификатор элемента."""

    template_path = None
    """Путь к шаблону Django, содержащему HTML-код элемента панели.

    В данном шаблоне будет доступен экземпляр (объект) данного компонента в
    переменной ``element``.

    .. note:
       При необходимости добавления других переменных в конекст шаблона
       переопределяйте метод :py:meth:`_get_template_context`
    """

    def __init__(self, request, context, **params):
        """Инициализация элемента панели.

        :param request: HTTP-запрос.
        :type request: django.http.HttpRequest

        :param context: Контекст операции.
        :type context: m3.action.context.ActionContext
        """
        self.request = request
        self.context = context
        self.params = params

    def _get_template(self):
        """Возвращает шаблон элемента панели.

        :rtype: django.template.base.Template
        """
        assert self.template_path is not None, 'Не указан путь к шаблону.'

        return get_template(self.template_path)

    def _get_template_context(self):
        """Возвращает контекст шаблона.

        В параметре ``element`` будет доступен сам элемент.

        :rtype: django.template.context.RequestContext
        """
        result = RequestContext(self.request)

        result['element'] = self

        return result

    def render(self):
        """Компиляция шаблона элемента панели.

        :rtype: str
        """
        template = self._get_template()
        template_context = self._get_template_context()

        return template.render(template_context)


class Container(HtmlPageComponent):
    """Контейнер компонент HTML-страницы.

    Логически состоит из вложенных элементов и других контейнеров.
    """

    items = []
    """Элементы контейнера.

    Может содержать как экземпляры компонент, так и классы. Если при компиляции
    контейнера в списке элементов окажется класс, то перед компиляцией этого
    элемента будет создан его экземпляр.
    """

    def __init__(self, request, context, **params):
        super(Container, self).__init__(request, context, **params)

        items = []
        for item in self.items:
            if isclass(item):
                items.append(item(self.request, self.context, **self.params))
            else:
                items.append(item)
        self.items = items

    def _get_template_context(self):
        """Возвращает контекст шаблона.

        Дополняет конекст шаблона переменной ``items``, содержащей
        упорядоченный список вложенных элементов контейнера.

        :rtype: django.template.context.RequestContext
        """
        result = super(Container, self)._get_template_context()

        result['items'] = self.items

        return result

    def get_item_by_id(self, item_id):
        """Возвращает первый элемент с идентификатором ``item_id``."""
        for item in self.items:
            if item.id == item_id:
                return item

    def remove_item_by_id(self, item_id):
        """Удаляет из списка элементов контейнера элемент с указанным id."""
        self.items[:] = [item for item in self.items if item.id == item_id]
