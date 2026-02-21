"""Visualization and HTML export for optimization results."""
import pandas as pd
import webbrowser
import os
import tempfile
from datetime import datetime, timedelta
from ua_batteries.main import add_optimization_to_dataframe
from ua_batteries.config import MAX_BUYS, MAX_SELLS, CAPACITY, POWER


def create_optimization_visualization(
    df,
    method="dp",
    max_buys=MAX_BUYS,
    max_sells=MAX_SELLS,
    capacity=CAPACITY,
    power=POWER,
):
    """
    Create a visualization of the buy/sell optimization strategy.

    Shows a table with:
    - Rows: dates
    - Columns: hours 1-24
    - Cells: colored green for buy hours, red for sell hours
    - RHS: total profit for each day

    Args:
        df: DataFrame from get_file() with prices for 24 hours per day
        method: 'dp' for dynamic programming, 'lp' for linear programming
        max_buys, max_sells, capacity, power: optimization parameters

    Returns:
        pd.DataFrame: Visualization dataframe with styling applied
    """
    # Run optimization if not already done
    if "Buy_hours" not in df.columns:
        df = add_optimization_to_dataframe(
            df,
            method=method,
            max_buys=max_buys,
            max_sells=max_sells,
            capacity=capacity,
            power=power,
        )

    # Create visualization dataframe
    viz_df = pd.DataFrame(index=df.index)

    # Add columns for each hour (1-24)
    for hour in range(1, 25):
        viz_df[f"Hour {hour}"] = ""

    # Fill in buy/sell information
    for idx, row in df.iterrows():
        buy_hours = row["Buy_hours"]
        sell_hours = row["Sell_hours"]

        # Mark buy hours
        if buy_hours:
            for buy_id, buy_info in buy_hours.items():
                hour = buy_info["hour"]
                amount = buy_info["buy_amount"]
                viz_df.at[idx, f"Hour {hour + 1}"] = f"BUY\n{amount:.1f}MWh"

        # Mark sell hours
        if sell_hours:
            for sell_id, sell_info in sell_hours.items():
                hour = sell_info["hour"]
                amount = sell_info["sell_amount"]
                viz_df.at[idx, f"Hour {hour + 1}"] = f"SELL\n{amount:.1f}MWh"

    # Add total profit column on RHS
    viz_df["Total Profit"] = df["Total_profit"].values

    return viz_df


def style_visualization(viz_df, df):
    """
    Apply styling to the visualization dataframe.

    - Green background for buy hours
    - Red background for sell hours
    - Bold text for profit column

    Args:
        viz_df: Visualization dataframe from create_optimization_visualization
        df: Original optimized dataframe with Buy_hours and Sell_hours

    Returns:
        Styled dataframe (can be displayed in Jupyter or exported to HTML)
    """

    def color_cells(val, df_row_idx, col_name):
        """Color cells based on buy/sell status"""
        if col_name == "Total Profit":
            return "font-weight: bold"

        if not val or val == "":
            return ""

        if "BUY" in val:
            return "background-color: #90EE90; color: black; font-weight: bold"
        elif "SELL" in val:
            return "background-color: #FFB6C1; color: black; font-weight: bold"

        return ""

    # Create a styled dataframe
    styled = viz_df.style

    # Apply cell coloring
    for col in viz_df.columns:
        for idx in viz_df.index:
            styled = (
                styled.applymap(
                    lambda v, row_idx=idx, col=col: color_cells(v, row_idx, col),
                    subset=pd.IndexSlice[idx, col],
                )
                if hasattr(styled, "applymap")
                else styled
            )

    return styled


def display_visualization(
    df,
    method="dp",
    max_buys=MAX_BUYS,
    max_sells=MAX_SELLS,
    capacity=CAPACITY,
    power=POWER,
    return_styled=False,
):
    """
    Create and display the optimization visualization.

    Args:
        df: DataFrame from get_file()
        method: 'dp' or 'lp'
        max_buys, max_sells, capacity, power: optimization parameters
        return_styled: If True, return styled dataframe; if False, return plain dataframe

    Returns:
        pd.DataFrame or Styled DataFrame
    """
    # Run optimization if needed
    optimized_df = add_optimization_to_dataframe(
        df,
        method=method,
        max_buys=max_buys,
        max_sells=max_sells,
        capacity=capacity,
        power=power,
    )

    # Create visualization
    viz_df = create_optimization_visualization(
        optimized_df,
        method=method,
        max_buys=max_buys,
        max_sells=max_sells,
        capacity=capacity,
        power=power,
    )

    if return_styled:
        return style_visualization(viz_df, optimized_df)
    else:
        return viz_df


