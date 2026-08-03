from pydantic import BaseModel, Field


class CastleRead(BaseModel):
    """Castle data returned by the API."""

    id: int
    name: str = Field(min_length=1, max_length=100)
    prefecture: str = Field(default="", max_length=32)
    address: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    image_url: str | None = Field(default=None, max_length=500)
    wikipedia_url: str = Field(min_length=1, max_length=500)
    official_url: str | None = Field(default=None, max_length=500)
    journal_count: int = Field(ge=0)
    castle_number: int | None = Field(default=None, ge=1, le=200)
    castle_series: str = Field(default="other", max_length=32)
