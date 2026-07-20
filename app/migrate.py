"""Apply SQL migrations in order (tracked in schema_migrations).

Fresh Postgres (Docker, DigitalOcean managed DB, local createdb) only needs a
database — the app runs this on startup so you never hand-run five .sql files.
"""

from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def apply_migrations(database_url: str) -> list[str]:
    """Run pending migrations; return filenames applied this call."""
    applied_now: list[str] = []
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        return applied_now

    with psycopg.connect(database_url, autocommit=False) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename   TEXT PRIMARY KEY,
                applied_at   TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        done = {
            row[0]
            for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
        }

        # Droplets that used docker initdb.d before auto-migrate shipped already have
        # the full schema but no schema_migrations rows — record files without re-running.
        users_exists = conn.execute("SELECT to_regclass('public.users')").fetchone()[0]
        if users_exists and not done:
            with conn.transaction():
                for path in files:
                    conn.execute(
                        "INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT DO NOTHING",
                        (path.name,),
                    )
            done = {path.name for path in files}

        for path in files:
            if path.name in done:
                continue
            sql = path.read_text()
            with conn.transaction():
                conn.run(sql)
                conn.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)",
                    (path.name,),
                )
            applied_now.append(path.name)

    return applied_now
