#!/usr/bin/env python
"""One-time migration: copy data from the legacy SQLite database into PostgreSQL.

If you are reading this because your app is already on Postgres, you do not need
to run this script again.

Requirements:
    - DATABASE_URL must be set to the PostgreSQL connection string.
    - The legacy SQLite file must exist (backend/pwf_app.db by default).

Usage:
    DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require \
        python migrate_sqlite_to_postgres.py

You can override the source with SQLITE_SOURCE_FILE=path/to/file.db
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import MetaData, create_engine, text  # noqa: E402

from app import models  # noqa: F401,E402  (registers ORM tables on Base.metadata)
from app.database import Base, DATABASE_URL  # noqa: E402

SQLITE_FILE = Path(os.getenv("SQLITE_SOURCE_FILE", str(BACKEND_DIR / "pwf_app.db")))

# Tables must be written in FK-safe order (parents first).
TABLE_ORDER = [
    "causes",
    "donations",
    "contact_inquiries",
    "team_members",
    "certificates",
    "gallery_items",
    "video_gallery",
    "upcoming_projects",
    "blogs",
    "about_info",
    "media_coverage",
]


def main():
    if not SQLITE_FILE.exists():
        sys.exit(f"SQLite source not found: {SQLITE_FILE}")

    sqlite_engine = create_engine(
        f"sqlite:///{SQLITE_FILE.as_posix()}", connect_args={"check_same_thread": False}
    )
    pg_engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(bind=pg_engine)
    print("PostgreSQL schema ready.")

    with pg_engine.begin() as pg_conn:
        pg_conn.execute(text(f"TRUNCATE TABLE {', '.join(TABLE_ORDER)} RESTART IDENTITY CASCADE"))
    print("Target tables truncated. Copying data...")

    with pg_engine.begin() as pg_conn:
        for table_name in TABLE_ORDER:
            target_table = Base.metadata.tables[table_name]
            target_columns = set(target_table.c.keys())

            with sqlite_engine.connect() as sqlite_conn:
                source_exists = sqlite_conn.execute(
                    text(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='table' AND name=:name"
                    ),
                    {"name": table_name},
                ).scalar()
                if not source_exists:
                    print(f"  - {table_name}: 0 rows (table missing in source, skipped)")
                    continue

                rows = sqlite_conn.execute(text(f"SELECT * FROM {table_name}")).mappings().all()

            if not rows:
                print(f"  - {table_name}: 0 rows (skipped)")
                continue

            data = [
                {k: v for k, v in row.items() if k in target_columns}
                for row in rows
            ]
            pg_conn.execute(target_table.insert(), data)

            sequence = pg_conn.execute(
                text("SELECT pg_get_serial_sequence(:table, 'id')"), {"table": table_name}
            ).scalar()
            if sequence:
                pg_conn.execute(
                    text(f"SELECT setval(:seq, (SELECT MAX(id) FROM {table_name}))"),
                    {"seq": sequence},
                )

            print(f"  - {table_name}: {len(rows)} rows copied")

    print("\nVerifying row counts...")
    ok = True
    with pg_engine.connect() as pg_conn:
        with sqlite_engine.connect() as sqlite_conn:
            for table_name in TABLE_ORDER:
                source_count = sqlite_conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                ).scalar()
                target_count = pg_conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                ).scalar()
                status = "OK" if source_count == target_count else "MISMATCH"
                if source_count != target_count:
                    ok = False
                print(f"  - {table_name}: sqlite={source_count} postgres={target_count} [{status}]")

    sqlite_engine.dispose()
    pg_engine.dispose()
    if ok:
        print("\nMigration finished successfully.")
    else:
        print("\nMigration finished WITH MISMATCHES. Investigate before switching over.")


if __name__ == "__main__":
    main()