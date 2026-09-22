-- ============================================================================
-- 07_advanced_analysis.sql — LEVEL 10: Window Functions ("Analyst Challenge")
-- Business Request: "Rank our products, and show management how revenue
-- has trended month over month, without collapsing the daily detail."
--
-- WHY WINDOW FUNCTIONS (AND WHY THEY'RE MARKED "ANALYST CHALLENGE")
-- GROUP BY collapses rows. A window function computes a value ACROSS a set
-- of related rows (a "window") while still returning one row per INPUT row
-- — e.g. "this pizza's rank among all pizzas" attached to every row, or a
-- running total that grows day by day. This is genuinely harder to reason
-- about than GROUP BY and is not required to complete the core course, but
-- it is exactly what separates "can write a report" from "can build a
-- trend/ranking analysis," so every serious analyst eventually needs it.
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- RANK() / ROW_NUMBER() — assign a rank to each row within a window,
-- without collapsing the underlying rows.
-- ----------------------------------------------------------------------------

-- Q: Rank every pizza flavor by revenue, without losing per-flavor detail.
-- RANK() gives ties the same rank and skips the next number; ROW_NUMBER()
-- never ties, even if the underlying values do.
SELECT
    pt.name AS pizza_name,
    SUM(od.total_price) AS revenue,
    RANK()       OVER (ORDER BY SUM(od.total_price) DESC) AS revenue_rank,
    ROW_NUMBER() OVER (ORDER BY SUM(od.total_price) DESC) AS revenue_row_num
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
ORDER BY revenue_rank
LIMIT 10;

-- Q: Within EACH category, what is that category's #1 best-selling pizza
-- by revenue? (PARTITION BY resets the ranking for every category — this
-- is the window-function equivalent of "GROUP BY category, then rank
-- inside each group.")
WITH ranked AS (
    SELECT
        pt.category,
        pt.name AS pizza_name,
        SUM(od.total_price) AS revenue,
        RANK() OVER (PARTITION BY pt.category ORDER BY SUM(od.total_price) DESC) AS rank_in_category
    FROM order_details od
    JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.category, pt.name
)
SELECT * FROM ranked WHERE rank_in_category = 1;

-- ----------------------------------------------------------------------------
-- RUNNING TOTALS — a window function with an explicit frame
-- (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW).
-- ----------------------------------------------------------------------------

-- Q: Show revenue's cumulative running total across the year, day by day.
WITH daily_revenue AS (
    SELECT o.order_date, SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    GROUP BY o.order_date
)
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (ORDER BY order_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_revenue
FROM daily_revenue
ORDER BY order_date
LIMIT 15;

-- ----------------------------------------------------------------------------
-- PERCENTAGE OF TOTAL — a window function with no ORDER BY, just a full
-- partition, used as a denominator.
-- ----------------------------------------------------------------------------

-- Q: What percentage of TOTAL revenue does each category represent?
SELECT
    pt.category,
    SUM(od.total_price) AS revenue,
    ROUND(
        100.0 * SUM(od.total_price) / SUM(SUM(od.total_price)) OVER (),
        1
    ) AS pct_of_total_revenue
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.category
ORDER BY revenue DESC;

-- ----------------------------------------------------------------------------
-- MONTH-OVER-MONTH COMPARISON — LAG() looks at the PREVIOUS row in the
-- window's order, letting you compute change without a self-join.
-- ----------------------------------------------------------------------------

-- Q: How did monthly revenue change from the previous month?
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_date)::date AS sales_month,
        SUM(od.total_price) AS revenue
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    GROUP BY sales_month
)
SELECT
    sales_month,
    revenue,
    LAG(revenue) OVER (ORDER BY sales_month) AS prior_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY sales_month))
        / NULLIF(LAG(revenue) OVER (ORDER BY sales_month), 0),
        1
    ) AS pct_change_mom
FROM monthly_revenue
ORDER BY sales_month;
