from pathlib import Path

import pytest

from backend.app.config import get_restaurant_data_path, path


def test_default_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RESTAURANT_TRIAL_PATH", raising=False)

    result = get_restaurant_data_path()

    assert result == path


def test_env_var_overrides_default_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESTAURANT_TRIAL_PATH", "/tmp/custom_restaurants.json")

    result = get_restaurant_data_path()

    assert result == Path("/tmp/custom_restaurants.json")
