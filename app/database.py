"""Database engine and session.

DATABASE_URL comes from the environment:
- Docker Compose: postgresql://...@db:5432/bookstore
- Render: Internal Database URL (injected from render.yaml)
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env.")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


def _engine_kwargs(url: str) -> dict:
    kwargs = {"pool_pre_ping": True}
    if "render.com" in url and "render-internal.com" not in url and "sslmode=" not in url:
        kwargs["connect_args"] = {"sslmode": "require"}
    return kwargs


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, **_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
