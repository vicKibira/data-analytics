# SQL Solutions — Levels 7-8: CASE, JOINs

---

## Level 7 — CASE

### 🟢 Warm-up
```sql
SELECT
    pizza_name_id,
    size,
    CASE WHEN size = 'S' THEN 'Small Format' ELSE 'Large Format' END AS format
FROM pizza.pizzas;
```
**Result:** 30 Small Format, 61 Large Format.

### 🟡 Analyst
```sql
SELECT
    CASE WHEN EXTRACT(ISODOW FROM order_date) IN (6, 7) THEN 'Weekend'
         ELSE 'Weekday' END AS day_type,
    COUNT(*) AS n_orders
FROM pizza.orders
GROUP BY day_type;
```
**Result:** Weekday = 15,514 orders, Weekend = 5,836 orders.
**Explanation:** There are 5 weekdays vs. 2 weekend days per week, so
raw counts naturally favor weekdays — the more interesting business
question (answered in the EDA/dashboard phase) is orders PER DAY on
average, not the raw total.

### 🔴 Business Challenge
```sql
-- Chosen cutoffs, based on observed min $11,589 / avg $25,558 / max $43,434:
-- Low    < $20,000  (below the midpoint of the observed range)
-- Medium $20,000-$32,000 (spans the average)
-- High   > $32,000
WITH flavor_revenue AS (
    SELECT pt.name, SUM(od.total_price) AS revenue
    FROM pizza.order_details od
    JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.name
)
SELECT
    CASE
        WHEN revenue < 20000 THEN 'Low'
        WHEN revenue < 32000 THEN 'Medium'
        ELSE 'High'
    END AS revenue_tier,
    COUNT(*) AS n_flavors
FROM flavor_revenue
GROUP BY revenue_tier;
```
**Result:** Low = 11 flavors, Medium = 12 flavors, High = 9 flavors — a
reasonably balanced three-way split. (Your exact cutoffs may differ from
these; what matters is that you looked at MIN/AVG/MAX first instead of
guessing round numbers, and ended up with groups that are actually useful
for a manager to act on.)

---

## Level 8 — JOINs

### 🟢 Warm-up
```sql
SELECT pt.name, pt.category, p.size, od.quantity
FROM pizza.order_details od
JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
ORDER BY od.quantity DESC
LIMIT 10;
```
**Result:** 10 rows, all at `quantity = 4` — the maximum quantity value in
this dataset (verified in `data/README.md`).

### 🟡 Analyst
```sql
SELECT
    o.order_time,
    pt.name AS pizza_name,
    pt.category,
    od.quantity
FROM pizza.order_details od
JOIN pizza.orders o        ON od.order_id       = o.order_id
JOIN pizza.pizzas p        ON od.pizza_name_id   = p.pizza_name_id
JOIN pizza.pizza_types pt  ON p.pizza_type_id    = pt.pizza_type_id
WHERE o.order_date = '2015-06-15'
ORDER BY o.order_time;
```
**Result:** 150 rows.

### 🔴 Business Challenge
```sql
SELECT pt.name, COUNT(DISTINCT p.size) AS n_sizes,
       STRING_AGG(DISTINCT p.size, ',') AS sizes_offered
FROM pizza.pizzas p
JOIN pizza.pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
GROUP BY pt.name
HAVING COUNT(DISTINCT p.size) = 1
ORDER BY pt.name;
```
**Result:** 3 flavors — The Big Meat Pizza (S only), The Brie Carre Pizza
(S only), The Five Cheese Pizza (L only).
**Explanation:** Everything else in this query is familiar (JOIN, GROUP
BY), but the business insight only appears once you filter groups down
with `HAVING COUNT(DISTINCT size) = 1` — a reminder that JOINs rarely
show up alone in real analyst work; they're almost always combined with
the aggregation concepts from Levels 4-6.
