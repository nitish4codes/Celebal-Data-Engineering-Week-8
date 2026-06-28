import sqlite3

def launch_cli():
    print("=========================================")
    print("   E-COMMERCE ORDER ANALYTICS PORTAL     ")
    print("=========================================\n")
    
    report_type = input("Choose Report Type (daily / weekly / monthly): ").strip().lower() #
    start_date = input("Enter start date bound (YYYY-MM-DD): ").strip() 
    end_date = input("Enter end date bound (YYYY-MM-DD): ").strip() 
    
    conn = sqlite3.connect("ecommerce_analytics.db") 
    cursor = conn.cursor()
    
    summary_query = """
        SELECT COUNT(DISTINCT o.order_id),
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2),
               COUNT(DISTINCT o.customer_id)
        FROM cleaned_orders o
        JOIN cleaned_order_items oi ON o.order_id = oi.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ?
    """ #
    
    try:
        cursor.execute(summary_query, (start_date, end_date))
        metrics = cursor.fetchone()
        
        total_orders = str(metrics[0] or 0)
        total_revenue = str(metrics[1] or 0.00)
        total_customers = str(metrics[2] or 0)
        
        print("\n-----------------------------------------")
        print("  EXECUTIVE METRICS (" + report_type.upper() + " WINDOW) ")
        print("-----------------------------------------")
        print("Total Completed Volume: " + total_orders + " Orders") 
        print("Gross Generated Revenue: $" + total_revenue) 
        print("Active Purchasing Base: " + total_customers + " Customers\n") 
    except Exception as error:
        print("Data extraction processing faulted: " + str(error))
    finally:
        conn.close()

if __name__ == "__main__":
    launch_cli()