def export_to_html(
    viz_df, original_df, title="Energy Trading Optimization", open_browser=True
):
    """
    Export visualization to styled HTML file with prices and optionally open in browser.

    Args:
        viz_df: Visualization dataframe from create_optimization_visualization
        original_df: Original dataframe with prices from get_file()
        title: Title for the HTML page
        open_browser: If True, open the HTML file in default browser

    Returns:
        str: Path to the generated HTML file
    """
    # Create styled HTML
    html_string = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            .container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                font-size: 11px;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .buy {{
                background-color: #90EE90;
                font-weight: bold;
                color: darkgreen;
            }}
            .sell {{
                background-color: #FFB6C1;
                font-weight: bold;
                color: darkred;
            }}
            .profit {{
                background-color: #FFF9C4;
                font-weight: bold;
                color: #F57F17;
            }}
            .date-col {{
                background-color: #E8F5E9;
                font-weight: bold;
                text-align: left;
            }}
            .price {{
                font-size: 10px;
                display: block;
                color: #666;
            }}
            .amount {{
                font-size: 10px;
                font-weight: bold;
                display: block;
            }}
            .summary {{
                margin-top: 20px;
                padding: 15px;
                background-color: #E3F2FD;
                border-left: 4px solid #2196F3;
                border-radius: 4px;
            }}
            .summary h2 {{
                margin-top: 0;
                color: #1976D2;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="container">
            <table>
                <tr>
                    <th>Date</th>
    """

    # Add hour headers
    for hour in range(1, 25):
        html_string += f"<th>Hour {hour}</th>"

    html_string += "<th>Total Profit</th></tr>"

    # Add data rows
    for i, (idx, row) in enumerate(viz_df.iterrows()):
        # Get the date from original_df at the same position
        date_value = original_df.index[i]
        html_string += f"<tr><td class='date-col'>{date_value}</td>"

        # Get the original prices for this date using iloc to match position
        original_row = original_df.iloc[i]

        for hour in range(1, 25):
            # Get price for this hour (columns are 1-24)
            price = original_row[str(hour)]
            cell_value = row[f"Hour {hour}"]

            # Determine if this hour has a buy or sell action
            if "BUY" in str(cell_value):
                # Extract amount from cell_value (format "BUY\n{amount}")
                html_string += f"<td class='buy'><span class='price'>{price:.2f}</span><span class='amount'>{cell_value}</span></td>"  # noqa E501
            elif "SELL" in str(cell_value):
                # Extract amount from cell_value (format "SELL\n{amount}")
                html_string += f"<td class='sell'><span class='price'>{price:.2f}</span><span class='amount'>{cell_value}</span></td>"  # noqa E501
            else:
                # Just show the price
                html_string += f"<td><span class='price'>{price:.2f}</span></td>"

        profit = row["Total Profit"]
        html_string += f"<td class='profit'>{profit:,.2f}</td></tr>"

    # Add summary
    total_profit = viz_df["Total Profit"].sum()
    html_string += f"""
            </table>
        </div>
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Profit for Period:</strong> {total_profit:,.2f} (UAH)</p>
            <p><strong>Number of Days:</strong> {len(viz_df)}</p>
            <p><strong>Average Daily Profit:</strong> {total_profit / len(viz_df):,.2f} (UAH)</p>
        </div>
    </body>
    </html>
    """

    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    html_file = os.path.join(temp_dir, "energy_optimization_viz.html")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_string)

    print(f"HTML visualization saved to: {html_file}")

    # Open in browser
    if open_browser:
        webbrowser.open(f"file://{html_file}")
        print("Opening in default browser...")

    return html_file


if __name__ == "__main__":
    from ua_batteries.utils.get_file import get_file

    df = get_file()

    # Create visualization
    print("\nRunning optimization (this may take a moment)...")
    viz = create_optimization_visualization(
        df, method="dp", max_buys=MAX_BUYS, max_sells=MAX_SELLS, capacity=CAPACITY, power=POWER
    )

    # Export to HTML and open in browser
    today = (datetime.today() + timedelta(days=1)).strftime("%B %Y")
    html_path = export_to_html(
        viz, df, title=f"Energy Trading Optimization - {today}", open_browser=True
    )
    print("\nVisualization complete!")
    print(f"Total profit for period: {viz['Total Profit'].sum():.2f}")
