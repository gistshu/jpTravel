from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.castle import CastleRead
from app.schemas.common import ApiResponse
from app.services.castle_service import CastleService

router = APIRouter(prefix="/castles", tags=["castles"])


@router.get(
    "",
    response_model=ApiResponse[list[CastleRead]],
    status_code=status.HTTP_200_OK,
)
def list_castles(
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[list[CastleRead]]:
    """Return all castle markers."""
    castles = CastleService(db_session).list_castles()
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=castles,
        errors=[],
    )
