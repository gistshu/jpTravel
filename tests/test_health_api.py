from fastapi.testclient import TestClient

from app.main import create_app


def test_health_api_returns_success_response() -> None:
    """Health API should return the unified response format."""
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "查詢成功",
        "data": {"status": "ok"},
        "errors": [],
    }

