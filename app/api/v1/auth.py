from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth import SESSION_USER_ID_KEY, get_current_user_optional
from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.common import ApiResponse
from app.schemas.user import AuthStatus, UserRead
from app.services.google_auth_service import GoogleAuthService

router = APIRouter(prefix="/auth", tags=["auth"])
GOOGLE_OAUTH_STATE_KEY = "google_oauth_state"


@router.get("/me", response_model=ApiResponse[AuthStatus])
def get_me(
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
) -> ApiResponse[AuthStatus]:
    """Return current authentication status."""
    user_data = None
    if current_user is not None:
        user_data = UserRead(
            id=current_user.id,
            email=current_user.email,
            display_name=current_user.display_name,
            avatar_url=current_user.avatar_url,
        )

    return ApiResponse(
        success=True,
        message="查詢成功",
        data=AuthStatus(
            authenticated=current_user is not None,
            user=user_data,
            google_login_enabled=GoogleAuthService().is_enabled(),
        ),
        errors=[],
    )


@router.get("/google/login")
def login_google(request: Request) -> RedirectResponse:
    """Redirect user to Google OAuth."""
    authorization_url, state = GoogleAuthService().build_authorization_url()
    request.session[GOOGLE_OAUTH_STATE_KEY] = state
    return RedirectResponse(authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def callback_google(
    request: Request,
    db_session: Annotated[Session, Depends(get_db_session)],
    code: Annotated[str, Query(min_length=1)],
    state: Annotated[str, Query(min_length=1)],
) -> RedirectResponse:
    """Handle Google OAuth callback and create a local session."""
    expected_state = request.session.get(GOOGLE_OAUTH_STATE_KEY)
    if not isinstance(expected_state, str) or expected_state != state:
        raise AuthenticationError("Google 登入狀態驗證失敗")

    userinfo = await GoogleAuthService().fetch_userinfo(code)
    user = UserRepository(db_session).upsert_google_user(
        google_sub=userinfo["google_sub"],
        email=userinfo["email"],
        display_name=userinfo["display_name"],
        avatar_url=userinfo["avatar_url"] or None,
    )
    db_session.commit()
    request.session.pop(GOOGLE_OAUTH_STATE_KEY, None)
    request.session[SESSION_USER_ID_KEY] = user.id
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@router.post("/logout", response_model=ApiResponse[dict[str, bool]])
def logout(request: Request) -> ApiResponse[dict[str, bool]]:
    """Clear current user session."""
    request.session.clear()
    return ApiResponse(
        success=True,
        message="已登出",
        data={"logged_out": True},
        errors=[],
    )
