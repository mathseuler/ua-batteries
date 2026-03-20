"""Price calculation utilities."""


def total_buy_price(price):
    """Calculate total buy price including commission."""
    return 1.05 * price


def total_sell_price(price):
    """Calculate total sell price minus commission."""
    return 0.95 * price
