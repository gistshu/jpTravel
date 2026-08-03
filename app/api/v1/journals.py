import json
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db_session
from app.core.exceptions import ValidationError
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.journal import (
    AccountJournalRead,
    AccountRankingRead,
    JournalActivityRead,
    JournalRead,
    JournalRecordRead,
)
from app.services.journal_image_service import build_journal_image_urls
from app.services.journal_service import JournalService

router = APIRouter(prefix="/me/journals", tags=["journals"])
public_router = APIRouter(prefix="/journals", tags=["journals"])


@public_router.get(
    "/latest",
    response_model=ApiResponse[list[JournalActivityRead]],
    status_code=status.HTTP_200_OK,
)
def list_latest_journal_updates(
    db_session: Annotated[Session, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=30)] = 20,
) -> ApiResponse[list[JournalActivityRead]]:
    """Return latest public journal update activities."""
    activities = JournalService(db_session).list_latest_updates(limit)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=activities,
        errors=[],
    )


@public_router.get(
    "/castles/{castle_id}/latest",
    response_model=ApiResponse[list[JournalRecordRead]],
    status_code=status.HTTP_200_OK,
)
def list_latest_castle_journals(
    castle_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[Session, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> ApiResponse[list[JournalRecordRead]]:
    """Return latest public journal records for one castle."""
    records = JournalService(db_session).list_latest_by_castle(castle_id, limit)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=records,
        errors=[],
    )


@public_router.get(
    "/accounts/rankings",
    response_model=ApiResponse[list[AccountRankingRead]],
    status_code=status.HTTP_200_OK,
)
def list_account_rankings(
    db_session: Annotated[Session, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=30)] = 30,
) -> ApiResponse[list[AccountRankingRead]]:
    """Return public account rankings by distinct visited castles."""
    rankings = JournalService(db_session).list_account_rankings(limit)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=rankings,
        errors=[],
    )


@public_router.get(
    "/accounts/{user_id}/journals",
    response_model=ApiResponse[list[AccountJournalRead]],
    status_code=status.HTTP_200_OK,
)
def list_account_journals(
    user_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[list[AccountJournalRead]]:
    """Return public visited journal records for one account."""
    records = JournalService(db_session).list_public_by_user(user_id)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=records,
        errors=[],
    )


@router.get(
    "",
    response_model=ApiResponse[list[JournalRead]],
    status_code=status.HTTP_200_OK,
)
def list_my_journals(
    current_user: Annotated[User, Depends(get_current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[list[JournalRead]]:
    """Return current user's castle journals."""
    journals = JournalService(db_session).list_my_journals(current_user)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=journals,
        errors=[],
    )


@router.put(
    "/{castle_id}",
    response_model=ApiResponse[JournalRead],
    status_code=status.HTTP_200_OK,
)
async def update_my_journal(
    castle_id: Annotated[int, Path(ge=1)],
    visited: Annotated[bool, Form()],
    travel_date: Annotated[date, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
    journal_text: Annotated[str, Form(max_length=5000)] = "",
    existing_image_urls: Annotated[str, Form()] = "[]",
    images: Annotated[list[UploadFile] | None, File()] = None,
) -> ApiResponse[JournalRead]:
    """Update current user's journal for one castle."""
    try:
        parsed_existing_urls = json.loads(existing_image_urls)
    except json.JSONDecodeError as exc:
        raise ValidationError("圖片資料格式錯誤") from exc
    if not isinstance(parsed_existing_urls, list) or not all(
        isinstance(item, str) for item in parsed_existing_urls
    ):
        raise ValidationError("圖片資料格式錯誤")

    image_urls = await build_journal_image_urls(parsed_existing_urls, images or [])
    journal = JournalService(db_session).update_my_journal(
        user=current_user,
        castle_id=castle_id,
        visited=visited,
        travel_date=travel_date,
        journal_text=journal_text,
        image_urls=image_urls,
    )
    return ApiResponse(
        success=True,
        message="儲存成功",
        data=journal,
        errors=[],
    )
