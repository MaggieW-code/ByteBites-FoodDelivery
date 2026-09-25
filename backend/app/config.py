import os
from pathlib import Path

path = Path(__file__).parent/"data"/"restaurants.json"

def get_restaurant_data_path() -> Path:
    # check if there is default
    env_path = os.getenv("RESTAURANT_TRIAL_PATH")
    # if none then return the path we set, else return the default path
    if env_path: 
        return Path(env_path)
    return path