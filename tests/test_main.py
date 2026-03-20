"""Tests for optimization algorithms."""

import pandas as pd
import pytest

from ua_batteries.main import (
    add_optimization_to_dataframe,
    optimize_day_lp,
)


class TestAddOptimizationToDf:
    """Test adding optimization to dataframe."""

    def test_output_columns_exist(self):
        """Test that output dataframe has required columns."""
        df = pd.DataFrame(
            {str(i): [5.0 for _ in range(3)] for i in range(1, 25)},
            index=["2026-02-01", "2026-02-02", "2026-02-03"],
        )

        result = add_optimization_to_dataframe(df, max_buys=2, max_sells=2, capacity=100, power=50)

        assert "Buy_hours" in result.columns
        assert "Sell_hours" in result.columns
        assert "Total_profit" in result.columns

    def test_dataframe_length_preserved(self):
        """Test that output dataframe has same number of rows."""
        df = pd.DataFrame(
            {str(i): [5.0 for _ in range(5)] for i in range(1, 25)},
            index=[f"2026-02-{i:02d}" for i in range(1, 6)],
        )

        result = add_optimization_to_dataframe(df)

        assert len(result) == len(df)

    def test_profit_is_numeric(self):
        """Test that profit column contains numeric values."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(2)] for i in range(1, 25)},
            index=["2026-02-01", "2026-02-02"],
        )

        result = add_optimization_to_dataframe(df)

        assert result["Total_profit"].dtype in [float, int]


class TestOptimizeDayLP:
    """Test linear programming optimization function."""

    def test_lp_produces_results(self):
        """Test that LP approach produces valid results."""
        pytest.importorskip("pulp")

        prices = [
            5,
            10,
            15,
            20,
            10,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
        ]

        profit, buy_hours, sell_hours = optimize_day_lp(prices, max_buys=2, max_sells=2, capacity=100, power=100)

        assert isinstance(profit, (int, float))
        assert isinstance(buy_hours, dict)
        assert isinstance(sell_hours, dict)
