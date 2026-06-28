import sqlite3
import pandas as pd

# 1. Establish a local connection to create the SQLite database file
connection = sqlite3.connect("ecommerce_analytics.db")

# 2. Define a map of your cleaned CSV files and their corresponding SQL table names
data_files = {
    "cleaned_orders.csv": "cleaned_orders",
    "cleaned_products.csv": "cleaned_products",
    "cleaned_order_items.csv": "cleaned_order_items",
    "cleaned_customers.csv": "cleaned_customers"
}

print("Starting database ingestion pipeline...")

# 3. Loop through each file, read it via Pandas, and write it straight to SQLite
for csv_file, table_name in data_files.items():
    try:
        # Read the local CSV file
        df = pd.read_csv(csv_file)
        
        # Load the dataframe into SQLite (if_exists="replace" drops old data and builds it fresh)
        df.to_sql(table_name, connection, if_exists="replace", index=False)
        print("Successfully loaded " + csv_file + " into SQL table '" + table_name + "'.")
        
    except Exception as error:
        print("Failed to load " + csv_file + ": " + str(error))

# Close the database connection safely
connection.close()
print("Ingestion complete! Your 'ecommerce_analytics.db' file is ready for analysis.")