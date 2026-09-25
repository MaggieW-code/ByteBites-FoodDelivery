import os
from pathlib import Path

path = Path(__file__).parent/"data"/"restaurants.json"

def get_restaurant_data_path() -> Path:
    env_path = os.getenv("RESTAURANT_TRIAL_PATH")

    if env_path:
        try:
            result = Path(env_path)
        except ValueError as e:
            raise ValueError(f"RESTAURANT_TRIAL_PATH is not a valid path: {env_path}") from e
    else:
        result = path

    if result.exists() and result.is_dir():
        raise ValueError(f"Configured persistence path is a directory, not a file: {result}")

    return result