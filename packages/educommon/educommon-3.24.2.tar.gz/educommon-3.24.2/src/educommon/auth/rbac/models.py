# pylint: disable=no-init
"""Модели для хранения данных системы авторизации RBAC."""

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError,
)
from django.db import (
    models,
)
from django.db.models.signals import (
    post_delete,
    pre_delete,
)
from django.dispatch import (
    receiver,
)

from m3 import (
    ApplicationLogicException,
)
from m3.db import (
    safe_delete,
)

from m3_django_compat import (
    ModelOptions,
    atomic,
)
from m3_django_compat.exceptions import (
    FieldDoesNotExist,
)
from m3_django_compat.models import (
    GenericForeignKey,
)

from educommon.auth.rbac import (
    config,
)
from educommon.auth.rbac.permissions import (
    PERM__ROLE__EDIT,
)
from educommon.auth.rbac.utils import (
    get_permission_full_title,
)
from educommon.django.db.mixins.date_interval import (
    ActualObjectsManager,
    DateIntervalMeta,
    DateIntervalMixin,
)
from educommon.django.db.mixins.validation import (
    post_clean,
)
from educommon.django.db.models import (
    BaseModel,
)
from educommon.django.db.utils import (
    model_modifier_metaclass,
)
from educommon.m3.extensions.listeners.delete_check.mixins import (
    CascadeDeleteMixin,
)


class Permission(BaseModel):
    """Разрешение."""

    name = models.CharField(
        'Имя',
        max_length=100,
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        'Название',
        max_length=200,
        blank=True,
        null=True,
    )
    description = models.TextField(
        'Описание',
        blank=True,
    )
    hidden = models.BooleanField(
        'Видимость пользователям',
        default=False,
    )

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'

    def __str__(self):
        return 'Permission<{}: {}>'.format(self.id, self.name)


