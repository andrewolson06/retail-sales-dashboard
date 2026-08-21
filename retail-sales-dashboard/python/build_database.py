"""
build_database.py

Creates retail.db (SQLite) and populates it with fictional but realistic
retail data: customers, products, orders, and order_items.

Run this once to generate the database:
    python build_database.py
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # reproducible data

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "retail.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

# ------------------------------------------------------------------
# Reference data pools (no internet / external packages required)
# ------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Nancy", "Matthew", "Lisa", "Anthony", "Betty", "Mark", "Margaret",
    "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly", "Andrew",
    "Emily", "Joshua", "Donna", "Kenneth", "Michelle", "Kevin", "Carol",
    "Brian", "Amanda", "George", "Melissa", "Timothy", "Deborah", "Ronald",
    "Stephanie",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]
CITIES_STATES = [
    ("Milwaukee", "WI"), ("Chicago", "IL"), ("Minneapolis", "MN"),
    ("Madison", "WI"), ("Detroit", "MI"), ("Columbus", "OH"),
    ("Indianapolis", "IN"), ("St. Louis", "MO"), ("Kansas City", "MO"),
    ("Denver", "CO"), ("Austin", "TX"), ("Dallas", "TX"),
    ("Phoenix", "AZ"), ("Seattle", "WA"), ("Portland", "OR"),
    ("Atlanta", "GA"), ("Charlotte", "NC"), ("Nashville", "TN"),
    ("Boston", "MA"), ("Philadelphia", "PA"), ("Pittsburgh", "PA"),
    ("Baltimore", "MD"), ("Sacramento", "CA"), ("San Diego", "CA"),
    ("Las Vegas", "NV"),
]

# Products grouped by category -> keeps GROUP BY category queries meaningful
PRODUCTS = [
    # Electronics
    ("Wireless Earbuds", "Electronics", 59.99),
    ("Bluetooth Speaker", "Electronics", 39.99),
    ("Smartwatch", "Electronics", 149.99),
    ("4K Streaming Stick", "Electronics", 34.99),
    ("Noise Cancelling Headphones", "Electronics", 199.99),
    ("Portable Power Bank", "Electronics", 24.99),
    ("USB-C Hub", "Electronics", 29.99),
    ("Mechanical Keyboard", "Electronics", 89.99),
    ("Wireless Mouse", "Electronics", 19.99),
    ("Webcam 1080p", "Electronics", 44.99),
    # Home & Kitchen
    ("Stainless Steel Cookware Set", "Home & Kitchen", 129.99),
    ("Air Fryer", "Home & Kitchen", 79.99),
    ("Coffee Maker", "Home & Kitchen", 49.99),
    ("Blender", "Home & Kitchen", 39.99),
    ("Knife Set", "Home & Kitchen", 59.99),
    ("Bedding Set - Queen", "Home & Kitchen", 69.99),
    ("Throw Blanket", "Home & Kitchen", 24.99),
    ("Scented Candle Set", "Home & Kitchen", 19.99),
    ("Storage Bins (Set of 6)", "Home & Kitchen", 34.99),
    ("Electric Kettle", "Home & Kitchen", 27.99),
    # Apparel
    ("Men's Running Shoes", "Apparel", 74.99),
    ("Women's Yoga Pants", "Apparel", 44.99),
    ("Unisex Hoodie", "Apparel", 39.99),
    ("Winter Jacket", "Apparel", 119.99),
    ("Baseball Cap", "Apparel", 19.99),
    ("Athletic Socks (6-Pack)", "Apparel", 14.99),
    ("Denim Jeans", "Apparel", 54.99),
    ("Graphic T-Shirt", "Apparel", 17.99),
    # Sports & Outdoors
    ("Yoga Mat", "Sports & Outdoors", 24.99),
    ("Adjustable Dumbbell Set", "Sports & Outdoors", 149.99),
    ("Camping Tent (2-Person)", "Sports & Outdoors", 89.99),
    ("Insulated Water Bottle", "Sports & Outdoors", 22.99),
    ("Resistance Bands Set", "Sports & Outdoors", 19.99),
    ("Hiking Backpack", "Sports & Outdoors", 64.99),
    ("Bike Helmet", "Sports & Outdoors", 34.99),
    # Beauty & Personal Care
    ("Electric Toothbrush", "Beauty & Personal Care", 44.99),
    ("Hair Dryer", "Beauty & Personal Care", 34.99),
    ("Skincare Gift Set", "Beauty & Personal Care", 39.99),
    ("Electric Shaver", "Beauty & Personal Care", 54.99),
    ("Makeup Brush Set", "Beauty & Personal Care", 24.99),
    # Books & Office
    ("Bestselling Novel", "Books & Office", 14.99),
    ("Desk Organizer", "Books & Office", 19.99),
    ("Notebook 3-Pack", "Books & Office", 9.99),
    ("Ergonomic Desk Chair", "Books & Office", 179.99),
    ("Standing Desk Converter", "Books & Office", 129.99),
]

NUM_CUSTOMERS = 120
NUM_ORDERS = 400
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 8, 18)  # "today"


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def build_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())


def seed_customers(conn: sqlite3.Connection) -> None:
    rows = []
    for cid in range(1, NUM_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        city, state = random.choice(CITIES_STATES)
        age = random.randint(18, 75)
        rows.append((cid, first, last, city, state, age))
    conn.executemany(
        "INSERT INTO customers (customer_id, first_name, last_name, city, state, age) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def seed_products(conn: sqlite3.Connection) -> None:
    rows = [
        (i + 1, name, category, price)
        for i, (name, category, price) in enumerate(PRODUCTS)
    ]
    conn.executemany(
        "INSERT INTO products (product_id, product_name, category, price) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )


def seed_orders_and_items(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Give some customers more purchasing frequency than others (realistic skew)
    customer_weights = {
        cid: random.choice([1, 1, 1, 2, 2, 3, 5])  # a few "power customers"
        for cid in range(1, NUM_CUSTOMERS + 1)
    }
    weighted_customers = []
    for cid, weight in customer_weights.items():
        weighted_customers.extend([cid] * weight)

    order_item_id = 1

    for order_id in range(1, NUM_ORDERS + 1):
        customer_id = random.choice(weighted_customers)
        order_date = random_date(START_DATE, END_DATE)

        # Each order has 1-5 line items
        num_items = random.randint(1, 5)
        chosen_products = random.sample(PRODUCTS, k=min(num_items, len(PRODUCTS)))

        total_amount = 0.0
        item_rows = []
        for name, category, price in chosen_products:
            product_id = next(i + 1 for i, p in enumerate(PRODUCTS) if p[0] == name)
            quantity = random.randint(1, 3)
            total_amount += price * quantity
            item_rows.append((order_item_id, order_id, product_id, quantity))
            order_item_id += 1

        cur.execute(
            "INSERT INTO orders (order_id, customer_id, order_date, total_amount) "
            "VALUES (?, ?, ?, ?)",
            (order_id, customer_id, order_date.isoformat(), round(total_amount, 2)),
        )
        cur.executemany(
            "INSERT INTO order_items (order_item_id, order_id, product_id, quantity) "
            "VALUES (?, ?, ?, ?)",
            item_rows,
        )


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        build_schema(conn)
        seed_customers(conn)
        seed_products(conn)
        seed_orders_and_items(conn)
        conn.commit()

        # quick sanity check
        cur = conn.cursor()
        for table in ["customers", "products", "orders", "order_items"]:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count} rows")
        print(f"\nDatabase created at: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
