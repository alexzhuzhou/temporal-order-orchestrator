from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import DB_URL

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Run schema.sql against the configured DB."""
    schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
