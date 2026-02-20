"""Tests for optimization algorithms."""
import pytest
import pandas as pd
from ua_batteries.main import (
    optimize_day_dp,
    optimize_day_lp,
    add_optimization_to_dataframe,
)


class TestOptimizeDayDP:
    """Test dynamic programming optimization function."""

    def test_simple_case_low_high_prices(self):
        """Test simple case: buy at low price, sell at high price."""
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

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=1, max_sells=1, capacity=100, power=100
        )

        # Should buy at lowest (5) and sell at highest (20)
        assert profit > 0
        assert len(buy_hours) == 1
        assert len(sell_hours) == 1
        assert buy_hours[1]["buy_amount"] > 0
        assert sell_hours[1]["sell_amount"] > 0

    def test_no_profit_opportunity(self):
        """Test when prices only go down (no buy profit)."""
        prices = [
            20,
            15,
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
            5,
            5,
        ]

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=1, max_sells=1, capacity=100, power=100
        )

        # Should not buy if prices only decrease
        assert profit == 0 or profit < 0

    def test_capacity_constraint(self):
        """Test that storage capacity is respected."""
        prices = [5] * 24
        capacity = 50
        power = 30

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=3, max_sells=3, capacity=capacity, power=power
        )

        # Check that we never exceed capacity
        current_capacity = 0
        for i in range(1, 25):
            for buy_info in buy_hours.values():
                if buy_info["hour"] == i - 1:
                    current_capacity += buy_info["buy_amount"]
                    assert current_capacity <= capacity

            for sell_info in sell_hours.values():
                if sell_info["hour"] == i - 1:
                    current_capacity -= sell_info["sell_amount"]
                    assert current_capacity >= 0

    def test_end_with_zero_capacity(self):
        """Test that we must end the day with zero capacity."""
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

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=5, max_sells=5, capacity=100, power=100
        )

        # Calculate final capacity
        final_capacity = 0
        for buy_info in buy_hours.values():
            final_capacity += buy_info["buy_amount"]
        for sell_info in sell_hours.values():
            final_capacity -= sell_info["sell_amount"]

        assert final_capacity == 0

    def test_max_buys_constraint(self):
        """Test that max_buys limit is respected."""
        prices = [
            5,
            20,
            5,
            20,
            5,
            20,
            5,
            20,
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
        max_buys = 2

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=max_buys, max_sells=5, capacity=100, power=100
        )

        assert len(buy_hours) <= max_buys

    def test_max_sells_constraint(self):
        """Test that max_sells limit is respected."""
        prices = [
            5,
            20,
            5,
            20,
            5,
            20,
            5,
            20,
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
        max_sells = 1

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=5, max_sells=max_sells, capacity=100, power=100
        )

        assert len(sell_hours) <= max_sells

    def test_cannot_buy_and_sell_same_hour(self):
        """Test that we cannot buy and sell in the same hour."""
        prices = [10] * 24

        profit, buy_hours, sell_hours = optimize_day_dp(
            prices, max_buys=3, max_sells=3, capacity=100, power=100
        )

        # Check no overlap in hours
        buy_hours_set = {info["hour"] for info in buy_hours.values()}
        sell_hours_set = {info["hour"] for info in sell_hours.values()}

        assert len(buy_hours_set & sell_hours_set) == 0


class TestAddOptimizationToDf:
    """Test adding optimization to dataframe."""

    def test_output_columns_exist(self):
        """Test that output dataframe has required columns."""
        df = pd.DataFrame(
            {str(i): [5.0 for _ in range(3)] for i in range(1, 25)},
            index=["2026-02-01", "2026-02-02", "2026-02-03"],
        )

        result = add_optimization_to_dataframe(
            df, method="dp", max_buys=2, max_sells=2, capacity=100, power=50
        )

        assert "Buy_hours" in result.columns
        assert "Sell_hours" in result.columns
        assert "Total_profit" in result.columns

    def test_dataframe_length_preserved(self):
        """Test that output dataframe has same number of rows."""
        df = pd.DataFrame(
            {str(i): [5.0 for _ in range(5)] for i in range(1, 25)},
            index=[f"2026-02-{i:02d}" for i in range(1, 6)],
        )

        result = add_optimization_to_dataframe(df, method="dp")

        assert len(result) == len(df)

    def test_profit_is_numeric(self):
        """Test that profit column contains numeric values."""
        df = pd.DataFrame(
            {str(i): [10.0 for _ in range(2)] for i in range(1, 25)},
            index=["2026-02-01", "2026-02-02"],
        )

        result = add_optimization_to_dataframe(df, method="dp")

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

        profit, buy_hours, sell_hours = optimize_day_lp(
            prices, max_buys=2, max_sells=2, capacity=100, power=100
        )

        assert isinstance(profit, (int, float))
        assert isinstance(buy_hours, dict)
        assert isinstance(sell_hours, dict)
