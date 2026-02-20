"""Price calculation utilities."""


def total_buy_price(price):
    """Calculate total buy price including commission."""
    return price * 1.0066


def total_sell_price(price):
    """Calculate total sell price minus commission."""
    return price
