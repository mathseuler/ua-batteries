"""File download and parsing utilities."""

import os
from datetime import datetime
from io import StringIO

import certifi
import pandas as pd
import requests
from bs4 import BeautifulSoup

from ua_batteries.config import HEADERS, MARKET, REQUEST_DAY, SAVE_FOLDER, URL, ZONE


def get_file(month_year=REQUEST_DAY, market=MARKET, zone=ZONE, lang="Ukrainian"):
    """Get latest available file from OREE website.

    OREE: https://www.oree.com.ua/index.php/pricectr?lang=ukr
    Change lang to 'English' for English file.
    """
    payload = {
        "date": month_year,
        "market": market,
        "zone": zone,
    }  # month_year is of form %m.%Y i.e. 02.2026 - you can change it to be any month / year. 01.2026 will produce January 2026, for example.  # noqa: E501

    if lang not in HEADERS:
        raise ValueError(f"Unsupported language: {lang}. Expected one of: {list(HEADERS)}")

    try:
        response = requests.post(
            URL,
            data=payload,
            headers=HEADERS[lang],
            timeout=10,
            verify=certifi.where(),
        )
        response.raise_for_status()
    except requests.exceptions.SSLError as e:
        raise RuntimeError("SSL verification failed. Check certificates.") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP Error occurred: {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise RuntimeError("Invalid API response: response body is not a valid JSON") from e
    # JSON Validation
    if not isinstance(data, dict):
        raise RuntimeError("Invalid API response: expected JSON object")

    if "content" not in data:
        raise RuntimeError("Invalid API response: missing 'content'")

    html_table = data["content"]

    # HTML Validation
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")

    if table is None:
        raise RuntimeError("Invalid API response: no table found in HTML")

    # DataFrame parsing
    df = pd.read_html(StringIO(str(table)))[0]
    if "Дата" not in df.columns:
        raise RuntimeError("Invalid data: missing 'Дата' column")

    # DataFrame Validation
    expected_hours = [str(i) for i in range(1, 25)]

    missing_hours = [h for h in expected_hours if h not in df.columns]
    if missing_hours:
        raise RuntimeError(f"Invalid data: missing hour columns: {missing_hours}")

    if df.empty:
        raise RuntimeError("Invalid data: empty dataframe")

    if df[expected_hours].isnull().any().any():
        df[expected_hours] = df[expected_hours].ffill(axis=1)  # Accounting for Daylight Savings months (hour transitions lose an hour)

    df = df.set_index("Дата")

    return df


def download_file(month_year=REQUEST_DAY):
    """Download and save prices to CSV file."""
    df = get_file(month_year=month_year)

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    create_file_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{create_file_time}_oree_prices_{month_year.replace('.', '_')}.csv"
    filepath = os.path.join(SAVE_FOLDER, filename)

    df.to_csv(filepath, index_label="Дата")

    print(f"Saved to {filepath}")

    return df


if __name__ == "__main__":
    download_file()
