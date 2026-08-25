from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import castle, castle_journal, journal_recommendation, user
from app.models.base import Base

_ = (castle, castle_journal, journal_recommendation, user)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session]:
    """Yield a database session for request-scoped dependencies."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def create_database_tables() -> None:
    """Create database tables for local development bootstrap."""
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_schema()


def _migrate_sqlite_schema() -> None:
    """Apply lightweight SQLite schema additions for local development."""
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "journal_recommendations" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("journal_recommendations")
    }
    column_definitions = {
        "address": "VARCHAR(255)",
        "image_urls_json": "TEXT DEFAULT '[]' NOT NULL",
        "latitude": "FLOAT",
        "longitude": "FLOAT",
        "osm_type": "VARCHAR(16)",
        "osm_id": "VARCHAR(32)",
        "osm_url": "VARCHAR(500)",
        "rating": "INTEGER",
    }
    with engine.begin() as connection:
        for column_name, column_type in column_definitions.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        "ALTER TABLE journal_recommendations "
                        f"ADD COLUMN {column_name} {column_type}",
                    ),
                )
