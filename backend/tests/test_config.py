from pathlib import Path
import os
from backend.app.config import get_restaurant_data_path, path

def test_default_path():
    if "RESTAURANT_TRIAL_PATH" in os.environ:
        del os.environ["RESTAURANT_TRIAL_PATH"]

    result = get_restaurant_data_path()

    assert result == path

def test_env_var_overrides_default_path():
    os.environ["RESTAURANT_TRIAL_PATH"] = "/tmp/custom_restaurants.json"

    result = get_restaurant_data_path()
    assert result == Path("/tmp/custom_restaurants.json")
    del os.environ["RESTAURANT_TRIAL_PATH"]



