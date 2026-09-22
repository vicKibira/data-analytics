-- ============================================================================
-- 04_aggregation.sql — LEVELS 4-7: Aggregations, GROUP BY, HAVING, CASE
-- Business Request 3: "Which pizzas and categories generate the most
-- revenue? Give management a quick classification of performance."
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- LEVEL 4: AGGREGATIONS (no GROUP BY yet — one number for the whole table)
-- Concept: aggregate functions collapse many rows into one summary value.
-- NULL behavior matters: COUNT(*) counts rows; COUNT(column) counts only
-- non-null values in that column; SUM/AVG/MIN/MAX silently ignore NULLs.
-- This dataset has zero NULLs (verified in 02_data_quality.sql), but the
-- distinction still matters in every real dataset you'll ever query.
-- ----------------------------------------------------------------------------

-- Q: How many orders were placed in total?
SELECT COUNT(*) AS total_orders FROM orders;

-- Q: How many distinct pizza flavors do we sell? (COUNT DISTINCT)
SELECT COUNT(DISTINCT pizza_type_id) AS distinct_flavors FROM pizzas;

-- Q: How many total pizzas were sold (not line-items — actual units)?
SELECT SUM(quantity) AS total_pizzas_sold FROM order_details;

-- Q: What is total revenue for the year?
SELECT SUM(total_price) AS total_revenue FROM order_details;

-- Q: What is the average price of a single line-item?
SELECT ROUND(AVG(total_price), 2) AS avg_line_item_value FROM order_details;

-- Q: What are the cheapest and most expensive SKUs we sell?
SELECT MIN(price) AS cheapest_price, MAX(price) AS most_expensive_price FROM pizzas;

-- Q: Row-level calculation vs. aggregation — NOT the same thing.
-- This returns one row PER line-item (row-level):
SELECT order_details_id, quantity, total_price, ROUND(total_price / quantity, 2) AS price_per_unit
FROM order_details LIMIT 5;
-- This collapses ALL rows into a single summary row (aggregation):
SELECT ROUND(SUM(total_price) / SUM(quantity), 2) AS avg_price_per_pizza FROM order_details;

-- ----------------------------------------------------------------------------
-- LEVEL 5: GROUP BY
-- Concept: GROUP BY splits rows into buckets sharing the same value(s) in
-- the grouped column(s), then applies aggregate functions PER bucket
-- instead of to the whole table. Every non-aggregated column in SELECT
-- must appear in GROUP BY.
-- ----------------------------------------------------------------------------

-- Q: What is revenue by individual pizza flavor? (Business Request 3)
SELECT
    pt.name           AS pizza_name,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
ORDER BY revenue DESC
LIMIT 10;

-- Q: What is revenue by category?
SELECT
    pt.category,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.category
ORDER BY revenue DESC;

-- Q: How many orders were placed on each calendar day? (Business Request 4)
SELECT order_date, COUNT(*) AS n_orders
FROM orders
GROUP BY order_date
ORDER BY order_date
LIMIT 10;

-- Q: How many pizzas (units) were sold per size?
SELECT p.size, SUM(od.quantity) AS units_sold
FROM order_details od
JOIN pizzas p ON od.pizza_name_id = p.pizza_name_id
GROUP BY p.size
ORDER BY units_sold DESC;

-- Q: What is the average price by category? (GROUP BY with AVG)
SELECT pt.category, ROUND(AVG(p.price), 2) AS avg_price
FROM pizzas p
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
GROUP BY pt.category
ORDER BY avg_price DESC;

-- ----------------------------------------------------------------------------
-- LEVEL 6: HAVING
-- Concept: WHERE filters ROWS before grouping; HAVING filters GROUPS after
-- aggregation. You cannot write `WHERE SUM(total_price) > 1000` — SUM
-- doesn't exist yet at the row-filtering stage. HAVING is where that
-- condition belongs.
-- ----------------------------------------------------------------------------

-- Q: Which pizza flavors generated more than $30,000 in revenue?
SELECT
    pt.name AS pizza_name,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
HAVING SUM(od.total_price) > 30000
ORDER BY revenue DESC;

-- Q: Which categories sold more than 10,000 pizzas (units) in the year?
SELECT
    pt.category,
    SUM(od.quantity) AS units_sold
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.category
HAVING SUM(od.quantity) > 10000
ORDER BY units_sold DESC;

-- Q: WHERE + HAVING together: among Large pizzas only, which flavors sold
-- more than 200 units? (WHERE filters rows to size='L' BEFORE grouping;
-- HAVING filters the resulting flavor groups AFTER aggregation)
SELECT
    pt.name AS pizza_name,
    SUM(od.quantity) AS units_sold
FROM order_details od
JOIN pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
WHERE p.size = 'L'
GROUP BY pt.name
HAVING SUM(od.quantity) > 200
ORDER BY units_sold DESC;

-- ----------------------------------------------------------------------------
-- LEVEL 7: CASE
-- Concept: CASE lets you turn continuous or many-valued data into business
-- categories directly in SQL — the same logic an analyst would otherwise
-- write with pandas.cut() or np.select() in Python later.
-- ----------------------------------------------------------------------------

-- Q: Classify every SKU into a price tier management can talk about.
SELECT
    pizza_name_id,
    price,
    CASE
        WHEN price < 12.50 THEN 'Budget'
        WHEN price < 17.50 THEN 'Standard'
        ELSE 'Premium'
    END AS price_tier
FROM pizzas
ORDER BY price;

-- Q: Classify each order as Small / Medium / Large based on how many
-- pizzas it contains.
SELECT
    o.order_id,
    SUM(od.quantity) AS pizzas_in_order,
    CASE
        WHEN SUM(od.quantity) <= 2 THEN 'Small order'
        WHEN SUM(od.quantity) <= 5 THEN 'Medium order'
        ELSE 'Large order'
    END AS order_size
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id
ORDER BY pizzas_in_order DESC
LIMIT 10;

-- Q: Classify orders into a time-of-day bucket (mirrors utils.add_time_features
-- in the Python phase — the same business logic, expressed in SQL first).
SELECT
    order_id,
    order_time,
    CASE
        WHEN order_time < TIME '11:00' THEN 'Morning'
        WHEN order_time < TIME '15:00' THEN 'Lunch'
        WHEN order_time < TIME '18:00' THEN 'Afternoon'
        WHEN order_time < TIME '21:00' THEN 'Dinner'
        ELSE 'Late Night'
    END AS time_of_day
FROM orders
ORDER BY order_time
LIMIT 10;

-- Q: Revenue by price tier — combining CASE with GROUP BY (a preview of how
-- CASE and aggregation compose, used heavily from here on).
SELECT
    CASE
        WHEN p.price < 12.50 THEN 'Budget'
        WHEN p.price < 17.50 THEN 'Standard'
        ELSE 'Premium'
    END AS price_tier,
    SUM(od.total_price) AS revenue
FROM order_details od
JOIN pizzas p ON od.pizza_name_id = p.pizza_name_id
GROUP BY price_tier
ORDER BY revenue DESC;
