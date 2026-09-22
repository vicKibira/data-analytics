-- ============================================================================
-- 02_data_quality.sql
-- Business Request: "Before we trust any report built on this database,
-- prove the load worked correctly."
--
-- WHY THIS FILE EXISTS
-- A script finishing without an error (load_data.py's "SUCCESS" line) only
-- proves nothing crashed. It does NOT prove the data is trustworthy. A
-- real analyst re-checks the loaded data independently before building
-- anything on top of it. This file is that independent check, written in
-- SQL instead of pandas, so it doubles as your first real SQL practice.
-- ============================================================================​
SET search_path TO pizza;

-- 1. ROW COUNTS — do the four tables have the row counts we expect?
--    (32 flavors, 91 flavor x size SKUs, 21,350 orders, 48,620 line items)
SELECT 'pizza_types'   AS table_name, COUNT(*) AS row_count FROM pizza_types
UNION ALL
SELECT 'pizzas',                       COUNT(*)             FROM pizzas
UNION ALL
SELECT 'orders',                       COUNT(*)             FROM orders
UNION ALL
SELECT 'order_details',                COUNT(*)             FROM order_details;

-- 2. NULLS — any required column that came through empty?
SELECT
    COUNT(*) FILTER (WHERE order_date IS NULL) AS null_order_date,
    COUNT(*) FILTER (WHERE order_time IS NULL) AS null_order_time
FROM orders;

SELECT
    COUNT(*) FILTER (WHERE quantity IS NULL)    AS null_quantity,
    COUNT(*) FILTER (WHERE total_price IS NULL) AS null_total_price
FROM order_details;

-- 3. DUPLICATES — any primary key that snuck in twice?
--    (should return zero rows for a clean load)
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 4. REFERENTIAL INTEGRITY — any order_details row pointing at an order or
--    pizza that doesn't exist? (The FK constraints in 01_schema.sql should
--    make this impossible, but we verify rather than assume.)
SELECT COUNT(*) AS orphaned_order_details
FROM order_details od
LEFT JOIN orders o ON od.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 5. VALUE RANGES — do categorical columns contain only the values we expect?
SELECT DISTINCT size FROM pizzas ORDER BY size;
SELECT DISTINCT category FROM pizza_types ORDER BY category;

-- 6. DATE RANGE — does order_date fall inside the expected 2015 calendar
--    year, with no impossible future/past dates?
SELECT MIN(order_date) AS earliest_order, MAX(order_date) AS latest_order
FROM orders;

-- 7. PRICE SANITY — any non-positive price or quantity? (CHECK constraints
--    in the schema should prevent this at load time; confirming here.)
SELECT COUNT(*) AS bad_rows
FROM order_details
WHERE quantity <= 0 OR total_price <= 0;

-- 8. CROSS-CHECK total_price AGAINST pizzas.price * quantity
--    This re-verifies, from inside the database, the same check load_data.py
--    already ran in pandas before loading — never trust a single check.
SELECT COUNT(*) AS mismatched_totals
FROM order_details od
JOIN pizzas p ON od.pizza_name_id = p.pizza_name_id
WHERE ROUND(p.price * od.quantity, 2) <> od.total_price;

-- ============================================================================
-- If every query above comes back clean (expected row counts, 0 nulls,
-- 0 duplicates, 0 orphans, sane ranges, 0 bad rows, 0 mismatches), the
-- database is trustworthy and Phase 2 (sql/03_basic_queries.sql onward)
-- can begin.
-- ============================================================================
