from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.castle import Castle
from app.models.castle_journal import CastleJournal
from app.models.journal_recommendation import JournalRecommendation
from app.models.user import User
from app.services.journal_image_service import dump_image_urls


class JournalRepository:
    """Repository for user castle journals."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def list_by_user(self, user_id: int) -> list[CastleJournal]:
        """Return all castle journals for a user."""
        statement = select(CastleJournal).where(CastleJournal.user_id == user_id)
        return list(self.db_session.scalars(statement).all())

    def get_by_user_castle_and_date(
        self,
        user_id: int,
        castle_id: int,
        travel_date: date,
    ) -> CastleJournal | None:
        """Return one castle journal for a user, castle, and travel date."""
        statement = select(CastleJournal).where(
            CastleJournal.user_id == user_id,
            CastleJournal.castle_id == castle_id,
            CastleJournal.travel_date == travel_date,
        )
        return self.db_session.scalars(statement).first()

    def upsert(
        self,
        user_id: int,
        castle_id: int,
        visited: bool,
        travel_date: date,
        journal_text: str,
        image_urls_json: str = "[]",
    ) -> CastleJournal:
        """Create or update one castle journal."""
        journal = self.get_by_user_castle_and_date(
            user_id,
            castle_id,
            travel_date,
        )
        if journal is None:
            journal = CastleJournal(
                user_id=user_id,
                castle_id=castle_id,
                visited=visited,
                travel_date=travel_date,
                journal_text=journal_text,
                image_urls_json=image_urls_json,
            )
            self.db_session.add(journal)
            self.db_session.flush()
            return journal

        journal.visited = visited
        journal.travel_date = travel_date
        journal.journal_text = journal_text
        journal.image_urls_json = image_urls_json
        return journal

    def replace_recommendations(
        self,
        journal: CastleJournal,
        recommendations: list[dict[str, object]],
    ) -> None:
        """Replace recommendations attached to a journal."""
        journal.recommendations.clear()
        self.db_session.flush()
        for index, recommendation in enumerate(recommendations):
            name = str(recommendation.get("name") or "").strip()
            if not name:
                continue
            journal.recommendations.append(
                JournalRecommendation(
                    journal_id=journal.id,
                    user_id=journal.user_id,
                    castle_id=journal.castle_id,
                    name=name,
                    category=str(recommendation.get("category") or "other").strip()
                    or "other",
                    description=str(recommendation.get("description") or "").strip(),
                    google_maps_url=(
                        str(recommendation.get("google_maps_url")).strip()
                        if recommendation.get("google_maps_url")
                        else None
                    ),
                    image_urls_json=dump_image_urls(
                        [
                            image_url
                            for image_url in recommendation.get("image_urls", [])
                            if isinstance(image_url, str)
                        ],
                    ),
                    address=(
                        str(recommendation.get("address")).strip()
                        if recommendation.get("address")
                        else None
                    ),
                    latitude=_to_float_or_none(recommendation.get("latitude")),
                    longitude=_to_float_or_none(recommendation.get("longitude")),
                    osm_type=(
                        str(recommendation.get("osm_type")).strip()
                        if recommendation.get("osm_type")
                        else None
                    ),
                    osm_id=(
                        str(recommendation.get("osm_id")).strip()
                        if recommendation.get("osm_id")
                        else None
                    ),
                    osm_url=(
                        str(recommendation.get("osm_url")).strip()
                        if recommendation.get("osm_url")
                        else None
                    ),
                    rating=_to_rating_or_none(recommendation.get("rating")),
                    sort_order=index,
                ),
            )

    def list_latest_updates(
        self,
        limit: int,
    ) -> list[tuple[CastleJournal, User, Castle]]:
        """Return latest public journal update activities."""
        statement = (
            select(CastleJournal, User, Castle)
            .join(User, CastleJournal.user_id == User.id)
            .join(Castle, CastleJournal.castle_id == Castle.id)
            .order_by(CastleJournal.updated_at.desc(), CastleJournal.id.desc())
            .limit(limit)
        )
        return list(self.db_session.execute(statement).all())

    def list_latest_by_castle(
        self,
        castle_id: int,
        limit: int,
    ) -> list[tuple[CastleJournal, User]]:
        """Return latest public journal records for one castle."""
        statement = (
            select(CastleJournal, User)
            .join(User, CastleJournal.user_id == User.id)
            .where(CastleJournal.castle_id == castle_id)
            .order_by(CastleJournal.updated_at.desc(), CastleJournal.id.desc())
            .limit(limit)
        )
        return list(self.db_session.execute(statement).all())

    def list_all_by_castle(self, castle_id: int) -> list[tuple[CastleJournal, User]]:
        """Return all public journal records for one castle."""
        statement = (
            select(CastleJournal, User)
            .join(User, CastleJournal.user_id == User.id)
            .where(CastleJournal.castle_id == castle_id)
            .order_by(CastleJournal.travel_date.desc(), CastleJournal.id.desc())
        )
        return list(self.db_session.execute(statement).all())

    def get_visited_castle_counts_by_user_ids(
        self,
        user_ids: set[int],
    ) -> dict[int, int]:
        """Return distinct visited castle counts for users."""
        if not user_ids:
            return {}

        visited_count = func.count(func.distinct(CastleJournal.castle_id)).label(
            "visited_count",
        )
        statement = (
            select(CastleJournal.user_id, visited_count)
            .where(
                CastleJournal.user_id.in_(user_ids),
                CastleJournal.visited.is_(True),
            )
            .group_by(CastleJournal.user_id)
        )
        return {
            user_id: visited_castle_count
            for user_id, visited_castle_count in self.db_session.execute(statement)
        }

    def list_account_rankings(self, limit: int) -> list[tuple[User, int]]:
        """Return users ranked by distinct visited castle count."""
        visited_count = func.count(func.distinct(CastleJournal.castle_id)).label(
            "visited_count",
        )
        statement = (
            select(User, visited_count)
            .join(CastleJournal, CastleJournal.user_id == User.id)
            .where(CastleJournal.visited.is_(True))
            .group_by(User.id)
            .order_by(visited_count.desc(), User.id.asc())
            .limit(limit)
        )
        return list(self.db_session.execute(statement).all())

    def get_public_stats(self) -> tuple[int, int]:
        """Return distinct journal user count and total journal count."""
        statement = select(
            func.count(func.distinct(CastleJournal.user_id)),
            func.count(CastleJournal.id),
        )
        user_count, journal_count = self.db_session.execute(statement).one()
        return int(user_count or 0), int(journal_count or 0)

    def list_public_by_user(self, user_id: int) -> list[CastleJournal]:
        """Return public visited journal records for one user."""
        statement = (
            select(CastleJournal)
            .where(
                CastleJournal.user_id == user_id,
                CastleJournal.visited.is_(True),
            )
            .order_by(CastleJournal.travel_date.desc(), CastleJournal.id.desc())
        )
        return list(self.db_session.scalars(statement).all())


def _to_float_or_none(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_rating_or_none(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    return rating if 1 <= rating <= 5 else None
