"""Паки и экшены для окна реестра "Роли"."""

import json
from collections import (
    defaultdict,
)
from functools import (
    reduce,
)
from itertools import (
    chain,
)
from operator import (
    or_,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    Case,
    F,
    Q,
    Value,
    When,
)
from django.db.models.fields import (
    CharField,
)
from django.db.models.functions import (
    Concat,
)
from django.utils.functional import (
    cached_property,
)
from m3.actions import (
    ApplicationLogicException,
    PreJsonResult,
)
from m3.actions.results import (
    OperationResult,
)
from m3_django_compat import (
    atomic,
    get_request_params,
)

from objectpack.actions import (
    BaseAction,
    BasePack,
    ObjectPack,
    ObjectRowsAction,
    ObjectSelectWindowAction,
)
from objectpack.exceptions import (
    ValidationError,
)
from objectpack.models import (
    VirtualModel,
)
from objectpack.tools import (
    extract_int_list,
)
from objectpack.tree_object_pack.actions import (
    TreeObjectPack,
)

from educommon.auth.rbac import (
    ui,
)
from educommon.auth.rbac.config import (
    rbac_config,
)
from educommon.auth.rbac.constants import (
    PERM_SOURCE__DEPENDENCIES,
    PERM_SOURCE__NESTED_ROLE,
    PERM_SOURCE__ROLE,
)
from educommon.auth.rbac.manager import (
    rbac,
)
from educommon.auth.rbac.models import (
    Permission,
    Role,
    RoleParent,
    RolePermission,
    RoleUserType,
    UserRole,
)
from educommon.auth.rbac.permissions import (
    PERM_GROUP__ROLE,
)
from educommon.auth.rbac.utils import (
    get_permission_full_title,
)
from educommon.m3 import (
    convert_validation_error_to,
    get_id_value,
    get_pack,
    get_pack_id,
)


def _get_role(role_id):
    """Возвращает объект роли по ID или выбрасывает исключение."""
    try:
        return Role.objects.get(pk=role_id)
    except Role.DoesNotExist:
        raise ApplicationLogicException('Роль ID:{} не существует'.format(role_id))


class RolesTreeRowsAction(ObjectRowsAction):
    """Экшн, отдающий данные иерархии ролей.

    Т.к. одна и та же роль может быть включена в несколько ролей, то она также
    может отображаться вложенной в несколько ролей.
    """

    @cached_property
    def _parent_ids(self):
        """Id ролей, содержащих в себе другие роли.

        :rtype: set
        """
        result = RoleParent.objects.values_list('parent', flat=True).distinct()

        return set(result)

    def is_leaf(self, role):
        """Возвращает True, если данная роль не включает другие роли.

        :param role: Роль.
        :type role: Role

        :rtype: bool
        """
        if get_request_params(self.request).get('filter', False):
            result = True
        else:
            result = role.id not in self._parent_ids

        return result

    def prepare_object(self, obj):
        """Сохранение данных роли в словарь перед сериализацией в JSON."""
        data = super().prepare_object(obj)

        data['leaf'] = self.is_leaf(obj)

        return data

    def run(self, *args, **kwargs):
        """Тело Action, вызывается при обработке запроса к серверу."""
        result = super().run(*args, **kwargs)

        data = result.data.get('rows', [])

        return PreJsonResult(data)


class AddRoleToRoleWindowAction(ObjectSelectWindowAction):
    """Отображение окна добавления одной роли в другую."""

    def create_window(self):
        """Метод инстанцирует окно."""
        self.win = ui.RoleSelectWindow()

    def set_window_params(self):
        """Метод заполняет словарь self.win_params, который будет передан в окно.

        Этот словарь выступает как шина передачи данных от Actions/Packs к окну.
        """
        super().set_window_params()

        self.win_params['pack'] = self.parent

        role_id = getattr(self.context, self.parent.id_param_name)
        role = _get_role(role_id)
        self.win_params['role'] = role


class AddRoleToRoleAction(BaseAction):
    """Добавление одной роли к другой."""

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):
        """Тело Action, вызывается при обработке запроса к серверу."""
        role_parent = RoleParent(
            role=_get_role(getattr(context, self.parent.id_param_name)),
            parent=_get_role(context.parent_id),
        )
        role_parent.full_clean()
        role_parent.save()

        return OperationResult()


