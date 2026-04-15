from django.db import migrations


def backfill_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        # Step 1 of migration plan: copy historical JSON embeddings into pgvector column.
        cursor.execute(
            """
            UPDATE db_server_embedding
            SET vector_pg = vector::text::vector
            WHERE vector_pg IS NULL
              AND vector IS NOT NULL
            """
        )

        # Step 2 of migration plan: create an ANN index for cosine similarity queries.
        # Keep this index partial to skip not-yet-migrated rows.
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS dbs_emb_vector_pg_ivfflat_idx
            ON db_server_embedding
            USING ivfflat (vector_pg vector_cosine_ops)
            WHERE vector_pg IS NOT NULL
            """
        )


def rollback_backfill_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            DROP INDEX IF EXISTS dbs_emb_vector_pg_ivfflat_idx
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("db_server", "0007_embedding_pgvector_prepare"),
    ]

    operations = [
        migrations.RunPython(backfill_pgvector, rollback_backfill_pgvector),
    ]
