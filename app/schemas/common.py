from pydantic import BaseModel, Field


class ErrorItem(BaseModel):
    """Structured API error item."""

    code: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=255)
    field: str | None = Field(default=None, max_length=128)


class ApiResponse[ResponseData](BaseModel):
    """Unified API response body."""

    success: bool
    message: str
    data: ResponseData | None = None
    errors: list[ErrorItem] = Field(default_factory=list)


class Pagination(BaseModel):
    """Pagination metadata for list API responses."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedItems[ResponseData](BaseModel):
    """Paginated list wrapper."""

    items: list[ResponseData]
    pagination: Pagination
