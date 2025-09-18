import sys

import psycopg

from app.database import _dsn
from app.config import settings


CREATE_USERS_SQL = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL
    );
    """
)


def _admin_dsn() -> str:
    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/postgres"
    )


def main() -> int:
    # Ensure server is reachable via admin database first
    try:
        with psycopg.connect(_admin_dsn(), autocommit=True) as admin_conn:
            with admin_conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.postgres_db,))
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(f"CREATE DATABASE {psycopg.sql.Identifier(settings.postgres_db).string}")
                    print(f"database '{settings.postgres_db}' created.")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to reach postgres server on admin DB: {exc}")
        print(
            "Start PostgreSQL and verify host/port/user/password in environment variables."
        )
        return 1

    # Now ensure table in target database
    try:
        dsn = _dsn()
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_USERS_SQL)
            conn.commit()
        print("users table ensured (created if missing).")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to initialize users table: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


