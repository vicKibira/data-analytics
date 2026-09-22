-- ============================================================================
-- 08_business_questions.sql
-- Business Request 6: "What should management know about our sales
-- performance?" — a self-contained set of queries an analyst could actually
-- hand to a stakeholder, each combining several concepts from Levels 1-10.
--
-- This file is the bridge into Phase 3: every query here is also produced
-- again in notebooks/04_business_analysis.ipynb via src/extract_data.py,
-- so you can compare "answer it in SQL" against "answer it in pandas."
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- SALES PERFORMANCE
-- ----------------------------------------------------------------------------

-- Q: Headline KPIs — total revenue, total orders, total pizzas sold, AOV.
SELECT
    SUM(od.total_price)                              AS total_revenue,
    COUNT(DISTINCT od.order_id)                       AS total_orders,
    SUM(od.quantity)                                  AS total_pizzas_sold,
    ROUND(SUM(od.total_price) / COUNT(DISTINCT od.order_id), 2) AS avg_order_value
FROM order_details od;

-- Q: How has revenue trended month over month across 2015?
SELECT
    DATE_TRUNC('month', o.order_date)::date AS sales_month,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
GROUP BY sales_month
ORDER BY sales_month;

-- ----------------------------------------------------------------------------
-- PRODUCT PERFORMANCE
-- ----------------------------------------------------------------------------

-- Q: Top 5 pizzas by revenue, and top 5 by units sold — are they the same
-- pizzas? (Answers "are high-volume pizzas necessarily high-revenue pizzas?")
WITH flavor_sales AS (
    SELECT
        pt.name AS pizza_name,
        SUM(od.quantity)    AS units_sold,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
)
SELECT 'Top 5 by revenue' AS ranking, pizza_name, units_sold, revenue
FROM flavor_sales ORDER BY revenue DESC LIMIT 5;

WITH flavor_sales AS (
    SELECT
        pt.name AS pizza_name,
        SUM(od.quantity)    AS units_sold,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
)
SELECT 'Top 5 by units sold' AS ranking, pizza_name, units_sold, revenue
FROM flavor_sales ORDER BY units_sold DESC LIMIT 5;

-- Q: Which SIZE contributes the most revenue?
SELECT
    p.size,
    SUM(od.quantity)    AS units_sold,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN pizzas p ON od.pizza_name_id = p.pizza_name_id
GROUP BY p.size
ORDER BY revenue DESC;

-- Q: Product concentration — what share of total revenue comes from just
-- the top 5 flavors (out of 32)? A large number here means the business is
-- concentrated in a few bestsellers, worth knowing for menu-risk planning.
WITH flavor_revenue AS (
    SELECT pt.name AS pizza_name, SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
),
ranked AS (
    SELECT *, RANK() OVER (ORDER BY revenue DESC) AS rnk
    FROM flavor_revenue
)
SELECT
    ROUND(100.0 * SUM(revenue) FILTER (WHERE rnk <= 5) / SUM(revenue), 1) AS pct_revenue_from_top5_flavors
FROM ranked;

-- ----------------------------------------------------------------------------
-- ORDER / TIME BEHAVIOR
-- ----------------------------------------------------------------------------

-- Q: Which day of week is busiest, by order count?
SELECT
    TO_CHAR(order_date, 'Day')  AS day_of_week,
    COUNT(*)                     AS n_orders
FROM orders
GROUP BY day_of_week, EXTRACT(ISODOW FROM order_date)
ORDER BY EXTRACT(ISODOW FROM order_date);

-- Q: Which hour of day is busiest?
SELECT
    EXTRACT(HOUR FROM order_time)::int AS order_hour,
    COUNT(*) AS n_orders
FROM orders
GROUP BY order_hour
ORDER BY order_hour;

-- Q: How large is a typical order (in pizzas), and how much does that vary?
WITH order_sizes AS (
    SELECT order_id, SUM(quantity) AS pizzas_in_order
    FROM order_details
    GROUP BY order_id
)
SELECT
    ROUND(AVG(pizzas_in_order), 2) AS avg_pizzas_per_order,
    MIN(pizzas_in_order)            AS smallest_order,
    MAX(pizzas_in_order)            AS largest_order
FROM order_sizes;

-- ----------------------------------------------------------------------------
-- BUSINESS OPPORTUNITIES
-- ----------------------------------------------------------------------------

-- Q: Which SKUs (flavor + size) sell in meaningful volume (top half by
-- units) but rank in the bottom half by revenue-per-unit? These are
-- candidates for a price review.
WITH sku_sales AS (
    SELECT
        p.pizza_name_id,
        pt.name AS pizza_name,
        p.size,
        p.price,
        SUM(od.quantity) AS units_sold
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY p.pizza_name_id, pt.name, p.size, p.price
),
ranked AS (
    SELECT
        *,
        NTILE(2) OVER (ORDER BY units_sold DESC) AS volume_half,   -- 1 = top half
        NTILE(2) OVER (ORDER BY price ASC)        AS price_half     -- 1 = cheaper half
    FROM sku_sales
)
SELECT pizza_name, size, price, units_sold
FROM ranked
WHERE volume_half = 1 AND price_half = 1
ORDER BY units_sold DESC;

-- Q: Are there any pizza flavors present in the catalog that never appear
-- in order_details at all? (LEFT JOIN, revisited from 05_joins.sql, as a
-- final "opportunity" check — zero rows back here confirms every flavor in
-- our 32-flavor menu sold at least once in 2015.)
SELECT pt.name
FROM pizza_types pt
LEFT JOIN pizzas p        ON pt.pizza_type_id = p.pizza_type_id
LEFT JOIN order_details od ON p.pizza_name_id  = od.pizza_name_id
WHERE od.order_details_id IS NULL;
