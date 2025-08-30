import json

from m3.actions import (
    context,
)

from educommon.rest.controllers import (
    ObservableController,
)
from educommon.rest.misc import (
    get_request_params,
)


class RestDeclarativeActionContext(ObservableController.VerboseDeclarativeContext):
    def build(self, request, rules):
        """Выполняет заполнение собственных атрибутов согласно переданному запросу, исходя из списка правил.

        :param request:запрос, на основе которого производится
            заполнение контекста
        :type reques: django.http.Request

        :param rules: правила извлечения контекста из запроса
        :type rules: список m3_core.actions.context.ActionContextDeclaration

        :raise: TypeError, ContextBuildingError, CriticalContextBuildingError
        """
        assert self.matches(rules), 'rules must be a dict or pair!'
        # определяем режим, если правилла описаны парой
        if isinstance(rules, tuple):
            # режим
            mode = get_request_params(request).get(rules[0])
            try:
                # правила для конкретного режима
                rules = rules[1][mode]
            except KeyError:
                raise TypeError('Неизвестный режим: %r=%r' % (rules[0], mode))
            # ну и запоминаем режим
            self._mode = mode

        # аккумуляторы ошибок, связанных с нехваткой и неправильным форматом
        requiremets = []
        errors = []
        only_noncritical = True

        for key, parser_data in rules.items():
            parser = parser_data['type']
            if not callable(parser):
                try:
                    parser = self._parsers[parser]
                except KeyError:
                    raise TypeError(f'Неизвестный парсер контекста: "{parser}"')

            add_error_to = None
            try:
                val = None
                if request.method == 'GET':
                    val = get_request_params(request).get(key)
                else:
                    try:
                        json_params = json.loads(request.body)
                        val = json_params.get(str(key))
                    except ValueError:
                        pass

                if val is None:
                    if 'default' in parser_data:
                        val = parser_data['default']
                    else:
                        # параметр обязателен, но не присутствует в запросе
                        add_error_to = requiremets
                else:
                    val = parser(val)
            except (ValueError, TypeError, KeyError, IndexError):
                # ошибка преобразования
                add_error_to = errors

            if add_error_to is not None:
                add_error_to.append(parser_data.get('verbose_name', key))
                # ошибка критична, если хотя бы один из параметров
                # не имеет verbose_name
                only_noncritical = only_noncritical and ('verbose_name' in parser_data)
                continue

            setattr(self, key, val)

        if requiremets or errors:
            if only_noncritical:
                raise context.ContextBuildingError(requiremets, errors)
            else:
                raise context.CriticalContextBuildingError(requiremets, errors)
