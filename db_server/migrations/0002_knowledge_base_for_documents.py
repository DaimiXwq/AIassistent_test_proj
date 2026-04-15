from django.db import migrations, models
import django.db.models.deletion


def populate_default_knowledge_base(apps, schema_editor):
    KnowledgeBase = apps.get_model("db_server", "KnowledgeBase")
    Document = apps.get_model("db_server", "Document")

    default_kb, _ = KnowledgeBase.objects.get_or_create(
        slug="default",
        defaults={
            "name": "Default",
            "visibility": "shared",
            "description": "Default shared knowledge base",
        },
    )

    Document.objects.filter(knowledge_base__isnull=True).update(knowledge_base=default_kb)


class Migration(migrations.Migration):

    dependencies = [
        ("db_server", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="KnowledgeBase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("visibility", models.CharField(choices=[("shared", "Shared"), ("personal", "Personal")], max_length=20)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="document",
            name="knowledge_base",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="db_server.knowledgebase",
            ),
        ),
        migrations.RunPython(populate_default_knowledge_base, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="document",
            name="knowledge_base",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="db_server.knowledgebase",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["knowledge_base", "created_at"], name="db_server_d_knowled_324a38_idx"),
        ),
    ]
