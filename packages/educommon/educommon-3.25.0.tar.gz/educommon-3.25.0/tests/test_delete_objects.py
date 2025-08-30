import os
from io import (
    StringIO,
)

from django.test import (
    TestCase,
)

from tests.testapp import (
    models,
)

from educommon.utils.system_app.management.commands.delete_objects import (
    call_custom_command,
)


APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class DeleteObjectsCommandTestCase(TestCase):
    """Тесты для команды educommon.utils.system_app.delete_objects."""

    count_const = 'ModelA Модель A 4\nModelB Модель B 4\n'
    some_count_const = 'ModelA Модель A 2\nModelB Модель B 2\n'

    def add_test_records(self):
        """Заполняет бд тестовыми данными."""
        chars = ('test1', 'test2', 'test3', 'test4')
        for index, name in enumerate(chars, 1):
            record = models.ModelA(
                pk=index,
                field_a=name,
            )
            record.full_clean()
            record.save()

        for index, name in enumerate(chars, 1):
            record = models.ModelB(pk=index, field_b=name, field_fk=models.ModelA.objects.get(field_a=name))
            record.full_clean()
            record.save()

    def test_data_option(self):
        """Тест работы опции --data."""
        # pylint: disable=protected-access
        self.add_test_records()
        out = StringIO()
        call_custom_command('delete_objects', '--model=modela', '--data', stdout=out)
        json_path = os.path.join(APP_DIR, 'tests', 'fixtures', 'delete_data.json')
        with open(json_path) as json_data:
            reference_data = json_data.read()
        self.assertMultiLineEqual(reference_data, out.getvalue())

    def test_count_option(self):
        """Тест работы опции --count."""
        # pylint: disable=protected-access
        self.add_test_records()
        out = StringIO()
        call_custom_command('delete_objects', '--model=modela', '--count', stdout=out)
        self.assertMultiLineEqual(self.count_const, out.getvalue())
        records = models.ModelA.objects.all().count()
        records += models.ModelB.objects.all().count()
        self.assertEqual(8, records)

    def test_some_objects(self):
        """Тест удаления части обьектов."""
        # pylint: disable=protected-access
        self.add_test_records()
        out = StringIO()
        call_custom_command('delete_objects', '--model=modela', '--count', '--id__gt=2', stdout=out)
        self.assertMultiLineEqual(self.some_count_const, out.getvalue())
        records = models.ModelA.objects.all().count()
        records += models.ModelB.objects.all().count()
        self.assertEqual(8, records)

    def test_delete_objects(self):
        """Тест удаления зависимых обьектов."""
        # pylint: disable=protected-access
        self.add_test_records()
        out = StringIO()
        call_custom_command('delete_objects', '--model=modela', '--id__gt=2', stdout=out)
        reference_queryset = models.ModelA.objects.filter(id__gt=2)
        reference_queryset_rel = models.ModelB.objects.filter(id__gt=2)
        records = models.ModelA.objects.all().count()
        self.assertEqual(2, records)
        records += models.ModelB.objects.all().count()
        self.assertQuerysetEqual([], reference_queryset)
        self.assertQuerysetEqual([], reference_queryset_rel)
        self.assertEqual(4, records)

    def test_literal_filter(self):
        """Тест удаления зависимых обьектов с символами кириллицы."""
        # pylint: disable=protected-access
        chars = ('тест1', 'тест2', 'тест3', 'тест4')
        for index, name in enumerate(chars, 1):
            record = models.ModelA(
                pk=index,
                field_a=name,
            )
            record.full_clean()
            record.save()

        for index, name in enumerate(chars, 1):
            record = models.ModelB(pk=index, field_b=name, field_fk=models.ModelA.objects.get(field_a=name))
            record.full_clean()
            record.save()
        out = StringIO()
        call_custom_command('delete_objects', '--model=modela', '--field_a=тест1', stdout=out)
        reference_queryset = models.ModelA.objects.filter(id__lte=1)
        reference_queryset_rel = models.ModelB.objects.filter(id__lte=1)
        records = models.ModelA.objects.all().count()
        self.assertEqual(3, records)
        records += models.ModelB.objects.all().count()
        self.assertQuerysetEqual([], reference_queryset)
        self.assertQuerysetEqual([], reference_queryset_rel)
        self.assertEqual(6, records)
