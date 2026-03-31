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


class TestOptimizeDayLPValidation:
    """Test validation and constrained trade sizing in optimize_day_lp."""

    def test_rejects_non_24_hour_price_list(self):
        """Test that optimize_day_lp requires exactly 24 hourly prices."""
        prices = [100.0] * 23

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices)

        assert "exactly 24 hourly values" in str(exc_info.value)

    def test_rejects_non_positive_capacity(self):
        """Test that optimize_day_lp rejects non-positive capacity."""
        prices = [100.0] * 24

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices, capacity=0, power=50)

        assert "capacity must be greater than 0" in str(exc_info.value)

    def test_rejects_non_positive_power(self):
        """Test that optimize_day_lp rejects non-positive power."""
        prices = [100.0] * 24

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices, capacity=100, power=0)

        assert "power must be greater than 0" in str(exc_info.value)

    def test_rejects_negative_max_buys(self):
        """Test that optimize_day_lp rejects negative max_buys."""
        prices = [100.0] * 24

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices, max_buys=-1)

        assert "max_buys must be non-negative" in str(exc_info.value)

    def test_rejects_negative_max_sells(self):
        """Test that optimize_day_lp rejects negative max_sells."""
        prices = [100.0] * 24

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices, max_sells=-1)

        assert "max_sells must be non-negative" in str(exc_info.value)

    def test_rejects_power_greater_than_capacity(self):
        """Test that optimize_day_lp rejects power greater than capacity."""
        prices = [100.0] * 24

        with pytest.raises(ValueError) as exc_info:
            optimize_day_lp(prices, capacity=40, power=50)

        assert "power must be less than or equal to capacity" in str(exc_info.value)

    def test_allows_remainder_buy_and_sell(self):
        """Test that the optimizer allows remainder trades to fill and empty storage."""
        prices = [100.0] * 24
        prices[2] = 10.0
        prices[3] = 11.0
        prices[4] = 12.0
        prices[20] = 200.0
        prices[21] = 190.0
        prices[22] = 180.0

        profit, buy_hours, sell_hours = optimize_day_lp(
            prices,
            max_buys=3,
            max_sells=3,
            capacity=120,
            power=50,
        )

        buy_amounts = [trade["buy_amount"] for trade in buy_hours.values()]
        sell_amounts = [trade["sell_amount"] for trade in sell_hours.values()]

        assert profit > 0
        assert buy_amounts == pytest.approx([50.0, 50.0, 20.0], abs=1e-6)
        assert sell_amounts == pytest.approx([50.0, 50.0, 20.0], abs=1e-6)

    def test_does_not_use_partial_buy_when_full_buy_is_feasible(self):
        """Test that the optimizer does not use a partial buy when a full buy is feasible."""
        prices = [100.0] * 24
        prices[2] = 10.0
        prices[20] = 200.0

        profit, buy_hours, sell_hours = optimize_day_lp(
            prices,
            max_buys=1,
            max_sells=1,
            capacity=120,
            power=50,
        )

        buy_amounts = [trade["buy_amount"] for trade in buy_hours.values()]
        sell_amounts = [trade["sell_amount"] for trade in sell_hours.values()]

        assert profit > 0
        assert len(buy_amounts) == 1
        assert len(sell_amounts) == 1
        assert buy_amounts == pytest.approx([50.0], abs=1e-6)
        assert sell_amounts == pytest.approx([50.0], abs=1e-6)
