"""Pytest configuration and shared fixtures for ua_batteries tests."""

import pytest
import pandas as pd
import os

# Set environment variables for config before importing ua_batteries modules
# Using smaller values for tests to avoid timeout in DP algorithm
os.environ["MAX_BUYS"] = "3"
os.environ["MAX_SELLS"] = "3"
os.environ["CAPACITY"] = "200"
os.environ["POWER"] = "100"


@pytest.fixture
def sample_prices():
    """Fixture providing sample hourly prices for testing."""
    return [5, 10, 15, 20, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]


@pytest.fixture
def sample_dataframe():
    """Fixture providing a sample dataframe with 24 hours of prices."""
    return pd.DataFrame(
        {str(i): [10.0, 15.0, 20.0] for i in range(1, 25)},
        index=["2026-02-01", "2026-02-02", "2026-02-03"],
    )


@pytest.fixture
def optimized_sample_dataframe(sample_dataframe):
    """Fixture providing a dataframe with optimization columns added."""
    df = sample_dataframe.copy()
    df["Buy_hours"] = [{}, {}, {}]
    df["Sell_hours"] = [{}, {}, {}]
    df["Total_profit"] = [100.0, 150.0, 200.0]
    return df


@pytest.fixture
def mock_html_response():
    """Fixture providing a mock HTML response from the data source."""
    # Create HTML that will parse correctly with pandas.read_html()
    html = (
        """
    <html>
    <body>
    <table>
        <tr>
            <th>Дата</th>
    """
        + "".join([f"<th>{i}</th>" for i in range(1, 25)])
        + """
        </tr>
        <tr>
            <td>01.02.2026</td>
    """
        + "".join(["<td>1000.0</td>" for _ in range(24)])
        + """
        </tr>
    </table>
    </body>
    </html>
    """
    )
    return html
