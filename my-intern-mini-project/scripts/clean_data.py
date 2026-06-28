import pandas as pd
import re

df_orders = pd.read_csv("orders.csv")
df_products = pd.read_csv("products.csv")
df_customers = pd.read_csv("customers.csv")
df_items = pd.read_csv("order_items.csv")

issue_log = []

# 1. clean_orders()
def clean_orders(df):
    null_cust_count = df['customer_id'].isna().sum()
    issue_log.append("Orders: Found " + str(null_cust_count) + " records missing customer_id. Fixed by setting as 'UNKNOWN'.")
    df['customer_id'] = df['customer_id'].fillna('UNKNOWN')
    
    parsed_dates = pd.to_datetime(df['order_date'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
    malformed_mask = parsed_dates.isna()
    df.loc[malformed_mask, 'order_date'] = pd.to_datetime(df.loc[malformed_mask, 'order_date'], format="%d-%m-%Y", errors='coerce')
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    issue_log.append("Orders: Standardized " + str(malformed_mask.sum()) + " malformed date fields.")
    return df

# 2. clean_products()
def clean_products(df):
    df['product_name'] = df['product_name'].str.strip().str.title() #
    issue_log.append("Products: Whitespace trimmed and names altered to Title Case.")
    return df

# 3. validate_emails()
def validate_emails(df):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_mask = ~df['email'].str.match(email_regex, na=False)
    invalid_ids = df[invalid_mask]['customer_id'].tolist()
    issue_log.append("Customers: Detected invalid email formats for user accounts: " + str(invalid_ids))
    return invalid_ids

# 4. check_referential_integrity()
def check_referential_integrity(df_items, df_orders):
    orphaned_items = df_items[~df_items['order_id'].isin(df_orders['order_id'])]
    issue_log.append("Referential Integrity: Found " + str(len(orphaned_items)) + " line items referencing missing orders.")
    return orphaned_items

df_orders = clean_orders(df_orders)
df_products = clean_products(df_products)
invalid_emails = validate_emails(df_customers)
orphans = check_referential_integrity(df_items, df_orders)

df_items = df_items[df_items['order_id'].isin(df_orders['order_id'])]

df_orders.to_csv("cleaned_orders.csv", index=False)
df_products.to_csv("cleaned_products.csv", index=False)
df_items.to_csv("cleaned_order_items.csv", index=False)
df_customers.to_csv("cleaned_customers.csv", index=False)

print("\n--- PIPELINE DATA CLEANING REPORT ---")
for issue in issue_log:
    print("- " + issue)