"""Database model package."""

from app.models.castle import Castle
from app.models.castle_journal import CastleJournal
from app.models.journal_recommendation import JournalRecommendation
from app.models.user import User

__all__ = ["Castle", "CastleJournal", "JournalRecommendation", "User"]
