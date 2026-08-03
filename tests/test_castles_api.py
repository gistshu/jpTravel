from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db_session
from app.main import create_app
from app.models.base import Base
from app.models.castle import Castle


def build_test_session() -> Generator[Session]:
    """Yield an in-memory SQLite session for API tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    db_session.add(
        Castle(
            source_location_id="loc-1",
            name="五稜郭",
            address="函館市五稜郭町44 - 3",
            latitude=41.797184,
            longitude=140.756831,
            source_url="https://example.com/source",
        )
    )
    db_session.commit()
    try:
        yield db_session
    finally:
        db_session.close()


def test_castles_api_returns_markers() -> None:
    """Castles API should return map marker data."""
    application = create_app()
    application.dependency_overrides[get_db_session] = build_test_session
    client = TestClient(application)

    response = client.get("/api/v1/castles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "查詢成功"
    assert payload["errors"] == []
    assert payload["data"] == [
        {
            "id": 1,
            "name": "五稜郭",
            "prefecture": "",
            "address": "函館市五稜郭町44 - 3",
            "latitude": 41.797184,
            "longitude": 140.756831,
            "image_url": None,
            "wikipedia_url": "https://zh.wikipedia.org/wiki/%E4%BA%94%E7%A8%9C%E9%83%AD",
            "official_url": None,
            "journal_count": 0,
            "castle_number": None,
            "castle_series": "other",
        }
    ]
