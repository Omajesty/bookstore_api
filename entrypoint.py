"""Container startup: wait for Postgres, migrate, then serve.

On Render the HTTP port is $PORT (default 10000), not 8000.
"""

import os
import subprocess
import sys
import time

from sqlalchemy import create_engine, text

from app.database import _engine_kwargs, get_database_url


def wait_for_db(url: str, attempts: int = 60) -> None:
    for i in range(1, attempts + 1):
        try:
            engine = create_engine(url, **_engine_kwargs(url))
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except Exception as exc:
            print(f"Waiting for database... ({i}/{attempts}) {exc}")
            time.sleep(2)
    print("Could not connect to the database.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    url = get_database_url()
    wait_for_db(url)
    subprocess.check_call(["alembic", "upgrade", "head"])
    port = os.getenv("PORT", "8000")
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port],
    )


if __name__ == "__main__":
    main()
