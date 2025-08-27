from django.db import (
    migrations,
)


def delete_reports(apps, schema_editor):
    """Удаляет отчеты с несуществующими источниками данных."""
    ReportTemplate = apps.get_model('report_constructor', 'ReportTemplate')
    ReportTemplate.objects.filter(data_source_name__in=('unit.Unit', 'person.Person')).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('report_constructor', '0007_include_available_units'),
    ]

    operations = [migrations.RunPython(delete_reports)]
