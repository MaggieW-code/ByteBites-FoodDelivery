import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from filelock import FileLock, Timeout

from backend.app.models.order_model import Order, OrderItem
from backend.app.repositories.order_repository import (
    DuplicateOrderError,
    OrderDataError,
    OrderDataMalformedError,
    OrderRepository,
)


def make_order(
    order_id="order_001",
    customer_id="customer_001",
):
    item = OrderItem(
        item_id="item_001",
        name="Burger",
        quantity=2,
        unit_price=Decimal("12.50"),
        line_total=Decimal("25.00"),
    )

    return Order(
        order_id=order_id,
        customer_id=customer_id,
        restaurant_id="restaurant_001",
        items=[item],
        total=Decimal("25.00"),
    )


def test_save_order(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    order = make_order()

    result = repo.save(order)

    assert result == order
    assert repo.get_all() == [order]


def test_get_order_by_id(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    repo.save(make_order())

    result = repo.get_by_id("order_001")

    assert result is not None
    assert result.order_id == "order_001"


def test_missing_order_returns_none(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")

    assert repo.get_by_id("missing") is None


def test_get_orders_by_customer(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")

    repo.save(make_order("order_001", "customer_001"))
    repo.save(make_order("order_002", "customer_002"))
    repo.save(make_order("order_003", "customer_001"))

    result = repo.get_by_customer_id("customer_001")

    assert len(result) == 2
    assert {order.order_id for order in result} == {
        "order_001",
        "order_003",
    }


def test_duplicate_order_id_rejected(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    repo.save(make_order())

    with pytest.raises(DuplicateOrderError):
        repo.save(make_order())


def test_orders_survive_repository_restart(tmp_path):
    path = tmp_path / "orders.json"

    first_repo = OrderRepository(path)
    original = make_order()
    first_repo.save(original)

    second_repo = OrderRepository(path)
    restored = second_repo.get_by_id("order_001")

    assert restored == original
    assert restored.total == Decimal("25.00")


def test_invalid_json_rejected(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text("{invalid json", encoding="utf-8")

    repo = OrderRepository(path)

    with pytest.raises(OrderDataMalformedError):
        repo.get_all()


def test_non_list_json_rejected(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text(
        json.dumps({"order_id": "order_001"}),
        encoding="utf-8",
    )

    repo = OrderRepository(path)

    with pytest.raises(OrderDataError):
        repo.get_all()


def test_invalid_stored_order_rejected(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text(
        json.dumps([{"order_id": "incomplete"}]),
        encoding="utf-8",
    )

    repo = OrderRepository(path)

    with pytest.raises(OrderDataError):
        repo.get_all()


def test_new_order_preserves_existing_orders(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")

    first = make_order("order_001")
    second = make_order("order_002")

    repo.save(first)
    repo.save(second)

    assert repo.get_all() == [first, second]


def test_failed_write_preserves_existing_orders(tmp_path, monkeypatch):
    import backend.app.repositories.order_repository as module

    path = tmp_path / "orders.json"
    repo = OrderRepository(path)
    first = make_order("order_001")
    repo.save(first)

    original_contents = path.read_text(encoding="utf-8")

    def fail_replace(source, destination):
        raise OSError("Simulated persistence failure")

    monkeypatch.setattr(module.os, "replace", fail_replace)

    with pytest.raises(OSError):
        repo.save(make_order("order_002"))

    assert path.read_text(encoding="utf-8") == original_contents
    assert repo.get_all() == [first]


@pytest.mark.parametrize("second_id", ["order_002", "order_001"])
def test_concurrent_saves_preserve_orders_and_reject_duplicate_ids(tmp_path, second_id):
    path = tmp_path / "orders.json"
    start = Barrier(2)

    def save(order_id):
        repo = OrderRepository(path)
        start.wait(timeout=5)
        return repo.save(make_order(order_id))

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(save, "order_001"),
            executor.submit(save, second_id),
        ]

    saved = [future.result() for future in futures if future.exception() is None]
    failures = [future.exception() for future in futures if future.exception() is not None]
    assert {order.order_id for order in saved} == {"order_001", second_id}
    assert len(saved) == len({"order_001", second_id})
    assert len(failures) == 2 - len(saved)
    assert all(isinstance(error, DuplicateOrderError) for error in failures)
    assert sorted(OrderRepository(path).get_all(), key=lambda order: order.order_id) == sorted(
        saved, key=lambda order: order.order_id
    )


def test_save_holds_file_lock_while_reading_and_writing(tmp_path, monkeypatch):
    path = tmp_path / "orders.json"
    repo = OrderRepository(path)
    competing_lock = FileLock(path.with_suffix(".json.lock"), timeout=0)
    read = repo.get_all
    write = repo._write

    def read_while_locked():
        with pytest.raises(Timeout):
            competing_lock.acquire()
        return read()

    def write_while_locked(path, records):
        with pytest.raises(Timeout):
            competing_lock.acquire()
        write(path, records)

    monkeypatch.setattr(repo, "get_all", read_while_locked)
    monkeypatch.setattr(repo, "_write", write_while_locked)
    repo.save(make_order())

    with competing_lock:
        assert len(read()) == 1


def test_mutated_order_is_rejected_without_changing_storage(tmp_path):
    path = tmp_path / "orders.json"
    repo = OrderRepository(path)
    original = repo.save(make_order())
    before = path.read_bytes()
    invalid = make_order("order_002")
    invalid.items[0].quantity += 1

    with pytest.raises(OrderDataError, match="Cannot save an invalid order"):
        repo.save(invalid)

    assert path.read_bytes() == before
    assert repo.get_all() == [original]


def test_invalid_utf8_is_reported_as_malformed_storage(tmp_path):
    path = tmp_path / "orders.json"
    path.write_bytes(b"\xff")

    with pytest.raises(OrderDataMalformedError):
        OrderRepository(path).get_all()
