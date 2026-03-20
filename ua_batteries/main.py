"""Optimization algorithms for energy trading strategy."""

from ua_batteries.config import CAPACITY, MAX_BUYS, MAX_SELLS, POWER
from ua_batteries.utils.get_file import get_file
from ua_batteries.utils.total_price import total_buy_price, total_sell_price


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
        from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value  # type: ignore
    except ImportError:
        raise ImportError("Please install pulp: pip install pulp")

    prices = list(prices)
    n_hours = len(prices)

    # Create LP problem
    model = LpProblem("Energy_Trading", LpMaximize)

    # Decision variables
    buy_amount = LpVariable.dicts("buy", range(n_hours), lowBound=0, upBound=power)
    sell_amount = LpVariable.dicts("sell", range(n_hours), lowBound=0, upBound=power)
    is_buy = LpVariable.dicts("is_buy", range(n_hours), cat="Binary")
    is_sell = LpVariable.dicts("is_sell", range(n_hours), cat="Binary")
    storage = LpVariable.dicts("storage", range(n_hours), lowBound=0, upBound=capacity)

    # Objective: maximize profit (sell revenue - buy cost)
    objective = lpSum([sell_amount[h] * total_sell_price(prices[h]) for h in range(n_hours)]) - lpSum(
        [buy_amount[h] * total_buy_price(prices[h]) for h in range(n_hours)]
    )
    model += objective

    # Constraints
    # 1. Cannot buy and sell in same hour
    for h in range(n_hours):
        model += is_buy[h] + is_sell[h] <= 1, f"no_buy_sell_same_hour_{h}"

    # 2. Buy/sell amounts are bounded by whether we buy/sell
    for h in range(n_hours):
        model += buy_amount[h] == power * is_buy[h], f"buy_only_if_selected_{h}"
        model += sell_amount[h] == power * is_sell[h], f"sell_only_if_selected_{h}"

    # 3. Max number of buys and sells
    model += lpSum([is_buy[h] for h in range(n_hours)]) <= max_buys, "max_buys"
    model += lpSum([is_sell[h] for h in range(n_hours)]) <= max_sells, "max_sells"

    # 4. Storage balance
    for h in range(n_hours):
        if h == 0:
            model += storage[h] == buy_amount[h] - sell_amount[h], "storage_0"
        else:
            model += (
                storage[h] == storage[h - 1] + buy_amount[h] - sell_amount[h],
                f"storage_{h}",
            )

    # 5. End with 0 storage
    model += storage[n_hours - 1] == 0, "end_with_empty"

    # Solve
    model.solve()

    # Extract solution
    total_profit = value(model.objective)

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
