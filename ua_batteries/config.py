"""Configuration and constants for UA Batteries."""
import os
from datetime import datetime, timedelta

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

REQUEST_DAY = (datetime.today() + timedelta(days=1)).strftime(
    "%m.%Y"
)  # At the end of the month we already need to start downloading next month's prices.

REQUIRED_ENV = ["MAX_BUYS", "MAX_SELLS", "CAPACITY", "POWER"]


def validate_required_env() -> None:
    missing = [var for var in REQUIRED_ENV if not os.getenv(var)]

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

validate_required_env()

MAX_BUYS = int(os.getenv("MAX_BUYS", "10"))
MAX_SELLS = int(os.getenv("MAX_SELLS", "10"))
CAPACITY = int(os.getenv("CAPACITY", "100"))
POWER = int(os.getenv("POWER", "50"))

# ADD POSSIBILITY TO CRAWL WEB FOR OTHER MONTHS - IT'S SIMPLE JUST CHANGE TIME IN PAYLOAD FROM 02.2026 TO ANYTHING ELSE.