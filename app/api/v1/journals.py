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
    CastleJournalCollectionRead,
    JournalActivityRead,
    JournalRead,
    JournalRecordRead,
    JournalStatsRead,
)
from app.services.journal_image_service import (
    MAX_RECOMMENDATION_IMAGES,
    build_journal_image_urls,
)
from app.services.journal_service import JournalService

router = APIRouter(prefix="/me/journals", tags=["journals"])
public_router = APIRouter(prefix="/journals", tags=["journals"])


@public_router.get(
    "/stats",
    response_model=ApiResponse[JournalStatsRead],
    status_code=status.HTTP_200_OK,
)
def get_journal_stats(
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[JournalStatsRead]:
    """Return public aggregate journal statistics."""
    stats = JournalService(db_session).get_public_stats()
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=stats,
        errors=[],
    )


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
    "/castles/{castle_id}",
    response_model=ApiResponse[CastleJournalCollectionRead],
    status_code=status.HTTP_200_OK,
)
def list_castle_journals(
    castle_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[CastleJournalCollectionRead]:
    """Return one castle with all public journal records."""
    collection = JournalService(db_session).list_all_by_castle(castle_id)
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=collection,
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
    recommendations_json: Annotated[str, Form()] = "[]",
    recommendation_image_indexes: Annotated[list[int] | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
    recommendation_images: Annotated[list[UploadFile] | None, File()] = None,
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
    try:
        parsed_recommendations = json.loads(recommendations_json)
    except json.JSONDecodeError as exc:
        raise ValidationError("推薦資料格式錯誤") from exc
    if not isinstance(parsed_recommendations, list):
        raise ValidationError("推薦資料格式錯誤")
    recommendations = []
    for item in parsed_recommendations:
        if not isinstance(item, dict):
            raise ValidationError("推薦資料格式錯誤")
        recommendations.append(
            {
                "name": item.get("name"),
                "category": item.get("category"),
                "description": item.get("description"),
                "google_maps_url": item.get("google_maps_url"),
                "address": item.get("address"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "osm_type": item.get("osm_type"),
                "osm_id": item.get("osm_id"),
                "osm_url": item.get("osm_url"),
                "rating": item.get("rating"),
                "existing_image_urls": item.get("existing_image_urls"),
            },
        )

    image_urls = await build_journal_image_urls(parsed_existing_urls, images or [])
    recommendation_uploads_by_index: dict[int, list[UploadFile]] = {}
    recommendation_indexes = recommendation_image_indexes or []
    recommendation_uploads = recommendation_images or []
    if len(recommendation_indexes) != len(recommendation_uploads):
        raise ValidationError("推薦圖片資料格式錯誤")
    for index, upload in zip(
        recommendation_indexes,
        recommendation_uploads,
        strict=True,
    ):
        recommendation_uploads_by_index.setdefault(index, []).append(upload)
    for index, recommendation in enumerate(recommendations):
        existing_urls = recommendation.get("existing_image_urls")
        if not isinstance(existing_urls, list):
            existing_urls = []
        recommendation["image_urls"] = await build_journal_image_urls(
            [item for item in existing_urls if isinstance(item, str)],
            recommendation_uploads_by_index.get(index, []),
            max_images=MAX_RECOMMENDATION_IMAGES,
        )
    journal = JournalService(db_session).update_my_journal(
        user=current_user,
        castle_id=castle_id,
        visited=visited,
        travel_date=travel_date,
        journal_text=journal_text,
        image_urls=image_urls,
        recommendations=recommendations,
    )
    return ApiResponse(
        success=True,
        message="儲存成功",
        data=journal,
        errors=[],
    )
