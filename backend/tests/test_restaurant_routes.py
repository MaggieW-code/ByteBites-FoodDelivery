from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_restaurant_endpoint() -> None:
    response = client.get("/restaurants")

    assert response.status_code == 200
