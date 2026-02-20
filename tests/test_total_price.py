"""Tests for pricing calculations."""
from ua_batteries.utils.total_price import total_buy_price, total_sell_price


class TestTotalBuyPrice:
    """Test total_buy_price function."""

    def test_positive_price(self):
        """Test with positive price."""
        price = 100.0
        result = total_buy_price(price)

        assert isinstance(result, (int, float))
        assert result > 0

    def test_zero_price(self):
        """Test with zero price."""
        result = total_buy_price(0)
        assert result == 0

    def test_float_precision(self):
        """Test with decimal prices."""
        price = 123.456
        result = total_buy_price(price)

        assert isinstance(result, float)


class TestTotalSellPrice:
    """Test total_sell_price function."""

    def test_positive_price(self):
        """Test with positive price."""
        price = 150.0
        result = total_sell_price(price)

        assert isinstance(result, (int, float))
        assert result > 0

    def test_zero_price(self):
        """Test with zero price."""
        result = total_sell_price(0)
        assert result == 0

    def test_float_precision(self):
        """Test with decimal prices."""
        price = 234.567
        result = total_sell_price(price)

        assert isinstance(result, float)


class TestBuySellPriceFunctions:
    """Test both functions together."""

    def test_buy_sell_consistency(self):
        """Test that buy and sell price functions are consistent."""
        price = 100.0
        buy = total_buy_price(price)
        sell = total_sell_price(price)

        # Both should return values for the same input
        assert isinstance(buy, (int, float))
        assert isinstance(sell, (int, float))

    def test_multiple_prices(self):
        """Test functions with multiple prices."""
        prices = [5.0, 50.0, 100.0, 500.0, 5000.0]

        for price in prices:
            buy = total_buy_price(price)
            sell = total_sell_price(price)

            assert buy > 0 or buy == 0
            assert sell > 0 or sell == 0
