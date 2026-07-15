from fastapi.testclient import TestClient

from app.api.app import create_app


def test_health_check() -> None:
    application = create_app()

    with TestClient(application) as client:
        response = client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
    }