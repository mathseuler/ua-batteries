import pandas as pd
import numpy as np
import ast
import os
import re
from typing import List, Callable, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
import math
import webbrowser
from assumptions import total_price

def optimize_profit_low_level(
        prices: List[float],
        total_price: Callable[[float], float] = total_price,
        buy_step: int = 50,
        inventory_limit: int = 100,
        max_buy_sell_cycles: Optional[int] = None):
    """Will add the description later. High assumption scenario - inventory_limit is
    a multiple of buy_step.
    
    Args:
        prices (list): list of floats representing hourly prices.
        total_price (callable): function calculating total transaction price.
        buy_step (int): amount of MWh purchased at any given hour.
        inventory_limit (int): limit of energy that can be stored at once.
        max_buy_sell_cycles (int): maximum number of cycles to buy/sell per day.
    
    Returns:
        To be added later."""

    # ___validation part___

    # Validating that inventory_limit is a multiple of buy_step
    assert inventory_limit % buy_step == 0, "inventory_limit must be a limit of buy_step"

    T = len(prices)
    if T == 0:
        return ["Empty price series.", []]
    
    # We assume that only 1 action per hour is conducted, and at the end of
    # the day the inventory is flat. i.e. buys == sells.
    # Therefore, the maximum feasible number of buys is floor(T/2).
    # E.g. if T = 17 then at most 8 buys and 8 sells can be conducted.

    max_feasible_buys = T // 2
    if max_buy_sell_cycles is None or max_buy_sell_cycles > max_feasible_buys:
        max_buy_sell_cycles = max_feasible_buys
    
    if max_buy_sell_cycles < 0:
        raise ValueError("max_buy_sell_cycles cannot be negative")
    
    if inventory_limit == 0:
        raise ValueError("Inventory cannot be zero (inventory_limit = 0)")
    
    # ___the algorithm___

    


        
    