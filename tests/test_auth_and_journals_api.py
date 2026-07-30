from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db_session
from app.main import create_app
from app.models.base import Base
from app.models.castle import Castle
from app.models.castle_journal import CastleJournal
from app.models.user import User
from app.repositories.journal_repository import JournalRepository


def test_auth_me_returns_anonymous_status() -> None:
    """Auth status should be anonymous before login."""
    client = TestClient(create_app())

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["authenticated"] is False
    assert payload["data"]["user"] is None


def test_update_journal_requires_login() -> None:
    """Journal updates should require an authenticated user."""
    client = TestClient(create_app())

    response = client.put(
        "/api/v1/me/journals/1",
        json={
            "visited": True,
            "travel_date": "2026-07-29",
            "journal_text": "第一次到訪。",
        },
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["message"] == "尚未登入"


def test_latest_journal_updates_returns_activity_list() -> None:
    """Latest journal update API should expose public activity metadata."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    user = User(
        google_sub="google-user-1",
        email="user@example.com",
        display_name="測試使用者",
    )
    castle = Castle(
        source_location_id="loc-1",
        name="大阪城",
        address="大阪市中央區大阪城1-1",
        latitude=34.687315,
        longitude=135.526201,
        source_url="https://example.com/source",
    )
    db_session.add_all([user, castle])
    db_session.flush()
    db_session.add(
        CastleJournal(
            user_id=user.id,
            castle_id=castle.id,
            visited=True,
            travel_date=date(2026, 7, 29),
            journal_text="今天去了大阪城。",
        )
    )
    db_session.commit()

    def override_db_session():
        try:
            yield db_session
        finally:
            pass

    application = create_app()
    application.dependency_overrides[get_db_session] = override_db_session
    client = TestClient(application)

    response = client.get("/api/v1/journals/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"][0]["castle_id"] == castle.id
    assert payload["data"][0]["user_display_name"] == "測試使用者"
    assert payload["data"][0]["castle_name"] == "大阪城"
    assert payload["data"][0]["travel_date"] == "2026-07-29"
    assert payload["data"][0]["journal_text"] == "今天去了大阪城。"
    assert isinstance(payload["data"][0]["updated_at"], str)
    db_session.close()


def test_account_rankings_count_distinct_visited_castles() -> None:
    """Account rankings should count distinct visited castles per account."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    user = User(
        google_sub="ranking-user-1",
        email="ranking-user@example.com",
        display_name="城攻旅人",
    )
    castles = [
        Castle(
            source_location_id=f"rank-loc-{index}",
            name=f"測試城{index}",
            address=f"測試地址{index}",
            latitude=35 + index,
            longitude=135 + index,
            source_url="https://example.com/source",
        )
        for index in range(3)
    ]
    db_session.add(user)
    db_session.add_all(castles)
    db_session.flush()
    db_session.add_all(
        [
            CastleJournal(
                user_id=user.id,
                castle_id=castles[0].id,
                visited=True,
                travel_date=date(2026, 7, 1),
                journal_text="第一次。",
            ),
            CastleJournal(
                user_id=user.id,
                castle_id=castles[0].id,
                visited=True,
                travel_date=date(2026, 7, 2),
                journal_text="第二次。",
            ),
            CastleJournal(
                user_id=user.id,
                castle_id=castles[1].id,
                visited=True,
                travel_date=date(2026, 7, 3),
                journal_text="另一座。",
            ),
            CastleJournal(
                user_id=user.id,
                castle_id=castles[2].id,
                visited=False,
                travel_date=date(2026, 7, 4),
                journal_text="未去過。",
            ),
        ],
    )
    db_session.commit()

    def override_db_session():
        try:
            yield db_session
        finally:
            pass

    application = create_app()
    application.dependency_overrides[get_db_session] = override_db_session
    client = TestClient(application)

    response = client.get("/api/v1/journals/accounts/rankings")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"][0]["rank"] == 1
    assert payload["data"][0]["user_id"] == user.id
    assert payload["data"][0]["user_display_name"] == "城攻旅人"
    assert payload["data"][0]["visited_castle_count"] == 2
    assert payload["data"][0]["title"] == "浪人"
    assert payload["data"][0]["title_level"] == 0
    db_session.close()


