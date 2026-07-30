import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ExternalServiceError

GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleAuthService:
    """Service for Google OAuth login."""

    def is_enabled(self) -> bool:
        """Return whether Google login has required settings."""
        return bool(settings.google_client_id and settings.google_client_secret)

    def build_authorization_url(self) -> tuple[str, str]:
        """Build Google authorization URL and CSRF state."""
        if not self.is_enabled():
            raise AuthenticationError("Google 登入尚未設定")

        state = secrets.token_urlsafe(32)
        query = urlencode(
            {
                "client_id": settings.google_client_id,
                "redirect_uri": settings.google_redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "online",
                "prompt": "select_account",
            }
        )
        return f"{GOOGLE_AUTHORIZATION_URL}?{query}", state

    async def fetch_userinfo(self, code: str) -> dict[str, str]:
        """Exchange OAuth code for Google user information."""
        if not self.is_enabled():
            raise AuthenticationError("Google 登入尚未設定")

        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code != 200:
                raise ExternalServiceError("Google 登入驗證失敗")

            access_token = token_response.json().get("access_token")
            if not isinstance(access_token, str):
                raise ExternalServiceError("Google 登入驗證失敗")

            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_response.status_code != 200:
                raise ExternalServiceError("Google 使用者資料取得失敗")

        userinfo = userinfo_response.json()
        google_sub = userinfo.get("sub")
        email = userinfo.get("email")
        if not isinstance(google_sub, str) or not isinstance(email, str):
            raise ExternalServiceError("Google 使用者資料格式錯誤")

        return {
            "google_sub": google_sub,
            "email": email,
            "display_name": str(userinfo.get("name") or email),
            "avatar_url": str(userinfo.get("picture") or ""),
        }