class DeleteRoleFromRoleAction(BaseAction):
    """Удаление одной роли из другой."""

    def run(self, request, context):
        """Тело Action, вызывается при обработке запроса к серверу."""
        try:
            role_parent = RoleParent.objects.get(
                role=_get_role(getattr(context, self.parent.id_param_name)), parent_id=context.parent_id
            )
        except RoleParent.DoesNotExist:
            raise ApplicationLogicException('Выбранная роль должна являться вложенной ролью.')

        role_parent.delete()

        return OperationResult()


class Pack(TreeObjectPack):
    """Пак окна реестра "Роли"."""

    model = Role
    title = 'Роли'

    columns = [
        dict(
            data_index='name',
            header='Название',
            searchable=True,
        ),
    ]

    list_window = ui.RolesListWindow
    add_window = ui.RoleAddWindow
    edit_window = ui.RoleEditWindow

    column_name_on_select = 'name'

    def __init__(self):
        super().__init__()

        self.replace_action('rows_action', RolesTreeRowsAction())

        self.add_role_to_role_window_action = AddRoleToRoleWindowAction()
        self.add_role_to_role_action = AddRoleToRoleAction()
        self.delete_role_from_role_action = DeleteRoleFromRoleAction()

        self.actions.extend(
            (
                self.add_role_to_role_window_action,
                self.add_role_to_role_action,
                self.delete_role_from_role_action,
            )
        )
        # ---------------------------------------------------------------------
        # Настройка разрешений для экшенов пака.
        self.need_check_permission = True
        self.perm_code = PERM_GROUP__ROLE

        for action in (
            self.autocomplete_action,
            self.list_window_action,
            self.multi_select_window_action,
            self.rows_action,
            self.select_window_action,
            self.edit_window_action,
        ):
            action.perm_code = 'view'

        for action in (
            self.new_window_action,
            self.save_action,
            self.delete_action,
            self.add_role_to_role_window_action,
            self.add_role_to_role_action,
            self.delete_role_from_role_action,
        ):
            action.perm_code = 'edit'
        # ---------------------------------------------------------------------

    def extend_menu(self, menu):
        """Размещает в меню Пуск ссылку Администрирование --> Роли."""
        return menu.administry(
            menu.Item(self.title, self.list_window_action),
        )

    def declare_context(self, action):
        """Декларирует контекст для экшна."""
        result = super().declare_context(action)

        if action in (self.rows_action, self.add_role_to_role_window_action, self.add_role_to_role_action):
            result[self.id_param_name] = dict(type='int')

        if action is self.rows_action:
            result['select_mode'] = dict(type='boolean', default=False)
            result['role_id'] = dict(type='int_or_none', default=None)

        if action is self.add_role_to_role_action:
            result['parent_id'] = dict(type='int')

        if action is self.save_action:
            result.update(
                name=dict(type='str'),
                description=dict(type='str', default=''),
                permissions=dict(type='int_list', default=[]),
                user_type_ids=dict(type='json_or_none', default=None),
            )
        if action is self.delete_role_from_role_action:
            result['parent_id'] = dict(type=int)

        return result

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных."""
        request_params = get_request_params(request)
        if request_params.get('filter'):
            return super().get_rows_query(request, context)

        current_role_id = getattr(context, self.id_param_name)

        if request_params.get('filter', False):
            result = super().get_rows_query(request, context)
        elif current_role_id < 0:
            # Вывод корневых ролей
            result = self.model.objects.exclude(pk__in=RoleParent.objects.values('role').distinct())
        else:
            # Вывод ролей, вложенных в указанную роль
            result = self.model.objects.filter(
                pk__in=RoleParent.objects.filter(parent=current_role_id).values('role').distinct()
            )

        if context.select_mode and context.role_id is not None:
            # Режим выбора роли, в которую будет добавлена указанная роль.
            # В этом режиме надо исключить возможность создания циклов в
            # иерархии ролей, поэтому из результатов запроса надо исключить
            # все подчиненные роли.
            try:
                role = Role.objects.get(pk=context.role_id)
            except Role.DoesNotExist:
                raise ApplicationLogicException('Роль ID:{} не найдена'.format(context.role_id))

            result = result.exclude(pk__in=set([role.id]) | set(r.id for r in role.subroles))

        return result

    def get_list_window_params(self, params, request, context):
        """Возвращает словарь параметров, которые будут переданы окну списка."""
        params = super().get_list_window_params(params, request, context)

        if not params['is_select_mode']:
            params['width'] = 700
            params['height'] = 600

        params['can_edit'] = rbac.has_access(self.save_action, request)

        return params

    def get_edit_window_params(self, params, request, context):
        """Возвращает словарь параметров, которые будут переданы окну редактирования."""
        params = super().get_edit_window_params(params, request, context)

        params['roles_pack'] = self
        params['partitions_pack'] = get_pack(PartitionsPack)
        params['permissions_pack'] = get_pack(PermissionsPack)

        result_pack = get_pack(ResultPermissionsPack)
        result_action = result_pack.result_permissions_action
        params['result_action_url'] = result_action.get_absolute_url()

        if rbac_config.user_types:
            params['show_user_types'] = True
            params['user_types'] = tuple(
                (u_type.id, u_type.name)
                for u_type in (ContentType.objects.get_for_models(*rbac_config.user_types).values())
            )
            if not params['create_new']:
                params['user_type_ids'] = tuple(params['object'].user_types.values_list('pk', flat=True))

        if not params['create_new']:
            params['permission_ids'] = list(params['object'].permissions.values_list('pk', flat=True))

        params['can_edit'] = rbac.has_access(self.save_action, request)
        if not params['can_edit']:
            params['title'] = self.format_window_title('Просмотр')

        return params

    @staticmethod
    def _bind_user_types_to_role(role, types):
        """Привязывает типы пользователей к роли.

        При необходимости удаления типов пользователей, происходит
        проверка на наличие уже существующих пользователей с
        удаляемыми типами.

        :param role: роль в системе
        :type role: educommon.auth.rbac.models.Role
        :param list of int types: список ID записей модели
            :class:`~django.contrib.contenttypes.models.ContentType`
        """
        new_user_types = set(types)
        old_user_types = set(role.user_types.values_list('pk', flat=True))

        types_to_delete = old_user_types - new_user_types
        user_roles_to_delete = UserRole.objects.filter(
            role=role,
            content_type_id__in=types_to_delete,
        )
        # Проверка, есть ли пользователи с удаляемыми типами
        if types_to_delete and user_roles_to_delete.exists():
            related_content_types = ContentType.objects.filter(pk__in=types_to_delete)
            raise ApplicationLogicException(
                'Невозможно отменить назначение роли для пользователей '
                'типа {}, т.к. данная роль уже назначена {} '
                'пользователей.'.format(
                    ', '.join('"{}"'.format(ct.name) for ct in related_content_types),
                    'этому типу' if len(types_to_delete) == 1 else 'этим типам',
                )
            )
        # Удаление лишних типов пользователей
        RoleUserType.objects.filter(role=role, user_type__in=types_to_delete).delete()
        # Добавление новых типов пользователей
        for user_type_id in new_user_types - old_user_types:
            RoleUserType.objects.create(role=role, user_type_id=user_type_id)

    @convert_validation_error_to(ValidationError)
    @atomic
    def save_row(self, obj, create_new, request, context):
        """Сохраняет объект."""
        # При отключении флага удаляются все связи с типами пользователей
        if not (create_new or obj.can_be_assigned):
            RoleUserType.objects.filter(role=obj).delete()
        # Сохранение роли
        obj.full_clean()
        obj.save()

        if obj.can_be_assigned:
            self._bind_user_types_to_role(obj, context.user_type_ids or ())
        # Сохранение связи с родительской ролью
        if create_new and context.parent_id is not None:
            try:
                parent = Role.objects.get(pk=context.parent_id)
            except Role.DoesNotExist:
                raise ApplicationLogicException('Роль ID:{} не существует.'.format(context.parent_id))

            RoleParent.objects.create(role=obj, parent=parent)
        else:
            new_permissions = set(extract_int_list(request, 'permissions'))
            old_permissions = set(obj.permissions.values_list('pk', flat=True))

            # Удаление прав у роли
            for link in RolePermission.objects.filter(
                role=obj,
                permission__in=old_permissions - new_permissions,
            ):
                link.delete()

            # Добавление новых прав в роль
            for permission_id in new_permissions - old_permissions:
                RolePermission.objects.get_or_create(role=obj, permission_id=permission_id)


class Partition(VirtualModel):
    """Виртуальная модель "Раздел системы".

    Используется в связи с тем, что сведения о разделах не сохраняются в БД.
    """

    def __init__(self, data):
        self.__dict__.update(data)

    @classmethod
    def _get_ids(cls):
        """Метод получения ID и названий разделов системы.

        Метод возвращает iterable, или callable, возвращаюший iterable,
        для каждого элемента которого (iterable) будет инстанцирован объект класса
        (каждый эл-т итератора передаётся в конструктор).
        """
        if not hasattr(cls, 'data'):
            cls.data = []
            for i, title in enumerate(sorted(rbac.partitions)):
                cls.data.append(dict(id=i, title=title))

        return cls.data

    def __str__(self):
        return self.title


class PartitionsPack(ObjectPack):
    """Пак для грида "Разделы системы" окна редактирования роли."""

    model = Partition

    columns = [
        dict(
            data_index='__str__',
            header='Модуль',
        ),
    ]

    allow_paging = False

    def __init__(self):
        super().__init__()
        # ---------------------------------------------------------------------

        self.need_check_permission = True
        self.perm_code = PERM_GROUP__ROLE

        for action in self.actions:
            action.perm_code = 'view'
        # ---------------------------------------------------------------------


class PermissionsPack(ObjectPack):
    """Пак для грида "Права доступа" окна редактирования роли."""

    model = Permission

    columns = (
        dict(
            data_index='title_with_group',
            header='Разрешение',
            column_renderer='columnRenderer',
            width=4,
        ),
        dict(
            data_index='description',
            hidden=True,
        ),
        dict(
            data_index='dependencies',
            header='Включает разрешения',
            width=5,
        ),
    )
    list_sort_order = ('title_with_group',)

    allow_paging = False

    def __init__(self):
        super().__init__()

        self.need_check_permission = True
        self.perm_code = PERM_GROUP__ROLE

        for action in self.actions:
            action.perm_code = 'view'

    def declare_context(self, action):
        """Декларирует контекст для экшна"""
        result = super().declare_context(action)

        if action is self.rows_action:
            result['partition_id'] = dict(type='int')

        return result

    def prepare_row(self, obj, request, context):
        """Установка дополнительных атрибутов объекта."""
        result = super().prepare_row(obj, request, context)

        permission_names = rbac.get_dependent_permissions(obj.name) - rbac.hidden_permissions
        result.dependencies = json.dumps(
            sorted(get_permission_full_title(dependency) for dependency in permission_names)
        )

        return result

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных."""
        # Определение название раздела по его id.
        try:
            partition = PartitionsPack.model.objects.get(id=context.partition_id).title
        except PartitionsPack.model.DoesNotExists:
            raise ApplicationLogicException('Раздел {} не существует'.format(context.partition_id))

        query = (
            super()
            .get_rows_query(request, context)
            .filter(
                # Условия для выборки разрешений только из раздела partition.
                reduce(or_, (Q(name__startswith=code + '/') for code in rbac.partitions[partition])),
                hidden=False,
            )
            .annotate(
                title_with_group=Case(
                    # Добавление названия группы к названию разрешения.
                    output_field=CharField(),
                    *(
                        When(
                            name__startswith=group + '/',
                            then=Concat(
                                Value(title + ' - ' if title else ''),
                                F('title'),
                            ),
                        )
                        for group, title in rbac.groups.items()
                    ),
                )
            )
        )

        return query


