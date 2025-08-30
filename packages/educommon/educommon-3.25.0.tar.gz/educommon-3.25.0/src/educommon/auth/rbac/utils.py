"""Вспомогательные средства для работы с подсистемой RBAC."""

import operator
from inspect import (
    getfullargspec,
)

from m3.actions import (
    Action,
    ActionPack,
)

from educommon.m3 import (
    get_pack,
)


def _resolve_packs_or_actions(packs_or_actions):
    """Возвращает список из паков и экшенов, заданных классами и строками."""

    def resolve(pack_or_action):
        if isinstance(pack_or_action, tuple):
            pack, action = pack_or_action
            pack = get_pack(pack)
            result = getattr(pack, action)
        else:
            result = get_pack(pack_or_action)
        return result

    result = [resolve(pack_or_action) for pack_or_action in packs_or_actions]

    return result


def _rule_filter(rule_handler, packs_or_actions, operator_):
    """Возвращает обработчик правила, "обернутый" в фильтрующую функцию."""

    def action_in_list(action):
        for pack_or_action in _resolve_packs_or_actions(packs_or_actions):
            if (isinstance(pack_or_action, Action) and action.__class__ is pack_or_action.__class__) or (
                isinstance(pack_or_action, ActionPack) and action.parent is pack_or_action
            ):
                return True

        return False

    def wrapper(action, request, user):
        if operator_(action_in_list(action)):
            return rule_handler(action, request, user)
        else:
            return True

    return wrapper


def only_for(rule_handler, *packs_or_actions):
    """Выполняет правило только для указанных паков и экшенов.

    Экшены задаются в виде кортежа из двух элементов: первый элемент определяет
    пак (см. educommon.m3.get_pack()), а второй - имя атрибута этого пака, в
    котором содержится экшен. Иначе аргумент будет определять пак целиком.

    :param rule_handler: Обработчик правила.

    :rtype: callable
    """
    return _rule_filter(rule_handler, packs_or_actions, operator.truth)


def except_for(rule_handler, *packs_or_actions):
    """Выполняет правило для всех паков и экшенов, кроме указанных.

    Экшены задаются в виде кортежа из двух элементов: первый элемент определяет
    пак (см. educommon.m3.get_pack()), а второй - имя атрибута этого пака, в
    котором содержится экшен. Иначе аргумент будет определять пак целиком.

    :param rule_handler: Обработчик правила.

    :rtype: callable
    """
    return _rule_filter(rule_handler, packs_or_actions, operator.not_)


def invert_rule(rule_handler):
    """Применяет к обработчику правил RBAC операцию "логическое НЕ".

    .. code-block:: python
       :caption: ``permissions.py``

       rules = {
           PERM_SOME_ACTION: invert_rule(user_is_employee),
       }

    :rtype: callable
    """

    def wrapper(action, request, user, *args, **kwargs):
        return not rule_handler(action, request, user, *args, **kwargs)

    return wrapper


def any_rules(*rule_handlers):
    """Объединяет обработчики правил RBAC операцией "логическое ИЛИ".

    В результате объединения доступ будет разрешен если хотя бы один из
    обработчиков разрешит доступ.

    .. code-block:: python
       :caption: ``permissions.py``

       rules = {
           PERM_SOME_ACTION: any_rules(user_is_employee, user_is_sysadmin),
       }

    :rtype: callable
    """

    def wrapper(action, request, user, *args, **kwargs):
        for rule_handler in rule_handlers:
            if rule_handler(action, request, user, *args, **kwargs):
                return True
        return False

    return wrapper


def all_rules(*rule_handlers):
    """Объединяет обработчики правил RBAC операцией "логическое И".

    В результате объединения доступ будет разрешен только если каждый из
    обработчиков разрешит доступ.

    Например, разрешить доступ к какому-либо действию над объектом только для
    сотрудников текущего учреждения можно объединив два правила:

    .. code-block:: python
       :caption: ``permissions.py``

       rules = {
           PERM_SOME_ACTION: all_rules(user_is_employee, user_in_current_unit),
       }

    :rtype: callable
    """

    def wrapper(action, request, user, *args, **kwargs):
        for rule_handler in rule_handlers:
            if not rule_handler(action, request, user, *args, **kwargs):
                return False
        return True

    return wrapper


def get_rbac_rule_data(request, action):
    """Возвращает данные для обработчика правила RBAC.

    Если у :arg:`action` есть метод ``get_rbac_rule_data()``, то вызывает его.
    Иначе вызывает такой метод у набора действий (ActionPack), в который входит
    действие :arg:`action`.

    У метода ``get_rbac_rule_data()`` может быть один аргумент ``request``,
    либо два аргумента: ``request`` и ``action``.

    Результат выполнения метода ``get_rbac_rule_data()`` кешируется в атрибуте
    ``_rbac_rule_data`` объекта :arg:`request`.Это актуально, когда обработчики
    правил комбинируются с помощью функций :func:`any_rules` и
    :func:`all_rules`.

    :param request: HTTP-запрос.
    :type request: django.http.request.HttpRequest

    :param action: Обработчик запроса.
    :type action: m3.actions.Action
    """
    if not hasattr(request, '_rbac_rule_data'):
        if hasattr(action, 'get_rbac_rule_data'):
            method = action.get_rbac_rule_data
        else:
            method = action.parent.get_rbac_rule_data

        assert method is None or callable(method), method

        if method is None:
            data = None
        else:
            if 'action' in getfullargspec(method).args:
                data = method(request=request, action=action)
            else:
                data = method(request=request)

        setattr(request, '_rbac_rule_data', data)

    return getattr(request, '_rbac_rule_data')


def get_permission_full_title(permission_name):
    """Возвращает полное наименование разрешения по его имени.

    Полное наименование состоит их наименований раздела, группы и
    разрешения.
    """
    from educommon.auth.rbac.manager import (
        rbac,
    )

    _, permission_title = rbac.permissions_by_name[permission_name]
    group_name, group_title = rbac.get_group_params(permission_name)
    partition_title = rbac.get_partition_title(group_name)

    return ' - '.join((partition_title, group_title, permission_title))
