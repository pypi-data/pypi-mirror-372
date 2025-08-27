from django.template.loader import (
    render_to_string,
)
from m3_ext.ui import (
    all_components as ext,
)
from m3_ext.ui.containers.forms import (
    ExtPanel,
)

from objectpack.ui import (
    BaseWindow,
)

from educommon.django.db.model_view import (
    registries,
)
from educommon.utils.ui import (
    local_template,
)


class RelatedObjectsWindow(BaseWindow):
    """Окно с информацией о зависимых объектах.

    Используется для отображения информации об объектах, зависящих от
    удаляемых.

    В параметрах окна должен быть указан список удаляемых объектов и список
    объектов, зависимых от удаляемых.
    """

    #: Шаблон HTML-страницы с представлениями моделей.
    html_template = local_template('related-objects-window.html')

    @property
    def model_view_registry(self):
        """Реестр представлений моделей."""
        return registries['related_objects']

    def _init_components(self):
        super()._init_components()

        self.panel = ExtPanel(
            auto_scroll=True,
            cls='related-objects',
        )
        self.items.append(self.panel)

    def _do_layout(self):
        super()._do_layout()

        self.width = 800
        self.height = 600

        self.layout = 'fit'

    def _get_html(self, title, objects, related_objects):
        views = tuple(
            self.model_view_registry.get(model).get_view(objects) for model, objects in related_objects.items()
        )

        return render_to_string(
            template_name=self.html_template,
            context=dict(
                title=title,
                views=views,
            ),
        )

    def set_params(self, params):
        super().set_params(params)

        self.title = 'Внимание!'

        self.panel.html = self._get_html(
            params.get('title'),
            params['objects'],
            params['related_objects'],
        )


class CancelConfirmWindow(RelatedObjectsWindow):
    """Окно подтверждения удаления объекта и связанных с ним объектов.

    Содержит информацию об объектах, которые будут удалены при удалении
    объекта.
    """

    def _init_components(self):
        super()._init_components()

        self.button__confirm = ext.ExtButton(
            text='Удалить',
            handler='confirmDelete',
        )
        self.button__cancel = ext.ExtButton(
            text='Отмена',
            handler='closeWindow',
        )

    def _do_layout(self):
        super()._do_layout()

        self.buttons.extend(
            (
                self.button__confirm,
                self.button__cancel,
            )
        )

    def set_params(self, params):
        super().set_params(params)

        self.template_globals = local_template('cancel-confirm-window.js')

        self.blocked = params.get('blocked', True)
        if self.blocked:
            self.button__confirm.hidden = True
            self.button__cancel.hidden = True

        self.grid_id = params.get('grid_id')
