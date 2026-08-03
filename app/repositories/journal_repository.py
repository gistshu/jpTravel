from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.castle import Castle
from app.models.castle_journal import CastleJournal
from app.models.user import User


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
