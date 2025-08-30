from collections import (
    defaultdict,
)
from datetime import (
    date,
)
from itertools import (
    chain,
)
from logging import (
    getLogger,
)
from time import (
    time,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.core.cache import (
    cache,
)
from django.db.models.query_utils import (
    Q,
)
from django.db.models.signals import (
    post_delete,
    post_save,
)

from educommon.auth.rbac.backends.base import (
    BackendBase,
)
from educommon.auth.rbac.models import (
    Permission,
    Role,
    RoleParent,
    RolePermission,
    UserRole,
)
from educommon.utils.misc import (
    cached_property,
)


class CachingBackend(BackendBase):
    """Бэкенд, кеширующий объекты подсистемы RBAC.

    Перезагружает данные из БД в следующих случаях:

        - при инициализации подсистемы RBAC;
        - при изменении или удалении ролей;
        - при изменении прав в ролях;
        - при назначении или отзыве ролей у пользователей.
    """

    CACHE_KEY = 'RBAC_DATA_CHANGE_TIME'
    """Ключ кеша, в котором сохраняется время изменения объектов в БД."""

    # Модели, данные которых кэшируются.
    _cached_models = {Permission, Role, RoleParent, UserRole, RolePermission}

    @cached_property
    def _logger(self):
        return getLogger(__name__.rpartition('.')[0])

    def __init__(self, *args, **kwargs):
        """Инициализация бэкенда RBAC с поддержкой кэширования.

        Устанавливает параметры кэширования и подписывается на сигналы
        для обновления кэша при изменениях в связанных моделях.
        """
        super().__init__(*args, **kwargs)

        # Максимальная продолжительность кеширования объектов до их
        # перезагрузки (в секундах).
        self.CACHE_TIMEOUT = kwargs.get('CACHE_KEY', 1 * 60 * 60)

        self._loaded_at = 0  # время последней загрузки данных

        self._permissions_by_id = {}
        self._permissions_by_name = {}
        self._role_permissions = defaultdict(set)
        self._role_children = defaultdict(set)
        self._user_roles = defaultdict(set)
        # ---------------------------------------------------------------------
        # настройка сигналов

        def get_dispatch_uid(name):
            return '.'.join((self.__class__.__name__, name))

        self._manager.post_init.connect(
            self._signal_handler,
            dispatch_uid=get_dispatch_uid('post_init'),
        )
        post_save.connect(
            self._signal_handler,
            dispatch_uid=get_dispatch_uid('post_save'),
        )
        post_delete.connect(
            self._signal_handler,
            dispatch_uid=get_dispatch_uid('post_delete'),
        )

    def _signal_handler(self, sender, **kwargs):
        """Обработчик сигналов об изменениях в моделях."""
        if (
            # changed приходит только от post_init
            kwargs.get('changed', False)
            or
            # а port_save и post_delete нужно обрабатывать только для
            # кэшируемых моделей
            sender in self._cached_models
        ):
            self._set_data_change_time()

    def _get_data_change_time(self):
        """Возвращает время последнего изменения объектов RBAC в БД."""
        t = cache.get(self.CACHE_KEY)
        return float(t) if t else None

    def _set_data_change_time(self):
        """Сохраняет время последнего изменения объектов RBAC в БД."""
        t = time()
        cache.set(self.CACHE_KEY, str(t), self.CACHE_TIMEOUT)
        return t

    def _is_out_of_date(self):
        """Возвращает True, если кешированные данные устарели."""
        data_change_time = self._get_data_change_time()
        if data_change_time is None:
            # Либо, объекты еще не кэшировались, либо истекло время хранения
            # ключа, поэтому пора перезагрузить объекты RBAC.
            data_change_time = self._set_data_change_time()

        return self._loaded_at < data_change_time

    def _clear(self):
        """Очистка кеша объектов RBAC."""
        self._permissions_by_id.clear()
        self._permissions_by_name.clear()
        self._role_permissions.clear()
        self._role_children.clear()
        self._user_roles.clear()

    def _load_permissions(self):
        """Загрузка данных о разрешениях RBAC."""
        for pk, name in Permission.objects.values_list('pk', 'name'):
            self._permissions_by_id[pk] = name
            self._permissions_by_name[name] = pk

    def _load_role_hierarchy(self):
        """Загрузка данных о подчиненности ролей RBAC."""
        query = RoleParent.objects.values_list('parent', 'role')

        for parent_id, role_id in query:
            self._role_children[parent_id].add(role_id)

    def _load_role_permissions(self):
        """Загрузка данных о разрешениях ролей RBAC."""
        for role_id, permission_id in RolePermission.objects.values_list('role', 'permission'):
            self._role_permissions[role_id].add(permission_id)

    def _load_user_roles(self):
        """Загрузка данных о ролях пользователей."""
        query = UserRole.objects.filter(
            Q(date_to__isnull=True) | Q(date_to__gte=date.today()),
        ).values_list('content_type', 'object_id', 'date_from', 'date_to', 'role')

        for ct_id, obj_id, date_from, date_to, role_id in query:
            self._user_roles[ct_id, obj_id].add((date_from, date_to, role_id))

    def _get_role_descendants(self, role_id, include_self=False):
        """Возвращает вложенные роли."""
        result = set()

        if include_self:
            result.add(role_id)

        for child_role_id in self._role_children[role_id]:
            result.update(self._get_role_descendants(child_role_id, include_self=True))

        return result

    def _get_user_roles(self, user):
        """Возвращает все роли пользователя, в т.ч. и вложенные.

        :rtype: set
        """
        content_type_id = ContentType.objects.get_for_model(user).id
        roles_data = self._user_roles[content_type_id, user.id]
        today = date.today()

        return set(
            chain(
                *(
                    self._get_role_descendants(role_id, include_self=True)
                    for date_from, date_to, role_id in roles_data
                    if (date_from or today) <= today <= (date_to or today)
                )
            )
        )

    def _get_user_permissions(self, user):
        """Возврвщает все доступные пользователю разрешения.

        :rtype: itertools.chain
        """

        def get_role_permissions(role_id):
            # pylint: disable=protected-access
            for permission_id in self._role_permissions[role_id]:
                yield permission_id
                for name in self._manager.get_dependent_permissions(self._permissions_by_id[permission_id]):
                    yield self._permissions_by_name[name]

        return chain(*(get_role_permissions(role_id) for role_id in self._get_user_roles(user)))

    def _reload(self, force=False):
        """Перезагрузка кешируемых объектов при необходимости.

        :param bool force: Указывает на необходимость принудительной
            перезагрузки.
        """
        if force or self._is_out_of_date():
            self._clear()

            self._load_permissions()
            self._load_role_permissions()
            self._load_role_hierarchy()
            self._load_user_roles()

            self._loaded_at = time()

    def has_perm(self, user, perm_name):
        """Проверяет наличие у пользователя разрешения.

        :param user: Пользователь, возвращаемый функцией
            ioc.get('get_current_user').
        :param basestring perm_name: Имя разрешения.

        :rtype: bool
        """
        self._reload()

        assert perm_name in self._permissions_by_name, perm_name

        permission_id = self._permissions_by_name[perm_name]
        return permission_id in self._get_user_permissions(user)

    def has_access(self, action, request):
        """Проверяет наличие у текущего пользователя разрешения.

        :param action: Экшн, к которому проверяется наличие доступа.
        :type action: m3.actions.Action

        :param request: HTTP-запрос.
        :type request: django.http.HttpRequest

        :rtype: bool
        """
        if not self._need_check_access(action):
            return True

        user = self._get_current_user(request)
        if user is None:
            return False

        self._reload()

        # Id разрешений экшена, доступность которых будем проверять
        action_permissions = set(
            self._permissions_by_name[perm_name] for perm_name in self._get_action_permissions(action)
        )

        for permission_id in self._get_user_permissions(user):
            if permission_id in action_permissions:
                permission_name = self._permissions_by_id[permission_id]
                if self._check_permission(permission_name, action, request, user):
                    return True

        return False
