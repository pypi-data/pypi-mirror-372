"""Unit-тесты для роутера моделей приложения, использующего сервисную БД."""

from django.apps.registry import (
    apps,
)
from django.test import (
    TestCase,
)

from educommon.django.db.routers import (
    ServiceDbRouterBase,
)

from .settings import (
    DEFAULT_DB_ALIAS,
    SERVICE_DB_ALIAS,
)


class ServiceDbRouterTestCase(TestCase):
    """Тесты для роутера моделей приложения, использующего сервисную БД."""

    def test(self):
        """Проверка правильности выбора роутером базы данных."""
        model1 = apps.get_model('testapp', 'ModelA')
        model2 = apps.get_model('testapp', 'ModelB')
        model3 = apps.get_model('testapp', 'ModelC')

        class DatabaseRouter(ServiceDbRouterBase):
            app_name = 'testapp'
            service_db_model_names = set(['ModelB'])

        router = DatabaseRouter()

        self.assertEqual(router.db_for_read(model1), DEFAULT_DB_ALIAS)
        self.assertEqual(router.db_for_read(model2), SERVICE_DB_ALIAS)
        self.assertEqual(router.db_for_read(model3), DEFAULT_DB_ALIAS)

        self.assertTrue(router._allow(DEFAULT_DB_ALIAS, 'testapp', 'ModelA'))
        self.assertFalse(router._allow(SERVICE_DB_ALIAS, 'testapp', 'ModelA'))

        self.assertFalse(router._allow(DEFAULT_DB_ALIAS, 'testapp', 'ModelB'))
        self.assertTrue(router._allow(SERVICE_DB_ALIAS, 'testapp', 'ModelB'))

        self.assertTrue(router._allow(DEFAULT_DB_ALIAS, 'testapp', 'ModelC'))
        self.assertFalse(router._allow(SERVICE_DB_ALIAS, 'testapp', 'ModelC'))
