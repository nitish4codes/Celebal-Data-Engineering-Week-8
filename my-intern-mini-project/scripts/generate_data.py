import csv
import random
from datetime import datetime, timedelta

NUM_ROWS = 520 # as atleast 500 are required

# generating customers data

# 2% invalid email:
num_invalid = int(NUM_ROWS * 0.02)
#Picking exactly 10 unique row numbers to be invalid
invalid_rows = set(random.sample(range(1, NUM_ROWS + 1), num_invalid))

customers = []
for i in range(1, NUM_ROWS + 1):
    customer_id = "cust_" + str(i)
    customer_name = "Customer " + str(i)
    
    if i in invalid_rows:
        email = "user" + str(i) + "example.com"
    else:
        email = "user" + str(i) + "@example.com"
    
    start_date = datetime(2025, 1, 1)
    random_days = timedelta(days=random.randint(0, 365))
    registration_date = (start_date + random_days).strftime("%Y-%m-%d")

    customer_type = random.choice(["REGULAR", "PREMIUM", "VIP"])
    customers.append([customer_id, customer_name, email, registration_date, customer_type])


# generating products data

categories = {
    "Electronics": ["Laptop", "Smartphone", "Headphones"], 
    "Clothing": ["T-Shirt", "Jeans", "Jacket"], 
    "Home": ["Lamp", "Chair", "Blender"], 
    "Books": ["Fiction", "Sci-Fi", "Biography"] 
}
products = []
product_ids = []
for i in range(1, NUM_ROWS + 1):
    
    product_id = "PROD_" + str(i)
    category = random.choice(list(categories.keys()))
    subcategory = random.choice(categories[category])
    
    if random.random() < 0.1:
        product_name = "  " + subcategory + " " + str(i) + "  "
    else:
        product_name = subcategory + " " + str(i)
        
    cost_price = round(random.uniform(5, 500), 2)
    
    products.append([product_id, product_name, category, subcategory, cost_price])
    product_ids.append(product_id)


# Generating Orders Data

orders = []
order_ids = []
for i in range(1, NUM_ROWS + 1):
    order_id = "ORD_" + str(i)

    # 5% of orders missing customer_id
    if random.random() < 0.05:
        customer_id = ""
    else:
        customer_id = random.choice(customers)[0]
    
    dt = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
    
    # Date formats
    if random.random() < 0.05:
        order_date = dt.strftime("%d-%m-%Y")
    else:
        order_date = dt.strftime("%Y-%m-%d %H:%M:%S")
    
    status = random.choice(["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]) #
    region_code = random.choice(["EAST", "WEST", "NORTH", "SOUTH"])
    orders.append([order_id, customer_id, order_date, status, region_code])
    order_ids.append(order_id)

# Generating Order Items Data

order_items = []
for i in range(1, NUM_ROWS + 1):
    item_id = "ITEM_" + str(i)
    
    # Broken reference check
    if random.random() < 0.01:
        order_id = "ORD_99999"
    else:
        order_id = random.choice(order_ids)
        
    product_id = random.choice(product_ids)
    
    # 3% negative quantity
    if random.random() < 0.03:
        quantity = random.randint(-5, -1)
    else:
        quantity = random.randint(1, 10)
        
    unit_price = round(random.uniform(10, 600), 2)
    discount_percent = round(random.uniform(0, 100), 2) 
    order_items.append([item_id, order_id, product_id, quantity, unit_price, discount_percent])

def save_csv(filename, header, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

save_csv("customers.csv", ["customer_id", "customer_name", "email", "registration_date", "customer_type"], customers)
save_csv("products.csv", ["product_id", "product_name", "category", "subcategory", "cost_price"], products)
save_csv("orders.csv", ["order_id", "customer_id", "order_date", "status", "region_code"], orders)
save_csv("order_items.csv", ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"], order_items)
print("Data Generation Complete: CSV files created successfully.")