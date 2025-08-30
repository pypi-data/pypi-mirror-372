from django.apps import (
    apps,
)
from django.core.exceptions import (
    ValidationError,
)
from django.test import (
    TestCase,
)

from educommon.django.db.utils import (
    LazyModel,
)


class LazyModelTestCase(TestCase):
    """Тесты для класса educommon.django.db.utils.LazyModel."""

    def test(self):
        model = apps.get_model('testapp', 'ModelA')

        for arg in ('testapp.ModelA', ('testapp', 'ModelA'), model):
            lazy_model = LazyModel(arg)
            self.assertIs(lazy_model.get_model(), model)


class ModelModifierWIthMetaClassTestCase(TestCase):
    """
    Тесты для утилиты educommon.django.db.utils.model_modifier_metaclass.
    """

    def test_max_length_validator(self):
        """Проверяет валидатор максимальной длины.

        Валидатор максимальной длины должен отличаться у наследников
            абстрактной модели и моделей модифицированных утилитой.
        """
        ModelModifierWIthMetaClassFirst = apps.get_model('testapp', 'ModelModifierWIthMetaClassFirst')
        ModelModifierWIthMetaClassSecond = apps.get_model('testapp', 'ModelModifierWIthMetaClassSecond')

        ModelModifierWIthMetaClassThird = apps.get_model('testapp', 'ModelModifierWIthMetaClassThird')

        first_max_len_validator = ModelModifierWIthMetaClassFirst._meta.get_field('name').validators[0]
        second_max_len_validator = ModelModifierWIthMetaClassSecond._meta.get_field('name').validators[0]
        third_max_len_validator = ModelModifierWIthMetaClassThird._meta.get_field('name').validators[0]
        # Валидатор обычной модели-наследника
        # должен отличаться от модифицрованной.
        self.assertIsNot(first_max_len_validator, second_max_len_validator)
        # и между собой модифицированные должны отличаться.
        self.assertIsNot(second_max_len_validator, third_max_len_validator)

        # в первой модели ограничение должно остаться, 20 симоволов.
        ModelModifierWIthMetaClassFirst.objects.create(name='a' * 20)
        with self.assertRaises(ValidationError):
            ModelModifierWIthMetaClassFirst.objects.create(name='a' * 21)

        # во второй модели ограничение должно быть 10 симоволов.
        ModelModifierWIthMetaClassSecond.objects.create(name='a' * 10)
        with self.assertRaises(ValidationError):
            ModelModifierWIthMetaClassSecond.objects.create(name='a' * 11)

        # в третьей модели ограничение должно быть 30 симоволов.
        ModelModifierWIthMetaClassThird.objects.create(name='a' * 30)
