from datetime import date

from pydantic import BaseModel, Field


class JournalRecommendationRead(BaseModel):
    """User recommendation attached to one journal."""

    name: str
    category: str = "other"
    description: str = ""
    google_maps_url: str | None = None
    image_urls: list[str] = Field(default_factory=list)
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    osm_type: str | None = None
    osm_id: str | None = None
    osm_url: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)


class JournalRead(BaseModel):
    """User castle journal state."""

    castle_id: int
    visited: bool
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)
    recommendations: list[JournalRecommendationRead] = Field(default_factory=list)


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
    title: str | None = None
    title_level: int | None = None
    recommendations: list[JournalRecommendationRead] = Field(default_factory=list)


class CastleJournalCollectionRead(BaseModel):
    """Public journal collection for one castle."""

    castle_id: int
    castle_name: str
    prefecture: str = ""
    address: str
    image_url: str | None = None
    wikipedia_url: str
    official_url: str | None = None
    records: list[JournalRecordRead] = Field(default_factory=list)


class AccountJournalRead(BaseModel):
    """Public journal record for one ranked account."""

    castle_id: int
    castle_name: str
    user_display_name: str
    travel_date: date
    journal_text: str
    image_urls: list[str] = Field(default_factory=list)
    updated_at: str
    recommendations: list[JournalRecommendationRead] = Field(default_factory=list)


class AccountRankingRead(BaseModel):
    """Public account ranking by distinct visited castle count."""

    rank: int
    user_id: int
    user_display_name: str
    visited_castle_count: int
    title: str
    title_level: int


class JournalStatsRead(BaseModel):
    """Public aggregate journal statistics."""

    journal_user_count: int
    journal_count: int
