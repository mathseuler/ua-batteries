"""Optimization algorithms for energy trading strategy."""

from ua_batteries.config import CAPACITY, MAX_BUYS, MAX_SELLS, POWER
from ua_batteries.utils.get_file import get_file
from ua_batteries.utils.total_price import total_buy_price, total_sell_price


def _validate_optimization_inputs(prices, max_buys, max_sells, capacity, power):
    """Validate optimization inputs before solving."""
    if len(prices) != 24:
        raise ValueError("prices must contain exactly 24 hourly values")

    if max_buys < 0:
        raise ValueError("max_buys must be non-negative")

    if max_sells < 0:
        raise ValueError("max_sells must be non-negative")

    if capacity <= 0:
        raise ValueError("capacity must be greater than 0")

    if power <= 0:
        raise ValueError("power must be greater than 0")

    if power > capacity:
        raise ValueError("power must be less than or equal to capacity")


def optimize_day_lp(prices, max_buys=MAX_BUYS, max_sells=MAX_SELLS, capacity=CAPACITY, power=POWER):
    """Optimize buy/sell strategy for a single day using Linear Programming.

    Args:
    ----
        prices: list or pd.Series of 24 hourly prices
        max_buys: maximum number of buy transactions per day
        max_sells: maximum number of sell transactions per day
        capacity: maximum energy storage capacity in MWh
        power: maximum power that can be bought/sold per hour in MWh

    Returns:
    -------
        tuple: (total_profit, buy_hours_dict, sell_hours_dict)

    """
    try:
        from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value  # type: ignore
    except ImportError as e:
        raise ImportError("Please install pulp: pip install pulp") from e

    prices = list(prices)
    _validate_optimization_inputs(prices, max_buys, max_sells, capacity, power)
    n_hours = len(prices)
    eps = 1e-6

    # Create LP problem
    model = LpProblem("Energy_Trading", LpMaximize)

    # Decision variables
    buy_amount = LpVariable.dicts("buy", range(n_hours), lowBound=0, upBound=power)
    sell_amount = LpVariable.dicts("sell", range(n_hours), lowBound=0, upBound=power)
    is_buy = LpVariable.dicts("is_buy", range(n_hours), cat="Binary")
    is_sell = LpVariable.dicts("is_sell", range(n_hours), cat="Binary")
    storage = LpVariable.dicts("storage", range(n_hours), lowBound=0, upBound=capacity)
    # Decision variables below for cases where capacity % power != 0
    is_partial_buy = LpVariable.dicts("is_partial_buy", range(n_hours), cat="Binary")
    is_partial_sell = LpVariable.dicts("is_partial_sell", range(n_hours), cat="Binary")

    # Objective: maximize profit (sell revenue - buy cost)
    objective = lpSum([sell_amount[h] * total_sell_price(prices[h]) for h in range(n_hours)]) - lpSum(
        [buy_amount[h] * total_buy_price(prices[h]) for h in range(n_hours)]
    )
    model += objective

    for h in range(n_hours):
        prev_storage = 0 if h == 0 else storage[h - 1]

        # 1. Cannot buy and sell in same hour
        model += is_buy[h] + is_sell[h] <= 1, f"no_buy_sell_same_hour_{h}"

        # 2. Partial/full flags must be consistent with action flags
        model += is_partial_buy[h] <= is_buy[h], f"partial_buy_requires_buy_{h}"
        model += is_partial_sell[h] <= is_sell[h], f"partial_sell_requires_sell_{h}"

        # 3. Buy amount rules:
        #    - if not buying -> 0
        #    - if full buy -> exactly power
        #    - if partial buy -> less than power and must fill to capacity
        model += buy_amount[h] <= power * is_buy[h], f"buy_amount_upper_{h}"
        model += buy_amount[h] >= power * (is_buy[h] - is_partial_buy[h]), f"buy_amount_lower_{h}"

        # If partial buy is selected, resulting storage must be exactly capacity
        model += storage[h] >= capacity - capacity * (1 - is_partial_buy[h]), f"partial_buy_hits_capacity_lb_{h}"
        model += storage[h] <= capacity + capacity * (1 - is_partial_buy[h]), f"partial_buy_hits_capacity_ub_{h}"

        # Partial buy only allowed when full buy is impossible
        model += (
            prev_storage >= (capacity - power + eps) * is_partial_buy[h],
            f"partial_buy_only_when_full_not_possible_{h}",
        )  # noqa: E501

        # Partial sell only allowed when full sell is impossible
        model += (
            prev_storage <= (power - eps) + capacity * (1 - is_partial_sell[h]),
            f"partial_sell_only_when_full_not_possible_{h}",
        )  # noqa: E501

        # 4. Sell amount rules:
        #    - if not selling -> 0
        #    - if full sell -> exactly power
        #    - if partial sell -> less than power and must empty to zero
        model += sell_amount[h] <= power * is_sell[h], f"sell_amount_upper_{h}"
        model += sell_amount[h] >= power * (is_sell[h] - is_partial_sell[h]), f"sell_amount_lower_{h}"

        # If partial sell is selected, resulting storage must be exactly zero
        model += storage[h] >= 0 - capacity * (1 - is_partial_sell[h]), f"partial_sell_hits_zero_lb_{h}"
        model += storage[h] <= capacity * (1 - is_partial_sell[h]), f"partial_sell_hits_zero_ub_{h}"

        # 5. Storage balance
        model += storage[h] == prev_storage + buy_amount[h] - sell_amount[h], f"storage_balance_{h}"

    # 6. Max number of buys and sells
    model += lpSum([is_buy[h] for h in range(n_hours)]) <= max_buys, "max_buys"
    model += lpSum([is_sell[h] for h in range(n_hours)]) <= max_sells, "max_sells"

    # 7. End with 0 storage
    model += storage[n_hours - 1] == 0, "end_with_empty"

    # Solve
    model.solve(PULP_CBC_CMD(msg=False))

    status = LpStatus[model.status]
    if status != "Optimal":
        raise RuntimeError(f"Solver failed to find an optimal solution. Status: {status}")

    # Extract solution
    total_profit = value(model.objective)
    if total_profit is None:
        raise RuntimeError("Solver returned no objective value")

    # Reconstruct buy/sell dictionaries
    buy_hours = {}
    sell_hours = {}
    buy_count = 0
    sell_count = 0
    current_cap = 0

    for h in range(n_hours):
        buy_amt = value(buy_amount[h])
        sell_amt = value(sell_amount[h])

        if buy_amt and buy_amt > 1e-6:  # Account for floating point errors
            buy_count += 1
            buy_hours[buy_count] = {
                "hour": h,
                "buy_amount": buy_amt,
                "current_capacity": current_cap,
                "new_capacity": current_cap + buy_amt,
                "total_price": total_buy_price(prices[h]) * buy_amt,
            }
            current_cap += buy_amt

        if sell_amt and sell_amt > 1e-6:
            sell_count += 1
            sell_hours[sell_count] = {
                "hour": h,
                "sell_amount": sell_amt,
                "current_capacity": current_cap,
                "new_capacity": current_cap - sell_amt,
                "total_price": total_sell_price(prices[h]) * sell_amt,
            }
            current_cap -= sell_amt

    return total_profit, buy_hours, sell_hours


