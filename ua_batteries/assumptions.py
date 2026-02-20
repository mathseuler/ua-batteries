ROZPODIL = 1856.16 # A part of the price of a one-time buy
PEREDACHA = 686.31 # A part of the price of a one-time buy
MARZHA = 0.05 # A markup of the listed price during a "buy" action

def total_price(price: float) -> float:
    """Calculates the total price of 1 MWh of energy after all costs are applied.
    
    Args:
        price (float): The base price of 1 MWh as listed.
    
    Returns:
        float: The total price per 1 MWh after all costs are added."""
    
    result = price * (1 + MARZHA) + ROZPODIL + PEREDACHA
    return result