# -----------------------------------------------------------------------------


def _get_group_name(perm_name):
    """Возвращает имя группы разрешения."""
    return perm_name.split('/')[0]


def _get_group_title(perm_name):
    """Возвращает название группы разрешений."""
    group_name = _get_group_name(perm_name)
    group_title = rbac.groups[group_name]

    return group_title


def _get_partition_title(perm_name):
    """Возвращает название раздела, к которому относится разрешение."""
    group_name = perm_name.split('/')[0]

    for title, names in rbac.partitions.items():
        if group_name in names:
            return title

    return ''


class ResultPermissionsAction(BaseAction):
    """Возвращает данные для грида "Итоговые разрешения"."""

    def _get_nested_roles(self, role_id):
        """Возвращает все вложенные роли для заданной роли.

        Строит рекурсивное множество дочерних ролей, включая вложенные на любой глубине.
        """
        role_children = defaultdict(set)
        query = RoleParent.objects.values_list('parent', 'role')

        for parent_id, child_id in query:
            role_children[parent_id].add(child_id)

        def get_nested_roles(rid):
            result = set()

            if rid in role_children:
                for child_id in role_children[rid]:
                    result.add(child_id)
                    result.update(get_nested_roles(child_id))

            return result

        return get_nested_roles(role_id)

    def _get_nested_roles_permissions(self, role_id):
        """Возвращает разрешения, назначенные вложенным ролям заданной роли."""
        query = Permission.objects.filter(
            pk__in=RolePermission.objects.filter(role_id__in=self._get_nested_roles(role_id)).values('permission'),
            hidden=False,
        ).values_list('name', 'title', 'description')

        for name, title, description in query:
            yield dict(
                name=name,
                group=_get_group_title(name),
                partition=_get_partition_title(name),
                title=title,
                description=description,
                source=PERM_SOURCE__NESTED_ROLE,
            )

    def _get_dependent_permissions(self, permission_ids):
        """Возвращает разрешения, от которых зависят указанные разрешения.

        Исключает скрытые разрешения и формирует структуру для отображения
        в интерфейсе.
        """
        permissions_by_id = {
            pk: (name, title, description)
            for pk, name, title, description in Permission.objects.filter(
                hidden=False,
            ).values_list('pk', 'name', 'title', 'description')
        }
        permissions_by_name = {
            name: (pk, title, description) for pk, (name, title, description) in permissions_by_id.items()
        }

        for perm_id in permission_ids:
            # Может случиться так, что к роли будут привязаны скрытые
            # разрешения, но в permissions_by_id скрытых разрешений нет.
            if perm_id not in permissions_by_id:
                # Пропускаем скрытые разрешения.
                continue
            perm_name, _, _ = permissions_by_id[perm_id]
            dependent_perm_names = rbac.get_dependent_permissions(perm_name)
            dependent_perm_names -= rbac.hidden_permissions
            for name in dependent_perm_names:
                _, title, description = permissions_by_name[name]
                yield dict(
                    name=name,
                    group=_get_group_title(name),
                    partition=_get_partition_title(name),
                    title=title,
                    description=description,
                    source=PERM_SOURCE__DEPENDENCIES,
                )

    def _get_role_permissions(self, permission_ids):
        """Возвращает основные разрешения, явно назначенные роли."""
        query = Permission.objects.filter(
            pk__in=permission_ids,
            hidden=False,
        ).values_list('name', 'title', 'description', 'hidden')

        for name, title, description, hidden in query:
            if not hidden and _get_group_name(name) in rbac.groups:
                yield dict(
                    name=name,
                    group=_get_group_title(name),
                    partition=_get_partition_title(name),
                    title=title,
                    description=description,
                    source=PERM_SOURCE__ROLE,
                )

    def run(self, request, context):
        """Обрабатывает запрос на получение итоговых разрешений роли.

        Комбинирует разрешения:
        - явно назначенные роли;
        - зависимые разрешения;
        - разрешения вложенных ролей.

        Возвращает данные, сгруппированные по разделам и группам.
        """
        perm_names = set()

        data = defaultdict(lambda: defaultdict(list))

        for perm_data in chain(
            self._get_role_permissions(context.role_permissions),
            self._get_dependent_permissions(context.role_permissions),
            self._get_nested_roles_permissions(get_id_value(context, Pack)),
        ):
            if perm_data['name'] not in perm_names:
                perm_names.add(perm_data['name'])

                partition_title = perm_data['partition']
                group_title = perm_data['group']

                data[partition_title][group_title].append(
                    dict(
                        title=perm_data['title'],
                        description=perm_data['description'],
                        source=perm_data['source'],
                    )
                )

        return PreJsonResult(data)


class ResultPermissionsPack(BasePack):
    """Набор действий для грида "Итоговые разрешения" окна редактирования."""

    def __init__(self):
        super().__init__()
        # ---------------------------------------------------------------------

        self.result_permissions_action = ResultPermissionsAction()

        self.actions.extend((self.result_permissions_action,))
        # ---------------------------------------------------------------------

        self.need_check_permission = True
        self.perm_code = PERM_GROUP__ROLE

        for action in self.actions:
            action.perm_code = 'view'
        # ---------------------------------------------------------------------

    def declare_context(self, action):
        """Декларация контекста для экшна."""
        result = super().declare_context(action)

        if action is self.result_permissions_action:
            result[get_pack_id(Pack)] = dict(type='int_or_none', default=None)
            result['role_permissions'] = dict(type='int_list', default=())

        return result


# -----------------------------------------------------------------------------
