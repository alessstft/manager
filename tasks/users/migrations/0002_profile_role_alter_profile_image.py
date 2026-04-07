from django.db import migrations, models


def ensure_profiles_and_default_roles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('users', 'Profile')
    for user in User.objects.all():
        profile, _ = Profile.objects.get_or_create(user=user)
        if user.is_superuser and profile.role == 'employee':
            profile.role = 'admin'
            profile.save(update_fields=['role'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[('admin', 'Администратор'), ('employee', 'Сотрудник')],
                default='employee',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics'),
        ),
        migrations.RunPython(ensure_profiles_and_default_roles, migrations.RunPython.noop),
    ]
