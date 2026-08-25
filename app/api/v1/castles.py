from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.castle import CastleRead, NearbyPlaceRead
from app.schemas.common import ApiResponse
from app.services.castle_service import CastleService
from app.services.nearby_place_service import NearbyPlaceService

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


@router.get(
    "/nearby-pois",
    response_model=ApiResponse[list[NearbyPlaceRead]],
    status_code=status.HTTP_200_OK,
)
async def list_nearby_pois_by_coordinate(
    db_session: Annotated[Session, Depends(get_db_session)],
    latitude: Annotated[float, Query(alias="lat", ge=-90, le=90)],
    longitude: Annotated[float, Query(alias="lon", ge=-180, le=180)],
    radius_meters: Annotated[int, Query(alias="radius_m", ge=5, le=3000)] = 300,
) -> ApiResponse[list[NearbyPlaceRead]]:
    """Return OpenStreetMap POIs near a coordinate."""
    places = await NearbyPlaceService(db_session).list_nearby_places_by_coordinate(
        latitude,
        longitude,
        radius_meters,
    )
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=places,
        errors=[],
    )


@router.get(
    "/{castle_id}/nearby-pois",
    response_model=ApiResponse[list[NearbyPlaceRead]],
    status_code=status.HTTP_200_OK,
)
async def list_nearby_pois(
    castle_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[Session, Depends(get_db_session)],
    radius_meters: Annotated[int, Query(alias="radius_m", ge=5, le=3000)] = 1500,
) -> ApiResponse[list[NearbyPlaceRead]]:
    """Return OpenStreetMap POIs near one castle."""
    places = await NearbyPlaceService(db_session).list_nearby_places(
        castle_id,
        radius_meters,
    )
    return ApiResponse(
        success=True,
        message="查詢成功",
        data=places,
        errors=[],
    )
