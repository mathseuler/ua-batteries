"""Optimization algorithms for energy trading strategy."""
from ua_batteries.utils.get_file import get_file
from ua_batteries.utils.total_price import total_buy_price, total_sell_price
from ua_batteries.config import MAX_BUYS, MAX_SELLS, CAPACITY, POWER


def optimize_day_dp(
    prices, max_buys=MAX_BUYS, max_sells=MAX_SELLS, capacity=CAPACITY, power=POWER
):
    """
    Optimize buy/sell strategy for a single day using Dynamic Programming.

    Args:
        prices: list or pd.Series of 24 hourly prices
        max_buys: maximum number of buy transactions per day
        max_sells: maximum number of sell transactions per day
        capacity: maximum energy storage capacity in MWh
        power: maximum power that can be bought/sold per hour in MWh

    Returns:
        tuple: (total_profit, buy_hours_dict, sell_hours_dict)
    """
    prices = list(prices)
    n_hours = len(prices)

    # Memoization: dp[hour][capacity][buys_left][sells_left] = (max_profit, decisions)
    memo = {}

    def dp(hour, current_capacity, buys_left, sells_left):
        """
        DP recursive function.

        Returns: (max_profit, decisions_list)
        where decisions_list = [(action_type, hour, amount, price), ...]
        """
        if hour == n_hours:
            # End of day: capacity must be 0
            if current_capacity == 0:
                return (0, [])
            else:
                return (float("-inf"), [])  # Invalid state

        state = (hour, current_capacity, buys_left, sells_left)
        if state in memo:
            return memo[state]

        best_profit = float("-inf")
        best_decisions = []

        # Option 1: Do nothing this hour
        future_profit, future_decisions = dp(
            hour + 1, current_capacity, buys_left, sells_left
        )
        if future_profit > best_profit:
            best_profit = future_profit
            best_decisions = future_decisions

        # Option 2: Buy this hour
        if buys_left > 0:
            # Try different buy amounts (0 to min(power, capacity - current_capacity))
            max_buy_amount = min(power, capacity - current_capacity)
            for buy_amount in range(
                0,
                int(max_buy_amount) + 1,
                max(1, int(max_buy_amount) // 5) if max_buy_amount > 0 else 1,
            ):
                if buy_amount > 0:
                    buy_cost = total_buy_price(prices[hour]) * buy_amount
                    new_capacity = current_capacity + buy_amount
                    future_profit, future_decisions = dp(
                        hour + 1, new_capacity, buys_left - 1, sells_left
                    )
                    total_profit = future_profit - buy_cost

                    if total_profit > best_profit:
                        best_profit = total_profit
                        best_decisions = [
                            ("buy", hour, buy_amount, prices[hour])
                        ] + future_decisions

        # Option 3: Sell this hour
        if sells_left > 0 and current_capacity > 0:
            # Try different sell amounts (0 to min(power, current_capacity))
            max_sell_amount = min(power, current_capacity)
            for sell_amount in range(
                0,
                int(max_sell_amount) + 1,
                max(1, int(max_sell_amount) // 5) if max_sell_amount > 0 else 1,
            ):
                if sell_amount > 0:
                    sell_revenue = total_sell_price(prices[hour]) * sell_amount
                    new_capacity = current_capacity - sell_amount
                    future_profit, future_decisions = dp(
                        hour + 1, new_capacity, buys_left, sells_left - 1
                    )
                    total_profit = future_profit + sell_revenue

                    if total_profit > best_profit:
                        best_profit = total_profit
                        best_decisions = [
                            ("sell", hour, sell_amount, prices[hour])
                        ] + future_decisions

        memo[state] = (best_profit, best_decisions)
        return best_profit, best_decisions

    # Run DP
    max_profit, decisions = dp(0, 0, max_buys, max_sells)

    # Reconstruct buy/sell dictionaries
    buy_hours = {}
    sell_hours = {}
    buy_count = 0
    sell_count = 0
    current_cap = 0

    for action_type, hour, amount, price in decisions:
        if action_type == "buy":
            buy_count += 1
            buy_hours[buy_count] = {
                "hour": hour,
                "buy_amount": amount,
                "current_capacity": current_cap,
                "new_capacity": current_cap + amount,
                "total_price": total_buy_price(price) * amount,
            }
            current_cap += amount
        elif action_type == "sell":
            sell_count += 1
            sell_hours[sell_count] = {
                "hour": hour,
                "sell_amount": amount,
                "current_capacity": current_cap,
                "new_capacity": current_cap - amount,
                "total_price": total_sell_price(price) * amount,
            }
            current_cap -= amount

    return max_profit, buy_hours, sell_hours


def optimize_day_lp(
    prices, max_buys=MAX_BUYS, max_sells=MAX_SELLS, capacity=CAPACITY, power=POWER
):
    """
    Optimize buy/sell strategy for a single day using Linear Programming.

    Args:
        prices: list or pd.Series of 24 hourly prices
        max_buys: maximum number of buy transactions per day
        max_sells: maximum number of sell transactions per day
        capacity: maximum energy storage capacity in MWh
        power: maximum power that can be bought/sold per hour in MWh

    Returns:
        tuple: (total_profit, buy_hours_dict, sell_hours_dict)
    """
    try:
        from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value  # type: ignore
    except ImportError:
        raise ImportError("Please install pulp: pip install pulp")

    prices = list(prices)
    n_hours = len(prices)

    # Create LP problem
    prob = LpProblem("Energy_Trading", LpMaximize)

    # Decision variables
    buy_amount = {}  # buy_amount[h] = amount bought in hour h
    sell_amount = {}  # sell_amount[h] = amount sold in hour h
    is_buy = {}  # is_buy[h] = 1 if we buy in hour h, 0 otherwise
    is_sell = {}  # is_sell[h] = 1 if we sell in hour h, 0 otherwise
    storage = {}  # storage[h] = amount in storage after hour h

    for h in range(n_hours):
        buy_amount[h] = LpVariable(f"buy_{h}", lowBound=0, upBound=power)
        sell_amount[h] = LpVariable(f"sell_{h}", lowBound=0, upBound=power)
        is_buy[h] = LpVariable(f"is_buy_{h}", cat="Binary")
        is_sell[h] = LpVariable(f"is_sell_{h}", cat="Binary")
        storage[h] = LpVariable(f"storage_{h}", lowBound=0, upBound=capacity)

    # Objective: maximize profit (sell revenue - buy cost)
    objective = lpSum(
        [sell_amount[h] * total_sell_price(prices[h]) for h in range(n_hours)]
    ) - lpSum([buy_amount[h] * total_buy_price(prices[h]) for h in range(n_hours)])
    prob += objective

    # Constraints
    # 1. Cannot buy and sell in same hour
    for h in range(n_hours):
        prob += is_buy[h] + is_sell[h] <= 1, f"no_buy_sell_same_hour_{h}"

    # 2. Buy/sell amounts are bounded by whether we buy/sell
    for h in range(n_hours):
        prob += buy_amount[h] <= power * is_buy[h], f"buy_only_if_selected_{h}"
        prob += sell_amount[h] <= power * is_sell[h], f"sell_only_if_selected_{h}"

    # 3. Max number of buys and sells
    prob += lpSum([is_buy[h] for h in range(n_hours)]) <= max_buys, "max_buys"
    prob += lpSum([is_sell[h] for h in range(n_hours)]) <= max_sells, "max_sells"

    # 4. Storage balance
    for h in range(n_hours):
        if h == 0:
            prob += storage[h] == buy_amount[h] - sell_amount[h], "storage_0"
        else:
            prob += (
                storage[h] == storage[h - 1] + buy_amount[h] - sell_amount[h],
                f"storage_{h}",
            )

    # 5. End with 0 storage
    prob += storage[n_hours - 1] == 0, "end_with_empty"

    # Solve
    prob.solve()

    # Extract solution
    total_profit = value(prob.objective)

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
    method="dp",
    max_buys=MAX_BUYS,
    max_sells=MAX_SELLS,
    capacity=CAPACITY,
    power=POWER,
):
    """
    Apply optimization strategy to each day in the dataframe.

    Args:
        df: DataFrame from get_file() with prices for 24 hours per day
        method: 'dp' for dynamic programming, 'lp' for linear programming
        max_buys, max_sells, capacity, power: optimization parameters

    Returns:
        DataFrame with added columns: Buy_hours, Sell_hours, Total_profit
    """
    result_df = df.copy()
    result_df["Buy_hours"] = None
    result_df["Sell_hours"] = None
    result_df["Total_profit"] = 0.0

    optimizer = optimize_day_dp if method == "dp" else optimize_day_lp

    for idx, row in df.iterrows():
        # Extract 24 hourly prices (columns should be: '1', '2', ..., '24' for hours 1-24)
        prices = [row[str(h)] for h in range(1, 25)]

        profit, buy_hours, sell_hours = optimizer(
            prices, max_buys, max_sells, capacity, power
        )

        result_df.at[idx, "Buy_hours"] = buy_hours
        result_df.at[idx, "Sell_hours"] = sell_hours
        result_df.at[idx, "Total_profit"] = profit

    return result_df


if __name__ == "__main__":
    df = get_file()

    # Apply optimization using DP
    df_optimized = add_optimization_to_dataframe(df, method="dp")

    print(df_optimized[["Buy_hours", "Sell_hours", "Total_profit"]])
    print(f"\nTotal profit for period: {df_optimized['Total_profit'].sum()}")