class Role(CascadeDeleteMixin, BaseModel):
    """Роль."""

    name = models.CharField(
        'Название',
        max_length=300,
        db_index=True,
        unique=True,
    )
    description = models.TextField(
        'Описание',
        blank=True,
    )
    can_be_assigned = models.BooleanField(
        'Может быть назначена пользователю',
        default=True,
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        through='RolePermission',
    )
    user_types = models.ManyToManyField(
        ContentType,
        verbose_name='Может быть назначена',
        through='RoleUserType',
        related_name='+',
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return 'Role<{}: {}>'.format(self.id, self.name)

    @property
    def subroles(self):
        """Возвращает все вложенные роли данной роли.

        :rtype: set
        """
        result = set()

        for role_parent in RoleParent.objects.filter(parent_id=self.id):
            result.add(role_parent.role)
            result.update(role_parent.role.subroles)

        return result

    def get_permissions(self):
        """Возвращает все разрешения роли, в т.ч. вложенных ролей.

        :rtype: QuerySet
        """
        roles = set([self]) | self.subroles
        result = Permission.objects.filter(
            pk__in=RolePermission.objects.filter(
                role__in=roles,
            ).values('permission'),
        )

        return result

    def simple_clean(self, errors):
        """Проверка бизнес-логики роли.

        Запрещает отключение флага `can_be_assigned`, если роль уже назначена пользователям.
        """
        super().simple_clean(errors)

        if self.pk and not self.can_be_assigned and self.userrole_set.exists():
            errors['can_be_assigned'].append('Есть пользователи, которым назначана роль "{}" '.format(self.name))

    def safe_delete(self) -> bool:
        """Безопасное удаление роли и связанных с ней связей.

        Удаляет связи роли с разрешениями и родителями. Если возникает
        ошибка целостности, возвращает False.
        """
        # safe_delete неправильно работает внутри транзакций, из-за этого
        # при вызове commit() валится IntegrityError, который надо обрабатывать
        # вручную.
        try:
            with atomic():
                # Удаление связей разрешений с ролью
                RolePermission.objects.filter(role=self).delete()

                # Удаление связей роли с родительскими ролями
                RoleParent.objects.filter(role=self).delete()

                # Удаление самой роли
                safe_delete(self)

            result = True
        except Exception as error:  # pylint: disable=broad-except
            if error.__class__.__name__ == 'IntegrityError':
                result = False
            else:
                raise

        return result


class RoleUserType(BaseModel):
    """M2M-модель "Тип пользователя роли"."""

    role = models.ForeignKey(
        Role,
        verbose_name='Роль',
        related_name='+',
        on_delete=models.CASCADE,
    )
    user_type = models.ForeignKey(
        ContentType,
        verbose_name='Тип пользователя',
        related_name='+',
        on_delete=models.CASCADE,
    )

    cascade_delete_for = (role,)
    display_related_error = False

    class Meta:
        unique_together = ('role', 'user_type')
        verbose_name = 'Тип пользователя роли'
        verbose_name_plural = 'Типы пользователей ролей'

    def simple_clean(self, errors):
        """Проверка соответствия типа пользователя и роли.

        Запрещает назначение роли пользователям, если:
        - роль не может быть назначена;
        - тип пользователя не входит в допустимые типы.
        """
        super().simple_clean(errors)

        from educommon.auth.rbac.config import (
            rbac_config,
        )

        if not self.role.can_be_assigned:
            errors['role'].append('Роль "{}" не может назначаться пользователям'.format(self.role.name))

        if rbac_config.user_types and self.user_type.model_class() not in rbac_config.user_types:
            errors['role'].append(
                'Роль "{}" не может быть назначена типу "{}".'.format(
                    self.role.name,
                    self.user_type.name,
                )
            )

    @staticmethod
    def clean_role(instance, errors, **kwargs):
        """Проверяет типы пользователей роли при её изменении.

        Не допускает ситуаций, когда при отключении возможности назначения
        роли пользователям остаются ссылки на типы пользователей.

        Вызывается через сигнал ``post_clean`` модели
        :class:`~educommon.auth.rbac.models.Role`.

        :param instance: Роль.
        :type instance: :class:`~educommon.auth.rbac.models.Role`

        :param errors: Словарь с сообщениями об ошибках валидации.
        :type errors: :class:`defaultdict`
        """
        if instance.can_be_assigned:
            return

        if instance.user_types.exists():
            errors[NON_FIELD_ERRORS].append(
                'Для снятия флага "Может быть назначена пользователя", необходимо отвязать все типы пользователей.'
            )


post_clean.connect(receiver=RoleUserType.clean_role, sender=Role, dispatch_uid='RoleUserType.clean_role')


class RolePermission(BaseModel):
    """M2M-модель "Разрешение роли"."""

    role = models.ForeignKey(
        Role,
        verbose_name='Роль',
        on_delete=models.CASCADE,
    )
    permission = models.ForeignKey(
        Permission,
        verbose_name='Разрешение',
        on_delete=models.CASCADE,
    )

    cascade_delete_for = (role,)
    display_related_error = False

    class Meta:
        verbose_name = 'Разрешение роли'
        verbose_name_plural = 'Разрешения ролей'
        unique_together = ('role', 'permission')
        db_table = 'rbac_role_permissions'

    def __str__(self):
        return 'Роль: {}; Разрешение: {}'.format(self.role.name, self.permission.title)


@receiver(pre_delete, sender=RolePermission)
def protect_role_edit_permission(instance, **kwargs):
    """Предотвращает удаление из всех ролей разрешение на редактирование роли.

    Если это разрешение удалить из всех ролей, то никто из пользователей больше
    не сможет внести изменения в реестр ролей.
    """
    if (
        not RolePermission.objects.filter(
            permission__name=PERM__ROLE__EDIT,
        )
        .exclude(
            id=instance.pk,
        )
        .exists()
        and instance.permission.name == PERM__ROLE__EDIT
    ):
        raise ApplicationLogicException(
            'Роль "{role}" является единственной ролью в Cистеме, в которой '
            'есть разрешение "{permission}". В системе должна оставаться '
            'возможность настройки ролей, поэтому удаление из неё этого '
            'разрешения невозможно. Для удаления разрешения "{permission}" '
            'из роли "{role}" сначала назначьте данное разрешение любой '
            'другой роли в системе.'.format(
                role=instance.role.name,
                permission=get_permission_full_title(instance.permission.name),
            )
        )


class RoleParent(BaseModel):
    """M2M-модель "Вложенная роль"."""

    parent = models.ForeignKey(Role, related_name='+', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name='+', on_delete=models.CASCADE)

    cascade_delete_for = (parent, role)
    display_related_error = False

    def simple_clean(self, errors):
        """Валидация вложенности роли.

        Проверяет:
        - роль не может быть вложена сама в себя;
        - отсутствие циклов в иерархии ролей.
        """
        super().simple_clean(errors)

        if self.parent.id == self.role.id:
            errors['parent'].append('Роль не может содержать сама себя')

        # Проверка отсутствия цикла
        query = RoleParent.objects.all()
        if self.pk:
            query = query.exclude(pk=self.pk)

        def check(target_role, role):
            for role_parent in query.filter(role=role):
                if target_role.id == role_parent.parent_id:
                    raise ValidationError('В иерархии ролей обнаружен цикл')
                check(target_role, role_parent.parent)

        try:
            # Проверка, нет ли self.role среди предков self.parent
            check(self.role, self.parent)
        except ValidationError as error:
            errors['parent'].extend(error.messages)

    def __str__(self):
        return 'RoleParent({} --> {})'.format(str(self.role), str(self.parent))

    class Meta:
        unique_together = ('parent', 'role')
        verbose_name = 'Вложенная роль'
        verbose_name_plural = 'Вложенные роли'


UserRoleMeta = model_modifier_metaclass(
    DateIntervalMeta,
    date_from=dict(
        verbose_name='Действует с',
    ),
    date_to=dict(
        verbose_name='по',
    ),
)


class UserRole(DateIntervalMixin, BaseModel, metaclass=UserRoleMeta):
    """M2M-модель "Роль пользователя"."""

    no_intersections_for = ('content_type', 'object_id', 'role')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = GenericForeignKey()
    role = models.ForeignKey(
        Role,
        verbose_name='Роль',
        on_delete=models.CASCADE,
    )

    actual_objects = ActualObjectsManager()

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователя'

    def __str__(self):
        return 'UserRole({} --> {})'.format(
            str(self.user),
            str(self.role),
        )

    def interval_intersected_error_message(self, others=None) -> str:
        """Сообщение об ошибке при пересечении интервалов действия роли."""
        return 'Роль "{}" уже назначена этому пользователю в указанном интервале дат.'.format(self.role.name)

    def simple_clean(self, errors):
        """Валидация бизнес-логики при назначении роли пользователю.

        Проверяет:
        - возможность назначения роли;
        - доступность роли для указанного типа пользователя.
        """
        super().simple_clean(errors)

        if not self.role.can_be_assigned:
            errors['role'].append('Роль "{}" не может быть назначена пользователю'.format(self.role.name))

        if (
            config.rbac_config.user_types
            and self.role_id
            and self.content_type_id
            and not RoleUserType.objects.filter(
                role_id=self.role_id,
                user_type_id=self.content_type_id,
            ).exists()
        ):
            errors['role'].append(
                'Роль "{}" не доступна для назначения пользователям типа "{}".'.format(
                    self.role.name,
                    self.content_type.name,
                )
            )


@receiver(post_delete)
def delete_user_roles(instance, **kwargs):  # pylint: disable=unused-argument
    """Удаление привязки ролей к пользователям при удалении пользователя."""
    # Если модель была удалена из Системы, то при накатывании миграций, в
    # которых удаляются записи таких моделей случается AttributeError.
    try:
        content_type = ContentType.objects.get_for_model(instance)
    except AttributeError:
        return

    if content_type is None:
        return

    opts = ModelOptions(instance)
    try:
        opts.get_field_by_name('id')
    except FieldDoesNotExist:
        return

    UserRole.objects.filter(
        content_type=content_type,
        object_id=instance.id,
    ).delete()
