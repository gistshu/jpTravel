from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for authenticated users."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_id(self, user_id: int) -> User | None:
        """Return a user by primary key."""
        return self.db_session.get(User, user_id)

    def get_by_google_sub(self, google_sub: str) -> User | None:
        """Return a user by Google subject id."""
        statement = select(User).where(User.google_sub == google_sub)
        return self.db_session.scalars(statement).first()

    def upsert_google_user(
        self,
        google_sub: str,
        email: str,
        display_name: str,
        avatar_url: str | None,
    ) -> User:
        """Create or update a user from Google profile data."""
        user = self.get_by_google_sub(google_sub)
        if user is None:
            user = User(
                google_sub=google_sub,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
            )
            self.db_session.add(user)
            self.db_session.flush()
            return user

        user.email = email
        user.display_name = display_name
        user.avatar_url = avatar_url
        return user
