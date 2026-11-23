import os
from datetime import timedelta
from pathlib import Path

path = Path(__file__).parent / "data" / "restaurants.json"


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


DATA_DIRECTORY = Path(__file__).parent / "data"
DEFAULT_AUTH_TOKEN_TTL_MINUTES = 60


def get_data_file_path(variable: str, default_name: str) -> Path:
    configured = os.getenv(variable)
    result = Path(configured) if configured else DATA_DIRECTORY / default_name
    if result.is_dir():
        raise ValueError(f"{variable} points to a directory, not a file: {result}")
    return result


def get_accounts_data_path() -> Path:
    return get_data_file_path("ACCOUNTS_PATH", "accounts.json")


def get_sessions_data_path() -> Path:
    return get_data_file_path("SESSIONS_PATH", "sessions.json")


def get_auth_token_lifetime() -> timedelta:
    configured = os.getenv("AUTH_TOKEN_TTL_MINUTES", str(DEFAULT_AUTH_TOKEN_TTL_MINUTES))
    try:
        minutes = int(configured)
    except ValueError as error:
        raise ValueError(f"AUTH_TOKEN_TTL_MINUTES must be a whole number of minutes: {configured!r}") from error
    if minutes <= 0:
        raise ValueError(f"AUTH_TOKEN_TTL_MINUTES must be positive: {minutes}")
    return timedelta(minutes=minutes)
