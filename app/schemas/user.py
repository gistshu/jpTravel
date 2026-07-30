from pydantic import BaseModel, Field


class UserRead(BaseModel):
    """Authenticated user profile returned to the frontend."""

    id: int
    email: str = Field(min_length=3, max_length=255)
    display_name: str = Field(min_length=1, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)


class AuthStatus(BaseModel):
    """Current authentication state."""

    authenticated: bool
    user: UserRead | None = None
    google_login_enabled: bool