def test_account_journals_returns_public_visited_records() -> None:
    """Account journal API should expose visited records for one account."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    user = User(
        google_sub="account-map-user-1",
        email="account-map-user@example.com",
        display_name="公開大名",
    )
    castle = Castle(
        source_location_id="account-map-castle-1",
        name="弘前城",
        address="弘前市下白銀町1",
        latitude=40.607548,
        longitude=140.464413,
        source_url="https://example.com/source",
    )
    db_session.add_all([user, castle])
    db_session.flush()
    db_session.add_all(
        [
            CastleJournal(
                user_id=user.id,
                castle_id=castle.id,
                visited=True,
                travel_date=date(2026, 4, 20),
                journal_text="櫻花滿開。",
            ),
            CastleJournal(
                user_id=user.id,
                castle_id=castle.id,
                visited=False,
                travel_date=date(2026, 5, 20),
                journal_text="計畫中。",
            ),
        ],
    )
    db_session.commit()

    def override_db_session():
        try:
            yield db_session
        finally:
            pass

    application = create_app()
    application.dependency_overrides[get_db_session] = override_db_session
    client = TestClient(application)

    response = client.get(f"/api/v1/journals/accounts/{user.id}/journals")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) == 1
    assert payload["data"][0]["castle_id"] == castle.id
    assert payload["data"][0]["castle_name"] == "弘前城"
    assert payload["data"][0]["user_display_name"] == "公開大名"
    assert payload["data"][0]["travel_date"] == "2026-04-20"
    assert payload["data"][0]["journal_text"] == "櫻花滿開。"
    db_session.close()


def test_latest_castle_journals_returns_public_records() -> None:
    """Castle journal latest API should expose public journal records."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    user = User(
        google_sub="google-user-2",
        email="user2@example.com",
        display_name="另一位旅人",
    )
    castle = Castle(
        source_location_id="loc-2",
        name="姬路城",
        address="姬路市本町68",
        latitude=34.839449,
        longitude=134.693905,
        source_url="https://example.com/source",
    )
    db_session.add_all([user, castle])
    db_session.flush()
    db_session.add(
        CastleJournal(
            user_id=user.id,
            castle_id=castle.id,
            visited=True,
            travel_date=date(2026, 7, 20),
            journal_text="白色城牆非常漂亮。",
        )
    )
    db_session.commit()

    def override_db_session():
        try:
            yield db_session
        finally:
            pass

    application = create_app()
    application.dependency_overrides[get_db_session] = override_db_session
    client = TestClient(application)

    response = client.get(f"/api/v1/journals/castles/{castle.id}/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"][0]["user_display_name"] == "另一位旅人"
    assert payload["data"][0]["travel_date"] == "2026-07-20"
    assert payload["data"][0]["journal_text"] == "白色城牆非常漂亮。"
    db_session.close()


def test_journal_upsert_allows_multiple_travel_dates_per_castle() -> None:
    """Same user and castle should allow one journal per travel date."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()
    user = User(
        google_sub="google-user-3",
        email="user3@example.com",
        display_name="日期測試旅人",
    )
    castle = Castle(
        source_location_id="loc-3",
        name="大阪城",
        address="大阪市中央區大阪城1-1",
        latitude=34.687315,
        longitude=135.526201,
        source_url="https://example.com/source",
    )
    db_session.add_all([user, castle])
    db_session.flush()

    repository = JournalRepository(db_session)
    repository.upsert(user.id, castle.id, True, date(2026, 7, 20), "第一次。")
    repository.upsert(user.id, castle.id, True, date(2026, 7, 21), "第二天。")
    repository.upsert(user.id, castle.id, True, date(2026, 7, 20), "同日更新。")
    db_session.commit()

    journals = repository.list_by_user(user.id)

    assert len(journals) == 2
    assert sorted(journal.travel_date.isoformat() for journal in journals) == [
        "2026-07-20",
        "2026-07-21",
    ]
    assert repository.get_by_user_castle_and_date(
        user.id,
        castle.id,
        date(2026, 7, 20),
    ).journal_text == "同日更新。"
    db_session.close()
