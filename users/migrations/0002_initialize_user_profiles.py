from django.conf import settings
from django.db import migrations


def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    UserProfile = apps.get_model("users", "UserProfile")

    db_alias = schema_editor.connection.alias

    for user in User.objects.using(db_alias).all().iterator():
        UserProfile.objects.using(db_alias).get_or_create(
            user=user,
            defaults={
                "group_type": "standard",
                "access_level": "4",
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_profiles_for_existing_users, noop_reverse),
    ]
