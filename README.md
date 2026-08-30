# Retail Sales & Customer Analytics Dashboard
 
A SQL and Python data analysis project built around a fictional retail
company's sales data. The project uses a relational database and SQL
queries — including joins, aggregations, window functions, and a self-join
— to answer real business questions about revenue, customers, and products,
with results visualized through a Python/pandas layer.

![alt text](charts/revenue_by_category.png)
 
## Overview
 
This project integrates a SQLite database with a Python analysis layer into
a complete sales-analytics workflow. The database stores customers, products,
orders, and order line items; SQL queries answer business questions about
revenue and customer behavior; and a Python script runs those queries and
turns the results into charts.
 
The project demonstrates the implementation and integration of:
 
- Relational database design (primary keys, foreign keys, indexes)
- Multi-table SQL joins
- Aggregate functions and `GROUP BY`
- Window functions (`LAG()`, `ROW_NUMBER()`)
- Self-joins for market basket analysis
- Common Table Expressions (CTEs) and subqueries
- Python/pandas integration with SQL
- Data visualization with matplotlib
## Features
 
- Generate a reproducible fictional dataset (120 customers, 45 products,
  400 orders, ~1,200 order line items)
- Query total, category-level, and monthly revenue
- Identify top customers and top products by revenue
- Calculate month-over-month revenue growth
- Find customers who haven't ordered in the last 90 days
- Measure revenue concentration among top customers
- Identify products frequently purchased together
- Visualize key metrics as saved PNG charts
## Technologies
 
- **SQL (SQLite)**
- **Python**
- **pandas**
- **matplotlib**
- **Git**
## Project Structure
 
| File | Description |
|------|-------------|
| `sql/schema.sql` | Defines the four tables and their relationships |
| `sql/queries.sql` | The 12 business-question SQL queries |
| `python/build_database.py` | Generates and seeds `retail.db` with fictional data |
| `python/analysis.py` | Runs queries through pandas and saves charts |
| `data/retail.db` | The generated SQLite database |
| `charts/` | PNG chart output from `analysis.py` |
| `requirements.txt` | Python dependencies |
 
## Schema
 
```
customers (customer_id PK, first_name, last_name, city, state, age)
products  (product_id PK, product_name, category, price)
orders    (order_id PK, customer_id FK, order_date, total_amount)
order_items (order_item_id PK, order_id FK, product_id FK, quantity)
```
 
`customers → orders → order_items → products` — a standard one-to-many /
many-to-many pattern that mirrors how real e-commerce schemas are shaped.
 
## How It Works
 
The database models a small retailer: customers place orders, each order
contains one or more line items, and each line item references a product.
SQL queries join across these tables to answer questions like which
customers generate the most revenue or which products are frequently
bought together, using aggregation, window functions, and a self-join.
The Python layer then runs those same queries through pandas and renders
the results as charts, so the project produces both raw query output and
visual summaries.
 
### Setup
 
**1. Clone and set up a virtual environment**
 
```bash
git clone <your-repo-url>
cd retail-sales-dashboard
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```
 
**2. Build the database**
 
```bash
python python/build_database.py
```
 
This creates `data/retail.db` with 120 customers, 45 products, 400 orders,
and ~1,200 order line items — enough volume for the aggregates to look
realistic without needing a real dataset.
 
**3. Run the SQL directly (optional)**
 
If you have the `sqlite3` CLI installed:
 
```bash
sqlite3 data/retail.db
sqlite> .read sql/queries.sql
```
 
Or open `data/retail.db` in any SQLite GUI (DB Browser for SQLite, TablePlus,
the SQLite extension in VS Code, etc.) and run `sql/queries.sql` query by
query.
 
**4. Run the Python analysis + generate charts**
 
```bash
python python/analysis.py
```
 
This prints each query's results as a pandas DataFrame and saves four charts
to `charts/`:
- `revenue_by_category.png`
- `monthly_revenue.png`
- `top_10_products.png`
- `top_10_customers.png`
## Business Questions Answered
 
| # | Question | SQL concept |
|---|----------|-------------|
| 1 | What are the 10 most expensive products? | `ORDER BY`, `LIMIT` |
| 2 | What is total revenue? | `SUM()`, `JOIN` |
| 3 | How much revenue did each product category generate? | `GROUP BY`, `SUM()` |
| 4 | Which customers have spent the most money? | multi-table `JOIN` |
| 5 | What was monthly revenue? | `strftime()` date bucketing |
| 6 | What are the top 5 products by revenue? | `GROUP BY`, `ORDER BY`, `LIMIT` |
| 7 | Who are the top 10 customers by total spending? | multi-table `JOIN`, `GROUP BY` |
| 8 | Which category has the highest average order value? | subquery, `AVG()` |
| 9 | Which customers haven't ordered in the last 90 days? | `LEFT JOIN`, `HAVING` |
| 10 | What % of revenue comes from the top 10 customers? | CTE, `ROW_NUMBER()` window function |
| 11 | What is month-over-month revenue growth? | CTE, `LAG()` window function |
| 12 | Which products are frequently bought together? | self-join (market basket analysis) |
 
All queries live in `sql/queries.sql` with comments explaining the SQL
concept each one practices.
 
## Testing
 
Every query was run directly against the generated database to confirm it
executes without error and returns results consistent with the underlying
data — for example, cross-checking that category revenue totals sum to the
overall total revenue figure, and that the top-10-customer percentage from
query 10 is mathematically consistent with individual customer totals.
`python/analysis.py` re-runs the core queries as an additional check each
time it's executed, since a broken query would raise an error or produce an
empty DataFrame instead of a chart.
 
## Skills Demonstrated
 
This project demonstrates experience with:
 
- Relational database design and normalization
- Writing multi-table SQL joins
- Aggregate functions, `GROUP BY`, and `HAVING`
- Window functions (`LAG()`, `ROW_NUMBER()`) for trend and ranking analysis
- Self-joins for relationship analysis (market basket analysis)
- Common Table Expressions (CTEs) and subqueries
- Connecting a SQL database to Python with `sqlite3` and `pandas`
- Data visualization with matplotlib
- Using Git for version control
## Project Notes
 
The database is generated by `python/build_database.py` using a fixed
random seed, so results are reproducible. No external data source or API
key is needed — customer names, cities, and product names are drawn from
static lists in that script, and order dates/amounts are randomized with a
slight weighting so a handful of "power customers" naturally emerge, which
is what makes the customer-ranking and revenue-concentration queries
meaningful rather than flat.
