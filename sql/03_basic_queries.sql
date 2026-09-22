-- ============================================================================
-- 03_basic_queries.sql — LEVELS 1-3: SELECT, WHERE, ORDER BY
-- Business Request 2: "What does our menu actually look like, and which
-- pizzas are our most/least expensive?"
--
-- Practice problems for these levels live in docs/sql-exercises/, answers
-- in docs/sql-solutions/. This file is the TAUGHT reference: read it,
-- run each query, compare the result to the comment above it.
-- ============================================================================
SET search_path TO pizza;

-- ----------------------------------------------------------------------------
-- LEVEL 1: SELECT
-- Concept: SELECT chooses which columns come back. * means "all columns" —
-- fine for exploring, but real queries should name only the columns they
-- need (readability, and less data moved over the wire).
-- ----------------------------------------------------------------------------

-- Q: What does the raw pizzas table look like?
SELECT * FROM pizzas LIMIT 5;

-- Q: What pizza flavors and categories exist? (specific columns + alias)
SELECT
    name     AS pizza_name,
    category AS pizza_category
FROM pizza_types
ORDER BY pizza_name;

-- Q: What categories do we sell, with no repeats? (DISTINCT)
SELECT DISTINCT category FROM pizza_types;

-- Q: What sizes do we sell? (DISTINCT on a different table)
SELECT DISTINCT size FROM pizzas ORDER BY size;

-- Q: What would a 20% price increase look like? (calculated column)
SELECT
    pizza_name_id,
    price                       AS current_price,
    ROUND(price * 1.20, 2)      AS price_plus_20pct
FROM pizzas
LIMIT 10;

-- ----------------------------------------------------------------------------
-- LEVEL 2: WHERE
-- Concept: WHERE filters ROWS before they're returned. Runs before
-- SELECT's column list is applied, conceptually — you can filter on a
-- column you don't even display.
-- ----------------------------------------------------------------------------

-- Q: Which pizzas belong to the 'Veggie' category? (equality)
SELECT name, category FROM pizza_types WHERE category = 'Veggie';

-- Q: Which pizzas are NOT Classic? (inequality)
SELECT name, category FROM pizza_types WHERE category <> 'Classic';

-- Q: Which large ('L') pizzas cost more than $16.00? (AND)
SELECT pizza_name_id, size, price
FROM pizzas
WHERE size = 'L' AND price > 16.00
ORDER BY price DESC;

-- Q: Which pizzas are either Veggie or Chicken? (OR, and the cleaner IN)
SELECT name, category FROM pizza_types WHERE category = 'Veggie' OR category = 'Chicken';
SELECT name, category FROM pizza_types WHERE category IN ('Veggie', 'Chicken');

-- Q: Which pizzas are mid-priced, between $12 and $18? (BETWEEN is inclusive)
SELECT pizza_name_id, price FROM pizzas WHERE price BETWEEN 12 AND 18 ORDER BY price;

-- Q: Which pizzas have "Chicken" in their name? (LIKE + wildcard)
SELECT name FROM pizza_types WHERE name LIKE '%Chicken%';

-- Q: Which orders were placed on exactly March 15, 2015? (date equality)
SELECT order_id, order_date, order_time FROM orders WHERE order_date = '2015-03-15';

-- Q: IS NULL / IS NOT NULL — even though this dataset has zero nulls
-- (verified in 02_data_quality.sql), you must still know this syntax:
-- `WHERE column = NULL` NEVER matches anything, because NULL means
-- "unknown," and unknown compared to anything is also unknown, not true.
SELECT * FROM orders WHERE order_date IS NULL;      -- always empty here
SELECT * FROM orders WHERE order_date IS NOT NULL LIMIT 3;

-- ----------------------------------------------------------------------------
-- LEVEL 3: ORDER BY
-- Concept: ORDER BY sorts the RESULT, not the table. Default is ascending;
-- use DESC for descending. You can sort by more than one column.
-- ----------------------------------------------------------------------------

-- Q: What are our 5 most expensive pizzas (any size)?
SELECT pizza_name_id, size, price FROM pizzas ORDER BY price DESC LIMIT 5;

-- Q: What are our 5 cheapest pizzas?
SELECT pizza_name_id, size, price FROM pizzas ORDER BY price ASC LIMIT 5;

-- Q: List every SKU sorted by category, then by price within category
-- (multi-column sort — first key breaks ties with the second).
SELECT pt.category, p.pizza_name_id, p.price
FROM pizzas p
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
ORDER BY pt.category ASC, p.price DESC
LIMIT 15;

-- Q: Which single order line-item generated the most revenue?
SELECT order_details_id, order_id, pizza_name_id, quantity, total_price
FROM order_details
ORDER BY total_price DESC
LIMIT 1;
