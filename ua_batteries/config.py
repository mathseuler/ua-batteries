"""Configuration and constants for UA Batteries."""

import os

URL = "https://www.oree.com.ua/index.php/pricectr/data_view"
HEADERS = {
    "Ukrainian": {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.oree.com.ua/index.php/pricectr?lang=ukr",
    },
    "English": {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.oree.com.ua/index.php/pricectr?lang=english",
    },
}
SAVE_FOLDER = "file_downloads"
MARKET = "DAM"
ZONE = "IPS"

REQUEST_DAY = "03.2025"

REQUIRED_ENV = ["MAX_BUYS", "MAX_SELLS", "CAPACITY", "POWER"]


def _get_env_float(name: str, default: str) -> float:
    """Parse a float from environment variables."""
    raw_value = os.getenv(name, default)
    try:
        value = float(raw_value)
    except ValueError as e:
        raise RuntimeError(f"Environment variable {name} must be a valid number, got: {raw_value}") from e
    return value


def validate_required_env() -> None:
    """Validate that all required environment variables are set.

    Raises
    ------
        RuntimeError: If any variables defined in REQUIRED_ENV are missing
            from the system environment.

    """
    missing = [var for var in REQUIRED_ENV if not os.getenv(var)]

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def validate_config_values() -> None:
    """Validate config-level numeric values loaded from environment."""
    if MAX_BUYS < 0:
        raise RuntimeError("MAX_BUYS must be non-negative")
    if MAX_SELLS < 0:
        raise RuntimeError("MAX_SELLS must be non-negative")
    if CAPACITY <= 0:
        raise RuntimeError("CAPACITY must be greater than 0")
    if POWER <= 0:
        raise RuntimeError("POWER must be greater than 0")


# validate_required_env()

MAX_BUYS = float(os.getenv("MAX_BUYS", "10"))
MAX_SELLS = float(os.getenv("MAX_SELLS", "10"))
CAPACITY = float(os.getenv("CAPACITY", "100"))
POWER = float(os.getenv("POWER", "50"))

validate_config_values()
