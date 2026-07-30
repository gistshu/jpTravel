from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

SESSION_USER_ID_KEY = "user_id"


def get_current_user_optional(
    request: Request,
    db_session: Annotated[Session, Depends(get_db_session)],
) -> User | None:
    """Return the current session user when logged in."""
    user_id = request.session.get(SESSION_USER_ID_KEY)
    if not isinstance(user_id, int):
        return None
    return UserRepository(db_session).get_by_id(user_id)


def get_current_user(
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    """Return the current session user or raise 401."""
    if current_user is None:
        raise AuthenticationError("尚未登入")
    return current_user
