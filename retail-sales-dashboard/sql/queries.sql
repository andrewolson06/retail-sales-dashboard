-- ============================================================
-- Retail Sales & Customer Analytics Dashboard
-- Business questions answered in SQL
-- Run against data/retail.db
-- ============================================================


-- 1. What are the 10 most expensive products?
-- Practice: ORDER BY, LIMIT
SELECT
    product_name,
    category,
    price
FROM products
ORDER BY price DESC
LIMIT 10;


-- 2. What is total revenue?
-- Practice: SUM(), JOIN
-- Revenue = quantity * unit price at time of sale (we use current product price)
SELECT
    ROUND(SUM(oi.quantity * p.price), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id;


-- 3. How much revenue did each product category generate?
-- Practice: GROUP BY, SUM(), JOIN
SELECT
    p.category,
    ROUND(SUM(oi.quantity * p.price), 2) AS category_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- 4. Which customers have spent the most money?
-- Practice: multi-table JOIN, GROUP BY, SUM(), ORDER BY, LIMIT
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    ROUND(SUM(oi.quantity * p.price), 2) AS total_spent
FROM customers c
JOIN orders o       ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
GROUP BY c.customer_id, customer_name
ORDER BY total_spent DESC
LIMIT 20;


-- 5. What was monthly revenue?
-- Practice: GROUP BY, strftime() for date bucketing
SELECT
    strftime('%Y-%m', o.order_date) AS year_month,
    ROUND(SUM(oi.quantity * p.price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
GROUP BY year_month
ORDER BY year_month;


-- 6. What are the top 5 products by revenue?
-- Practice: GROUP BY, SUM(), ORDER BY, LIMIT
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * p.price), 2) AS product_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY product_revenue DESC
LIMIT 5;


-- 7. Who are the top 10 customers by total spending?
-- Practice: same pattern as #4, narrowed to top 10, with order count added
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS num_orders,
    ROUND(SUM(oi.quantity * p.price), 2) AS total_spent
FROM customers c
JOIN orders o       ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
GROUP BY c.customer_id, customer_name, c.city, c.state
ORDER BY total_spent DESC
LIMIT 10;


-- 8. Which product category has the highest average order value?
-- Practice: subquery, AVG(), GROUP BY
-- Approach: compute revenue per order per category, then average that per category
SELECT
    category,
    ROUND(AVG(order_category_revenue), 2) AS avg_order_value
FROM (
    SELECT
        o.order_id,
        p.category,
        SUM(oi.quantity * p.price) AS order_category_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    GROUP BY o.order_id, p.category
) AS order_category_totals
GROUP BY category
ORDER BY avg_order_value DESC;


-- 9. Which customers haven't placed an order in the last 90 days?
-- Practice: subquery / NOT IN, date arithmetic
-- "Today" is treated as the latest order date in the dataset for reproducibility.
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city,
    c.state,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, customer_name, c.city, c.state
HAVING last_order_date IS NULL
    OR last_order_date < DATE((SELECT MAX(order_date) FROM orders), '-90 days')
ORDER BY last_order_date;


-- 10. What percentage of total revenue comes from the top 10 customers?
-- Practice: CTE, window-style aggregation, subquery for grand total
WITH customer_totals AS (
    SELECT
        c.customer_id,
        SUM(oi.quantity * p.price) AS total_spent
    FROM customers c
    JOIN orders o       ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    GROUP BY c.customer_id
),
ranked AS (
    SELECT
        total_spent,
        ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS rnk
    FROM customer_totals
)
SELECT
    ROUND(SUM(CASE WHEN rnk <= 10 THEN total_spent ELSE 0 END), 2) AS top_10_revenue,
    ROUND(SUM(total_spent), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN rnk <= 10 THEN total_spent ELSE 0 END) / SUM(total_spent),
        2
    ) AS pct_of_total_revenue
FROM ranked;

-- 11. Month-over-month revenue growth
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS year_month,
        SUM(oi.quantity * p.price) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY year_month
)

SELECT
    year_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue) OVER (ORDER BY year_month),
        2
    ) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
        / LAG(revenue) OVER (ORDER BY year_month),
        2
    ) AS growth_percentage
FROM monthly_revenue
ORDER BY year_month;


-- 12. Items that are frequently bought together
WITH unique_items AS (
    SELECT DISTINCT
        order_id,
        product_id
    FROM order_items
)

SELECT
    p1.product_name AS product_1,
    p2.product_name AS product_2,
    COUNT(*) AS times_bought_together
FROM unique_items oi1
JOIN unique_items oi2
    ON oi1.order_id = oi2.order_id
    AND oi1.product_id < oi2.product_id
JOIN products p1
    ON oi1.product_id = p1.product_id
JOIN products p2
    ON oi2.product_id = p2.product_id
GROUP BY
    oi1.product_id,
    oi2.product_id
ORDER BY
    times_bought_together DESC;