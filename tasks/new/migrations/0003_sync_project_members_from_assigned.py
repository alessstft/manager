from django.db import migrations


def sync_project_members(apps, schema_editor):
    Project = apps.get_model('new', 'Project')
    for p in Project.objects.all():
        p.members.add(p.owner_id)
        if p.assigned_to_id and p.assigned_to_id != p.owner_id:
            p.members.add(p.assigned_to_id)


class Migration(migrations.Migration):

    dependencies = [
        ('new', '0002_project_assigned_to'),
    ]

    operations = [
        migrations.RunPython(sync_project_members, migrations.RunPython.noop),
    ]
