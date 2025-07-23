import os
import warnings
from urllib.parse import quote_plus

def _resolve_database_uri() -> str:
    """
    Resolve the best database URI to use.
    Priority:
      1. DATABASE_URL (Render / Docker / CI)
      2. POSTGRES_ env parts (common in docker-compose)
      3. SQLite fallback (local dev emergency)
    Also normalizes old 'postgres://' scheme for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        # Normalize deprecated prefix
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    # Try to assemble from pieces
    pg_user = os.getenv("POSTGRES_USER")
    pg_pass = os.getenv("POSTGRES_PASSWORD")
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db   = os.getenv("POSTGRES_DB")

    if pg_user and pg_pass and pg_db:
        # URL-encode password in case of special chars
        pg_pass_enc = quote_plus(pg_pass)
        return f"postgresql://{pg_user}:{pg_pass_enc}@{pg_host}:{pg_port}/{pg_db}"

    # Fallback (safe for local dev; not for prod)
    warnings.warn(
        "DATABASE_URL not set and no POSTGRES_* env vars found. "
        "Falling back to local SQLite 'sqlite:///local.db'.",
        RuntimeWarning,
    )
    return "sqlite:///local.db"


class Config:
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret")  # change in prod!

    # Optional: control Flask/Swagger behavior
    JSON_SORT_KEYS = False