from fastapi import APIRouter, status

from app.schemas.common import ApiResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=ApiResponse[dict[str, str]],
    status_code=status.HTTP_200_OK,
)
def get_health() -> ApiResponse[dict[str, str]]:
    """Return API health status."""
    return ApiResponse(
        success=True,
        message="查詢成功",
        data={"status": "ok"},
        errors=[],
    )
