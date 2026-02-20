"""File download and parsing utilities."""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

from ua_batteries.config import URL, HEADERS, SAVE_FOLDER, MARKET, ZONE, REQUEST_DAY


def get_file(month_year=REQUEST_DAY, market=MARKET, zone=ZONE, lang="Ukrainian"):
    """
    Get latest available file from OREE website.

    OREE: https://www.oree.com.ua/index.php/pricectr?lang=ukr
    Change lang to 'English' for English file.
    """
    payload = {"date": month_year, "market": market, "zone": zone}
    response = requests.post(URL, data=payload, headers=HEADERS[lang])

    if response.status_code != 200:
        print("Request failed:", response.status_code)
        raise Exception(f"Failed to fetch data: HTTP {response.status_code}")
    data = response.json()

    html_table = data["content"]
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")

    # pd.read_html() always returns a list since html can have multiple tables
    # Extract the dataframe with [0]
    df = pd.read_html(str(table))[0].set_index("Дата")
    return df


def download_file(month_year=REQUEST_DAY):
    """Download and save prices to CSV file."""
    df = get_file()

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    create_file_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{create_file_time}_oree_prices_{month_year.replace('.', '_')}.csv"
    filepath = os.path.join(SAVE_FOLDER, filename)

    df.to_csv(filepath, index=False)

    print(f"Saved to {filepath}")

    return df


if __name__ == "__main__":
    download_file()
