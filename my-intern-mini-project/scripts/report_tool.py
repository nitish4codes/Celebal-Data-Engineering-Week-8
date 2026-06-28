import sqlite3
from datetime import datetime, timedelta

def calculate_previous_dates(start_str, end_str, report_type):
    """
    Calculates the exact start and end dates of the previous period
    to handle the required percentage change comparison.
    """
    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
    delta = (end_dt - start_dt) + timedelta(days=1)
    
    # Calculate previous period boundaries based on the duration of the current input window
    prev_start_dt = start_dt - delta
    prev_end_dt = end_dt - delta
    
    return prev_start_dt.strftime("%Y-%m-%d"), prev_end_dt.strftime("%Y-%m-%d")

def fetch_metrics(cursor, start, end):
    """Extracts core sales KPIs from the database for a given date bound."""
    query = """
        SELECT COUNT(DISTINCT o.order_id),
               COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 0.0),
               COUNT(DISTINCT o.customer_id)
        FROM cleaned_orders o
        JOIN cleaned_order_items oi ON o.order_id = oi.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND oi.quantity > 0
    """
    cursor.execute(query, (start, end))
    return cursor.fetchone()

def fetch_top_products(cursor, start, end):
    """Extracts the top 3 items based on sales volumes within the timeframe."""
    query = """
        SELECT p.product_name, SUM(oi.quantity) as total_qty
        FROM cleaned_order_items oi
        JOIN cleaned_orders o ON oi.order_id = o.order_id
        JOIN cleaned_products p ON oi.product_id = p.product_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND oi.quantity > 0
        GROUP BY p.product_name
        ORDER BY total_qty DESC
        LIMIT 3
    """
    cursor.execute(query, (start, end))
    return cursor.fetchall()

def run_analytics_portal():
    print("       E-COMMERCE EXECUTIVE REPORTING TOOL        ")
    
    # 1 & 2. Accept targeted reporting parameters from the terminal prompt
    report_type = input("Enter Report Type (daily / weekly / monthly): ").strip().lower()
    start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
    end_date = input("Enter End Date   (YYYY-MM-DD): ").strip()
    
    # 3. Connect directly to our active SQLite local storage binary file
    connection = sqlite3.connect("ecommerce_analytics.db")
    cursor = connection.cursor()
    
    # Calculate dates for the historical matching period comparison
    prev_start_date, prev_end_date = calculate_previous_dates(start_date, end_date, report_type)
    
    # 4. Fetch metrics for both periods
    curr_orders, curr_revenue, curr_custs = fetch_metrics(cursor, start_date, end_date)
    prev_orders, prev_revenue, prev_custs = fetch_metrics(cursor, prev_start_date, prev_end_date)
    top_products = fetch_top_products(cursor, start_date, end_date)
    
    connection.close()
    
    # Compute Percentage Changes safely (avoiding DivisionByZero errors)
    order_pct = ((curr_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0.0
    rev_pct = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0
    cust_pct = ((curr_custs - prev_custs) / prev_custs * 100) if prev_custs > 0 else 0.0
    
    # Display the structured summary report on the screen
    print("")
    print(" EXECUTIVE METRICS SUMMARY REPORT (" + report_type.upper() + ")")
    print(" Timeline Window: " + start_date + " to " + end_date)
    print(" Compare Window:  " + prev_start_date + " to " + prev_end_date)
    
    print("Total Orders:     " + str(curr_orders) + " (" + str(round(order_pct, 1)) + "% vs prev period)")
    print("Total Revenue:    $" + str(round(curr_revenue, 2)) + " (" + str(round(rev_pct, 1)) + "% vs prev period)")
    print("Unique Customers: " + str(curr_custs) + " (" + str(round(cust_pct, 1)) + "% vs prev period)")
    
    print("\n TOP 3 POPULAR PRODUCTS ")
    if top_products:
        for index, item in enumerate(top_products, start=1):
            print(str(index) + ". " + item[0] + " (" + str(item[1]) + " units sold)")
    else:
        print("No item movements logged in this frame window.")

if __name__ == "__main__":
    run_analytics_portal()