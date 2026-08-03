from datetime import date

from pydantic import BaseModel, Field


class JournalRead(BaseModel):
    """User castle journal state."""

    castle_id: int
    visited: bool
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)


class JournalActivityRead(BaseModel):
    """Public journal update activity."""

    castle_id: int
    user_display_name: str
    castle_name: str
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)
    updated_at: str


class JournalRecordRead(BaseModel):
    """Public castle journal record."""

    user_display_name: str
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)
    updated_at: str


class AccountJournalRead(BaseModel):
    """Public journal record for one ranked account."""

    castle_id: int
    castle_name: str
    user_display_name: str
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)
    updated_at: str


class AccountRankingRead(BaseModel):
    """Public account ranking by distinct visited castle count."""

    rank: int
    user_id: int
    user_display_name: str
    visited_castle_count: int
    title: str
    title_level: int
