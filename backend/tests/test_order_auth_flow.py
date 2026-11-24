import json

from fastapi.testclient import TestClient

from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.password_hashing import hash_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD
from backend.tests.test_order_repository import make_order
from main import app


def test_signed_in_customer_only_sees_owned_orders(tmp_path, monkeypatch):
    accounts_path = tmp_path / "accounts.json"
    orders_path = tmp_path / "orders.json"
    accounts_path.write_text(
        json.dumps(
            [
                {
                    "id": "cust_001",
                    "full_name": "Order Customer",
                    "email": "orders@example.com",
                    "phone": "250-555-0100",
                    "role": "customer",
                    "is_active": True,
                    "password_hash": hash_password(TEST_PASSWORD),
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ACCOUNTS_PATH", str(accounts_path))
    monkeypatch.setenv("SESSIONS_PATH", str(tmp_path / "sessions.json"))
    monkeypatch.setenv("ORDERS_PATH", str(orders_path))
    repository = OrderRepository(orders_path)
    owned = repository.save(make_order("order_001", "cust_001"))
    repository.save(make_order("order_002", "cust_002"))

    with TestClient(app) as client:
        sign_in = client.post("/auth/sign-in", json={"email": "orders@example.com", "password": TEST_PASSWORD})
        assert sign_in.status_code == 200
        headers = {"Authorization": f"Bearer {sign_in.json()['access_token']}"}

        assert client.get("/orders/order_001", headers=headers).json() == owned.model_dump(mode="json")
        assert client.get("/customers/cust_001/orders", headers=headers).json() == [owned.model_dump(mode="json")]
        assert client.get("/orders/order_002", headers=headers).status_code == 404
        assert client.get("/customers/cust_002/orders", headers=headers).status_code == 403

        assert client.post("/auth/sign-out", headers=headers).status_code == 204
        assert client.get("/orders/order_001", headers=headers).status_code == 401
