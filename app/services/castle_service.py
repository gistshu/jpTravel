from urllib.parse import quote

from sqlalchemy.orm import Session

from app.repositories.castle_repository import CastleRepository
from app.schemas.castle import CastleRead


class CastleService:
    """Service for castle map workflows."""

    def __init__(self, db_session: Session) -> None:
        self.repository = CastleRepository(db_session)

    def list_castles(self) -> list[CastleRead]:
        """Return castle markers for map rendering."""
        castles = self.repository.list_all()
        journal_counts = self.repository.get_journal_counts_by_castle()
        return [
            CastleRead(
                id=castle.id,
                name=castle.name,
                prefecture=castle.prefecture or "",
                address=castle.address,
                latitude=castle.latitude,
                longitude=castle.longitude,
                image_url=castle.image_url,
                wikipedia_url=_build_wikipedia_url(castle.name),
                official_url=_build_official_url(castle.source_url),
                journal_count=journal_counts.get(castle.id, 0),
                castle_number=castle.castle_number,
                castle_series=castle.castle_series,
            )
            for castle in castles
        ]


def _build_wikipedia_url(castle_name: str) -> str:
    return f"https://zh.wikipedia.org/wiki/{quote(castle_name)}"


def _build_official_url(source_url: str) -> str | None:
    if source_url.startswith("https://www.100finecastles.com/"):
        return source_url
    return None
