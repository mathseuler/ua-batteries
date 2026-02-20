"""Tests for visualization functionality."""
import pandas as pd
import os
from ua_batteries.visualization import (
    create_optimization_visualization,
    export_to_html,
    display_visualization,
)


class TestCreateOptimizationVisualization:
    """Test create_optimization_visualization function."""

    def test_output_is_dataframe(self):
        """Test that output is a pandas DataFrame."""
        # Create mock optimized dataframe
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(2)] for i in range(1, 25)},
            index=["2026-02-01", "2026-02-02"],
        )

        # Add optimization columns
        df["Buy_hours"] = [{}, {}]
        df["Sell_hours"] = [{}, {}]
        df["Total_profit"] = [100.0, 200.0]

        result = create_optimization_visualization(df, method="dp")

        assert isinstance(result, pd.DataFrame)

    def test_visualization_has_hours_columns(self):
        """Test that visualization dataframe has hour columns."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        df["Buy_hours"] = [{}]
        df["Sell_hours"] = [{}]
        df["Total_profit"] = [0.0]

        result = create_optimization_visualization(df)

        # Check for hour columns
        hour_columns = [col for col in result.columns if "Hour" in col]
        assert len(hour_columns) == 24

    def test_visualization_has_profit_column(self):
        """Test that visualization includes Total Profit column."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        df["Buy_hours"] = [{}]
        df["Sell_hours"] = [{}]
        df["Total_profit"] = [150.0]

        result = create_optimization_visualization(df)

        assert "Total Profit" in result.columns
        assert result.iloc[0]["Total Profit"] == 150.0

    def test_visualization_marks_buy_hours(self):
        """Test that buy hours are properly marked."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        buy_info = {
            1: {
                "hour": 5,
                "buy_amount": 50.0,
                "current_capacity": 0,
                "new_capacity": 50,
                "total_price": 500.0,
            }
        }

        df["Buy_hours"] = [buy_info]
        df["Sell_hours"] = [{}]
        df["Total_profit"] = [0.0]

        result = create_optimization_visualization(df)

        # Hour 6 (index 5) should have BUY marker
        hour_6_cell = result.iloc[0]["Hour 6"]
        assert "BUY" in str(hour_6_cell)

    def test_visualization_marks_sell_hours(self):
        """Test that sell hours are properly marked."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        sell_info = {
            1: {
                "hour": 10,
                "sell_amount": 50.0,
                "current_capacity": 50,
                "new_capacity": 0,
                "total_price": 600.0,
            }
        }

        df["Buy_hours"] = [{}]
        df["Sell_hours"] = [sell_info]
        df["Total_profit"] = [100.0]

        result = create_optimization_visualization(df)

        # Hour 11 (index 10) should have SELL marker
        hour_11_cell = result.iloc[0]["Hour 11"]
        assert "SELL" in str(hour_11_cell)


class TestExportToHTML:
    """Test export_to_html function."""

    def test_html_file_created(self):
        """Test that HTML file is created."""
        viz_df = pd.DataFrame(
            {f"Hour {i}": [""] for i in range(1, 25)}, index=["2026-02-01"]
        )
        viz_df["Total Profit"] = [100.0]

        original_df = pd.DataFrame(
            {str(i): [10.0] for i in range(1, 25)}, index=["2026-02-01"]
        )

        html_path = export_to_html(viz_df, original_df, open_browser=False)

        assert os.path.exists(html_path)
        assert html_path.endswith(".html")

    def test_html_contains_content(self):
        """Test that generated HTML has expected content."""
        viz_df = pd.DataFrame(
            {f"Hour {i}": [""] for i in range(1, 25)}, index=["2026-02-01"]
        )
        viz_df["Total Profit"] = [100.0]

        original_df = pd.DataFrame(
            {str(i): [10.0] for i in range(1, 25)}, index=["2026-02-01"]
        )

        html_path = export_to_html(
            viz_df, original_df, title="Test Visualization", open_browser=False
        )

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Test Visualization" in content
        assert "Hour 1" in content
        assert "100.00" in content
        assert "<table>" in content

    def test_html_has_buy_sell_styling(self):
        """Test that HTML includes buy/sell styling."""
        viz_df = pd.DataFrame(
            {f"Hour {i}": [""] for i in range(1, 25)}, index=["2026-02-01"]
        )
        viz_df.loc["2026-02-01", "Hour 6"] = "BUY\n50"
        viz_df.loc["2026-02-01", "Hour 11"] = "SELL\n50"
        viz_df["Total Profit"] = [100.0]

        original_df = pd.DataFrame(
            {str(i): [10.0] for i in range(1, 25)}, index=["2026-02-01"]
        )

        html_path = export_to_html(viz_df, original_df, open_browser=False)

        with open(html_path, "r") as f:
            content = f.read()

        assert "buy" in content.lower()
        assert "sell" in content.lower()
        assert "#90EE90" in content or "green" in content.lower()  # Buy color
        assert "#FFB6C1" in content or "sell" in content.lower()  # Sell color


class TestDisplayVisualization:
    """Test display_visualization function."""

    def test_returns_dataframe(self):
        """Test that display_visualization returns dataframe."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        result = display_visualization(df, method="dp")

        assert isinstance(result, pd.DataFrame)

    def test_contains_profit_column(self):
        """Test that result contains profit column."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(1)] for i in range(1, 25)},
            index=["2026-02-01"],
        )

        result = display_visualization(df)

        assert "Total Profit" in result.columns
