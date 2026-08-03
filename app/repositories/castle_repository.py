from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.castle import Castle
from app.models.castle_journal import CastleJournal


class CastleRepository:
    """Repository for castle location persistence."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def list_all(self) -> list[Castle]:
        """Return all castles sorted by source order."""
        statement = select(Castle).order_by(Castle.id.asc())
        return list(self.db_session.scalars(statement).all())

    def get_by_id(self, castle_id: int) -> Castle | None:
        """Return a castle by primary key."""
        return self.db_session.get(Castle, castle_id)

    def get_journal_counts_by_castle(self) -> dict[int, int]:
        """Return journal counts grouped by castle id."""
        statement = (
            select(CastleJournal.castle_id, func.count(CastleJournal.id))
            .group_by(CastleJournal.castle_id)
        )
        return {
            castle_id: count
            for castle_id, count in self.db_session.execute(statement).all()
        }

    def upsert_many(self, castles: list[Castle]) -> int:
        """Insert or update castles by their source identity."""
        affected_count = 0
        for castle in castles:
            existing_castle = self._find_by_source(
                castle.source_url,
                castle.source_location_id,
            )
            if existing_castle is None:
                self.db_session.add(castle)
                affected_count += 1
                continue

            existing_castle.name = castle.name
            existing_castle.prefecture = castle.prefecture
            existing_castle.address = castle.address
            existing_castle.latitude = castle.latitude
            existing_castle.longitude = castle.longitude
            existing_castle.image_url = castle.image_url
            existing_castle.castle_number = castle.castle_number
            existing_castle.castle_series = castle.castle_series
            affected_count += 1
        return affected_count

    def _find_by_source(
        self,
        source_url: str,
        source_location_id: str,
    ) -> Castle | None:
        statement = select(Castle).where(
            Castle.source_url == source_url,
            Castle.source_location_id == source_location_id,
        )
        return self.db_session.scalars(statement).first()
