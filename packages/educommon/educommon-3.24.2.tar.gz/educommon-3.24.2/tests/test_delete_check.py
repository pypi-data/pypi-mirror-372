import json

from django.test import (
    TestCase,
)
from m3.actions import (
    ControllerCache,
)

from tests.delete_check.actions import (
    DeleteCheckPack,
)
from tests.delete_check.models import (
    DeleteCheckModel1,
    DeleteCheckModel2,
    DeleteCheckModel3,
    DeleteCheckModel4,
)

from educommon.m3 import (
    get_pack,
)


class DeleteCheckListenerTestCase(TestCase):
    """Тесты для примесей слушателя DeleteCheck."""

    @classmethod
    def setUpClass(cls):
        super(DeleteCheckListenerTestCase, cls).setUpClass()

        ControllerCache.populate()

    def test__cascade_delete_mixin(self):
        """Проверка работоспособности CascadeDeleteMixin."""
        obj1 = DeleteCheckModel1.objects.create()
        obj2 = DeleteCheckModel2.objects.create()
        obj3 = DeleteCheckModel3.objects.create(fk1=obj1, fk2=obj2)
        obj4 = DeleteCheckModel4.objects.create(fk1=obj1, fk2=obj2)

        obj2.safe_delete()
        self.assertTrue(
            DeleteCheckModel3.objects.filter(pk=obj3.pk, fk2__isnull=True).exists(),
        )
        self.assertTrue(
            DeleteCheckModel4.objects.filter(
                pk=obj4.pk,
                fk2__isnull=True,
            ).exists(),
        )

        obj1.safe_delete()
        self.assertFalse(
            DeleteCheckModel3.objects.filter(pk=obj3.pk).exists(),
        )
        self.assertTrue(
            DeleteCheckModel4.objects.filter(pk=obj4.pk, fk1_id__isnull=False).exists(),
        )

    def test__cascade_delete_pack_mixin(self):
        """Проверка работоспособности CascadeDeletePackMixin."""
        obj1 = DeleteCheckModel1.objects.create()
        obj3 = DeleteCheckModel3.objects.create(fk1=obj1)
        # ---------------------------------------------------------------------

        pack = get_pack(DeleteCheckPack)
        delete_url = pack.delete_action.get_absolute_url()

        response = self.client.post(delete_url, {pack.id_param_name: obj1.pk})
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content)
        self.assertTrue(result['success'])
        # ---------------------------------------------------------------------

        self.assertFalse(
            DeleteCheckModel1.objects.filter(pk=obj1.pk).exists(),
        )
        self.assertFalse(
            DeleteCheckModel3.objects.filter(pk=obj3.pk).exists(),
        )
