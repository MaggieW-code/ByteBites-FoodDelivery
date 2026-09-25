from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_restaurant_endpoint() -> None:
    response = client.get("/restaurants")

    assert response.status_code == 200