def add_optimization_to_dataframe(
    df,
    max_buys=MAX_BUYS,
    max_sells=MAX_SELLS,
    capacity=CAPACITY,
    power=POWER,
):
    """Apply optimization strategy to each day in the dataframe.

    Args:
    ----
        df: DataFrame from get_file() with prices for 24 hours per day.
        max_buys: Maximum number of buy operations allowed.
        max_sells: Maximum number of sell operations allowed.
        capacity: Total battery capacity in MWh.
        power: Battery power rating in MWh.

    Returns:
    -------
        pd.DataFrame with added columns: Buy_hours, Sell_hours, Total_profit

    """
    result_df = df.copy()
    result_df["Buy_hours"] = None
    result_df["Sell_hours"] = None
    result_df["Total_profit"] = 0.0

    optimizer = optimize_day_lp

    for idx, row in df.iterrows():
        # Extract 24 hourly prices (columns should be: '1', '2', ..., '24' for hours 1-24)
        prices = [row[str(h)] for h in range(1, 25)]

        profit, buy_hours, sell_hours = optimizer(prices, max_buys, max_sells, capacity, power)

        result_df.at[idx, "Buy_hours"] = buy_hours
        result_df.at[idx, "Sell_hours"] = sell_hours
        result_df.at[idx, "Total_profit"] = profit

    return result_df


if __name__ == "__main__":
    df = get_file()

    # Apply optimization using DP
    df_optimized = add_optimization_to_dataframe(df)

    print(df_optimized[["Buy_hours", "Sell_hours", "Total_profit"]])
    print(f"\nTotal profit for period: {df_optimized['Total_profit'].sum()}")
