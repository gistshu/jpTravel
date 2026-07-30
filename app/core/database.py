from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import castle, castle_journal, user
from app.models.base import Base

_ = (castle, castle_journal, user)

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
