import os.path

from django.db import (
    migrations,
)

from educommon.django.db.migration.operations import (
    CorrectSequence,
    LoadFixture,
)


APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Migration(migrations.Migration):
    dependencies = [
        ('async', '0001_initial'),
    ]

    operations = [
        LoadFixture(os.path.join(APP_DIR, 'fixtures', 'initial_data.json')),
        CorrectSequence('AsyncTaskType'),
    ]
