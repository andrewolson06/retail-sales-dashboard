"""
analysis.py

Connects to retail.db, runs the business-question queries through pandas,
prints the results, and saves a few charts to the charts/ folder.

Run after build_database.py:
    python analysis.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "retail.db"
CHARTS_DIR = ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def run(label: str, query: str) -> pd.DataFrame:
    df = pd.read_sql_query(query, conn)
    print(f"\n=== {label} ===")
    print(df.to_string(index=False))
    return df


# ------------------------------------------------------------------
# 1. Revenue by product category
# ------------------------------------------------------------------
category_revenue = run(
    "Revenue by Category",
    """
    SELECT p.category, SUM(oi.quantity * p.price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category
    ORDER BY revenue DESC;
    """,
)

plt.figure(figsize=(9, 5))
plt.bar(category_revenue["category"], category_revenue["revenue"], color="#3E6259")
plt.title("Revenue by Product Category")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "revenue_by_category.png", dpi=150)
plt.close()


# ------------------------------------------------------------------
# 2. Monthly revenue trend
# ------------------------------------------------------------------
monthly_revenue = run(
    "Monthly Revenue",
    """
    SELECT strftime('%Y-%m', o.order_date) AS year_month,
           SUM(oi.quantity * p.price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY year_month
    ORDER BY year_month;
    """,
)

plt.figure(figsize=(10, 5))
plt.plot(monthly_revenue["year_month"], monthly_revenue["revenue"], marker="o", color="#B5533C")
plt.title("Monthly Revenue")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=60, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "monthly_revenue.png", dpi=150)
plt.close()


# ------------------------------------------------------------------
# 3. Top 10 products by revenue
# ------------------------------------------------------------------
top_products = run(
    "Top 10 Products by Revenue",
    """
    SELECT p.product_name, SUM(oi.quantity * p.price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY revenue DESC
    LIMIT 10;
    """,
)

plt.figure(figsize=(9, 6))
plt.barh(top_products["product_name"][::-1], top_products["revenue"][::-1], color="#4C6A8C")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue ($)")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "top_10_products.png", dpi=150)
plt.close()


# ------------------------------------------------------------------
# 4. Top 10 customers by spending
# ------------------------------------------------------------------
top_customers = run(
    "Top 10 Customers by Spending",
    """
    SELECT c.first_name || ' ' || c.last_name AS customer_name,
           SUM(oi.quantity * p.price) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id, customer_name
    ORDER BY total_spent DESC
    LIMIT 10;
    """,
)

plt.figure(figsize=(9, 6))
plt.barh(top_customers["customer_name"][::-1], top_customers["total_spent"][::-1], color="#8C6A4C")
plt.title("Top 10 Customers by Total Spending")
plt.xlabel("Total Spent ($)")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "top_10_customers.png", dpi=150)
plt.close()


# ------------------------------------------------------------------
# 5. Total revenue + top-10-customer concentration (the "interview" stat)
# ------------------------------------------------------------------
concentration = run(
    "Top 10 Customer Revenue Concentration",
    """
    WITH customer_totals AS (
        SELECT c.customer_id, SUM(oi.quantity * p.price) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY c.customer_id
    ),
    ranked AS (
        SELECT total_spent, ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS rnk
        FROM customer_totals
    )
    SELECT
        SUM(CASE WHEN rnk <= 10 THEN total_spent ELSE 0 END) AS top_10_revenue,
        SUM(total_spent) AS total_revenue,
        100.0 * SUM(CASE WHEN rnk <= 10 THEN total_spent ELSE 0 END) / SUM(total_spent) AS pct_of_total
    FROM ranked;
    """,
)

print(
    f"\nTop 10 customers generate {concentration['pct_of_total'].iloc[0]:.1f}% "
    f"of total revenue (${concentration['top_10_revenue'].iloc[0]:,.2f} "
    f"of ${concentration['total_revenue'].iloc[0]:,.2f})."
)

conn.close()
print(f"\nCharts saved to: {CHARTS_DIR}")
