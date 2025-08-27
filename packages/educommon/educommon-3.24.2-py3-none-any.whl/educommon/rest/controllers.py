import json
import re

from m3 import (
    actions as m3_actions,
)

from objectpack.observer.base import (
    ObservableController,
    _warn,
)

from educommon.rest.context import (
    RestDeclarativeActionContext,
)
from educommon.rest.misc import (
    get_request_params,
)


class RestObservableController(ObservableController):
    """Контроллер для REST."""

    api = None
    object_id_regex = re.compile(r'/(?P<id>\d+)$')

    class VerboseDeclarativeContext(RestDeclarativeActionContext):
        def build(self, request, rules):
            self.__declared = list(rules.keys()) + self.__internal_attrs

            try:
                RestDeclarativeActionContext.build(self, request, rules)
            except m3_actions.CriticalContextBuildingError as e:
                if self.__debug:
                    raise
                else:
                    _warn(f'{e!r}, url="{request.path_info}"')

            for k, v in list(get_request_params(request).items()):
                if not hasattr(self, k):
                    setattr(self, k, v)

            # Если метод запроса не GET соберем контекст из body
            if request.method != 'GET':
                try:
                    json_params = json.loads(request.body)
                    for k, v in json_params.items():
                        if not hasattr(self, k):
                            setattr(self, k, v)
                except ValueError:
                    pass

    def __init__(self, observer, *args, **kwargs):
        super().__init__(observer, *args, **kwargs)

        self.api = {}

    def append_pack(self, pack):
        super().append_pack(pack)

        self.api[pack.__class__.__name__] = pack.get_absolute_url()

    def process_request(self, request):
        """Обработка входящего запроса *request* от клиента.

        Экшен определяется исходя из метода запроса.
        """

        # Если запрос вида url/id
        match = self.object_id_regex.search(request.path)
        request.object_id = int(match.groupdict().get('id'), 0) if match else 0

        path = self.object_id_regex.sub('', request.path)
        request.path = '{}/{}'.format(path.rstrip('/'), request.method.lower())

        return super().process_request(request)
