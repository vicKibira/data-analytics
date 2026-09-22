-- ============================================================================
-- 05_joins.sql — LEVEL 8: JOINs
-- Business Request: "Our sales data is spread across four related tables.
-- Nearly every real business question needs information from more than
-- one of them at once."
--
-- WHY WE NEED JOINS
-- order_details tells you WHAT was sold and for how much, but not what
-- flavor/category that pizza actually is (that's in pizza_types) or what
-- size/price SKU it was (pizzas) or when it happened (orders). Splitting
-- data into normalized tables (01_schema.sql) avoids repeating the same
-- ingredient list 48,620 times — but it means you must JOIN to get it back.
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- INNER JOIN: only keep rows that match in BOTH tables.
-- Here that's safe because every order_details.pizza_name_id is guaranteed
-- (by the FK constraint) to exist in pizzas — verified in 02_data_quality.sql.
-- ----------------------------------------------------------------------------

-- Q: Show each line-item together with the flavor name and category it sold.
SELECT
    od.order_details_id,
    od.order_id,
    pt.name     AS pizza_name,
    pt.category,
    od.quantity,
    od.total_price
FROM order_details od
INNER JOIN pizzas p        ON od.pizza_name_id = p.pizza_name_id
INNER JOIN pizza_types pt  ON p.pizza_type_id   = pt.pizza_type_id
LIMIT 10;

-- Q: Three-table join to answer: which pizza flavor + size combos sold on
-- 2015-06-15, and what time did each order come in?
SELECT
    o.order_date,
    o.order_time,
    pt.name AS pizza_name,
    p.size,
    od.quantity
FROM order_details od
JOIN orders o       ON od.order_id       = o.order_id
JOIN pizzas p        ON od.pizza_name_id  = p.pizza_name_id
JOIN pizza_types pt  ON p.pizza_type_id   = pt.pizza_type_id
WHERE o.order_date = '2015-06-15'
ORDER BY o.order_time
LIMIT 15;

-- ----------------------------------------------------------------------------
-- LEFT JOIN: keep every row from the LEFT table, even rows with no match
-- on the right. Essential for "which X have never sold" questions, where
-- an INNER JOIN would silently hide the very rows you're looking for.
-- ----------------------------------------------------------------------------

-- Q: Every pizza flavor we sell, and how many units of it were sold — even
-- if that number is zero. (In this dataset every flavor did sell at least
-- once, so the LEFT JOIN and an INNER JOIN happen to return the same rows
-- here — but LEFT JOIN is still the CORRECT choice, because it doesn't
-- silently assume that will always be true. This is the habit that matters:
-- always ask "could the right side legitimately have zero matches?")
SELECT
    pt.name AS pizza_name,
    COALESCE(SUM(od.quantity), 0) AS units_sold
FROM pizza_types pt
LEFT JOIN pizzas p       ON pt.pizza_type_id = p.pizza_type_id
LEFT JOIN order_details od ON p.pizza_name_id = od.pizza_name_id
GROUP BY pt.name
ORDER BY units_sold ASC;

-- Q: Every SKU (flavor + size) and its total revenue, including any SKU
-- that never sold (COALESCE turns a NULL sum into a readable 0).
SELECT
    p.pizza_name_id,
    COALESCE(SUM(od.total_price), 0) AS revenue
FROM pizzas p
LEFT JOIN order_details od ON p.pizza_name_id = od.pizza_name_id
GROUP BY p.pizza_name_id
ORDER BY revenue ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Business Request 5 preview: "Are there products that sell frequently but
-- contribute little revenue?" — needs a join across all 4 tables plus
-- GROUP BY plus two different aggregates at once. This is exactly the shape
-- of query CTEs (06_ctes.sql) exist to make readable.
-- ----------------------------------------------------------------------------
SELECT
    pt.name AS pizza_name,
    SUM(od.quantity)      AS units_sold,
    SUM(od.total_price)   AS revenue,
    ROUND(SUM(od.total_price) / NULLIF(SUM(od.quantity), 0), 2) AS revenue_per_unit
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
ORDER BY units_sold DESC
LIMIT 10;
