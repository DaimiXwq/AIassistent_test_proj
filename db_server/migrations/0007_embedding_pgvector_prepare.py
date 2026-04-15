from django.db import migrations


def prepare_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cursor.execute(
            """
            ALTER TABLE db_server_embedding
            ADD COLUMN IF NOT EXISTS vector_pg vector
            """
        )


def rollback_prepare_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE db_server_embedding
            DROP COLUMN IF EXISTS vector_pg
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("db_server", "0006_alter_chunk_options_alter_document_options_and_more"),
    ]

    operations = [
        migrations.RunPython(prepare_pgvector, rollback_prepare_pgvector),
    ]
