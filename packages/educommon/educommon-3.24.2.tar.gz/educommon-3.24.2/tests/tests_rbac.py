"""Тесты для моделей приложения."""

from abc import (
    ABCMeta,
    abstractmethod,
)

from django.core.exceptions import (
    ValidationError,
)
from django.test import (
    TestCase,
)

from educommon.auth.rbac.manager import (
    RBACManager,
)
from educommon.auth.rbac.models import (
    Permission,
    Role,
    RoleParent,
    RolePermission,
)


class RoleTestCase(TestCase):
    """Тесты для модели "Роль"."""

    @classmethod
    def setUp(cls):
        cls.roles = {}
        for i in range(1, 9):
            r = Role(name='role{}'.format(i))
            r.full_clean()
            r.save()
            cls.roles[i] = r

        # Вложенность ролей (child, parent)
        links = (
            (2, 1),
            (3, 1),
            (4, 2),
            (5, 2),
            (6, 2),
            (5, 3),
            (6, 3),
            (7, 3),
            (8, 3),
        )
        for child, parent in links:
            child, parent = cls.roles[child], cls.roles[parent]
            rp = RoleParent(role=child, parent=parent)
            rp.full_clean()
            rp.save()

        cls.permissions = {
            1: 'p1',
            2: 'p2',
            3: 'p3',
            4: 'p4',
        }
        for i, name in cls.permissions.items():
            permission = Permission(name=name)
            permission.full_clean()
            permission.save()
            cls.permissions[i] = permission

        role_permissions = {
            2: (1, 2),
            6: (3,),
            8: (4,),
        }
        for role, permissions in role_permissions.items():
            role = cls.roles[role]
            for permission in permissions:
                permission = cls.permissions[permission]
                RolePermission.objects.create(
                    role=role,
                    permission=permission,
                )

    @classmethod
    def tearDown(cls):
        RoleParent.objects.all().delete()
        RolePermission.objects.all().delete()
        Role.objects.all().delete()
        cls.roles = {}

    def test_cycle(self):
        """Проверка на невозможность создания циклов в иерархии."""
        links = (
            # role, parent
            (1, 6),
            (1, 4),
        )

        for role, parent in links:
            rp = RoleParent(role=self.roles[role], parent=self.roles[parent])
            self.assertRaises(ValidationError, rp.full_clean)

    def test_subroles(self):
        """Проверка свойства Role.subroles."""
        test_data = {
            1: (2, 3, 4, 5, 6, 7, 8),
            2: (4, 5, 6),
            3: (5, 6, 7, 8),
            4: (),
            5: (),
            6: (),
            7: (),
            8: (),
        }
        for role, subroles in test_data.items():
            role = self.roles[role]
            self.assertEquals(set('role{}'.format(i) for i in subroles), set(r.name for r in role.subroles))

    def test_permissions(self):
        """Проверка правильности формирования списков разрешений для роли."""
        test_data = {
            1: (1, 2, 3, 4),
            2: (1, 2, 3),
            3: (3, 4),
            4: (),
            5: (),
            6: (3,),
            7: (),
            8: (4,),
        }
        for role, permissions in test_data.items():
            role = self.roles[role]
            for i in permissions:
                self.assertIn(self.permissions[i], role.get_permissions())


class ManagerTestCaseBase(metaclass=ABCMeta):
    """Тесты для менеджера RBAC."""

    @property
    @abstractmethod
    def _rbac_backend_class_name(self):
        pass

    def setUp(self):
        if not hasattr(self, 'rbac'):
            with self.settings(RBAC_BACKEND=self._rbac_backend_class_name):
                self.rbac = RBACManager()
                self.rbac.init()

        return super(ManagerTestCaseBase, self).setUp()

    def test_permission_dependencies(self):
        """Проверка правильности обработки зависимостей."""
        from tests.rbac_test.permissions import (
            PERM__PACK1__EDIT,
            PERM__PACK1__VIEW,
            PERM__PACK2__EDIT,
            PERM__PACK2__VIEW,
            PERM__PACK3__EDIT,
            PERM__PACK3__VIEW,
        )

        permissions_map = {
            PERM__PACK1__EDIT: {
                PERM__PACK1__VIEW,
                PERM__PACK2__VIEW,
                PERM__PACK3__EDIT,
                PERM__PACK3__VIEW,
            },
            PERM__PACK2__EDIT: {
                PERM__PACK2__VIEW,
                PERM__PACK3__EDIT,
                PERM__PACK3__VIEW,
                PERM__PACK1__EDIT,
                PERM__PACK1__VIEW,
            },
            PERM__PACK3__VIEW: {
                PERM__PACK1__EDIT,
                PERM__PACK1__VIEW,
                PERM__PACK2__VIEW,
                PERM__PACK3__EDIT,
            },
        }

        for permission, dependencies in permissions_map.items():
            self.assertEquals(self.rbac.get_dependent_permissions(permission), dependencies)


class ManagerWithSimpleBackendTestCase(ManagerTestCaseBase, TestCase):
    """Проверка менеджера RBAC с НЕкеширующим бэкендом ."""

    _rbac_backend_class_name = 'educommon.auth.rbac.backends.simple.SimpleBackend'


class ManagerWithCachingBackendTestCase(ManagerTestCaseBase, TestCase):
    """Проверка менеджера RBAC с кеширующим бэкендом ."""

    _rbac_backend_class_name = 'educommon.auth.rbac.backends.caching.CachingBackend'
