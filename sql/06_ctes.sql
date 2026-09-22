-- ============================================================================
-- 06_ctes.sql — LEVEL 9: Common Table Expressions (CTEs)
-- Business Request 5: "Are there products that sell frequently but
-- contribute little revenue?"
--
-- WHY CTEs
-- The query below needs several steps: (1) compute per-flavor units sold
-- and revenue, (2) compute each flavor's SHARE of total units and total
-- revenue, (3) compare the two shares. Nesting that as subqueries inside
-- subqueries becomes unreadable fast. A CTE (`WITH name AS (...)`) lets you
-- name each step and read the final SELECT almost like English — this is
-- the single biggest reason analysts reach for CTEs over deeply nested
-- subqueries.
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- Start simple: one CTE, used once.
-- ----------------------------------------------------------------------------

-- Q: What is each pizza flavor's total revenue? (same result as the GROUP BY
-- in 04_aggregation.sql — now expressed as a named, reusable step)
WITH flavor_revenue AS (
    SELECT
        pt.name AS pizza_name,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
)
SELECT * FROM flavor_revenue ORDER BY revenue DESC LIMIT 10;

-- ----------------------------------------------------------------------------
-- Two CTEs, the second building on the first — this is the pattern used to
-- answer Business Request 5.
-- ----------------------------------------------------------------------------

-- Q: Which pizza flavors sell a lot of UNITS but contribute relatively
-- little REVENUE — i.e. where volume rank is much better than revenue rank?
WITH flavor_sales AS (
    SELECT
        pt.name AS pizza_name,
        SUM(od.quantity)    AS units_sold,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
),
flavor_ranks AS (
    SELECT
        pizza_name,
        units_sold,
        revenue,
        RANK() OVER (ORDER BY units_sold DESC) AS volume_rank,
        RANK() OVER (ORDER BY revenue DESC)    AS revenue_rank
    FROM flavor_sales
)
SELECT *
FROM flavor_ranks
WHERE volume_rank < revenue_rank          -- sells better than it earns
ORDER BY (revenue_rank - volume_rank) DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- CTEs also make date-based questions readable: category revenue by month,
-- built in two clear steps.
-- ----------------------------------------------------------------------------

-- Q: What is each category's monthly revenue trend?
WITH monthly_category_sales AS (
    SELECT
        DATE_TRUNC('month', o.order_date)::date AS sales_month,
        pt.category,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN orders o        ON od.order_id       = o.order_id
    JOIN pizzas p         ON od.pizza_name_id  = p.pizza_name_id
    JOIN pizza_types pt   ON p.pizza_type_id   = pt.pizza_type_id
    GROUP BY sales_month, pt.category
)
SELECT * FROM monthly_category_sales
ORDER BY sales_month, category
LIMIT 12;

-- ----------------------------------------------------------------------------
-- Business Request 6 preview: a single CTE-built query management could
-- read top-to-bottom as an executive summary.
-- ----------------------------------------------------------------------------
WITH order_totals AS (
    SELECT order_id, SUM(total_price) AS order_value
    FROM order_details
    GROUP BY order_id
)
SELECT
    COUNT(*)                          AS total_orders,
    ROUND(AVG(order_value), 2)         AS avg_order_value,
    ROUND(MIN(order_value), 2)         AS smallest_order,
    ROUND(MAX(order_value), 2)         AS largest_order
FROM order_totals;
