# SQL Solutions — Levels 4-6: Aggregations, GROUP BY, HAVING

---

## Level 4 — Aggregations

### 🟢 Warm-up
```sql
SELECT COUNT(DISTINCT size) FROM pizza.pizzas;      -- 5
SELECT COUNT(*) FROM pizza.orders;                  -- 21350
```

### 🟡 Analyst
```sql
SELECT
    SUM(total_price)       AS total_revenue,
    ROUND(AVG(total_price), 2) AS avg_line_item_value
FROM pizza.order_details;
```
**Result:** total_revenue = 817,860.05; avg_line_item_value = 16.82.

### 🔴 Business Challenge
```sql
SELECT
    SUM(total_price)  AS actual_revenue,
    SUM(quantity) * 15 AS hypothetical_flat15_revenue
FROM pizza.order_details;
```
**Result:** actual = $817,860.05; hypothetical flat-$15 = $743,610.00.
**Explanation:** Quantity sold (49,574 pizzas) is the same in both
scenarios — only price changes. The actual, size/flavor-based pricing
generated about **$74,250 (≈10%) more** than a flat $15 would have. This
is exactly the kind of question a stakeholder asks in plain English
("what if we simplified pricing?") that only becomes answerable once you
can separate "what varies" (price) from "what doesn't" (units sold) in
the same query.

---

## Level 5 — GROUP BY

### 🟢 Warm-up
```sql
SELECT p.size, SUM(od.total_price) AS revenue
FROM pizza.order_details od
JOIN pizza.pizzas p ON od.pizza_name_id = p.pizza_name_id
GROUP BY p.size
ORDER BY revenue DESC;
```
**Result:** L = $375,318.70, M = $249,382.25, S = $178,076.50,
XL = $14,076.00, XXL = $1,006.60.

### 🟡 Analyst
```sql
WITH order_values AS (
    SELECT o.order_id, o.order_date, SUM(od.total_price) AS order_value
    FROM pizza.orders o
    JOIN pizza.order_details od ON o.order_id = od.order_id
    GROUP BY o.order_id, o.order_date
)
SELECT
    TO_CHAR(order_date, 'Day')          AS day_of_week,
    ROUND(AVG(order_value), 2)           AS avg_order_value
FROM order_values
GROUP BY day_of_week, EXTRACT(ISODOW FROM order_date)
ORDER BY EXTRACT(ISODOW FROM order_date);
```
**Result:** Ranges narrowly from $37.58 (Monday) to $38.90 (Saturday).
**Explanation:** The inner CTE first collapses `order_details` to one row
per order (summing all its line-items) — only THEN do we average across
orders by day. Grouping directly on `order_details` without this step
would average individual pizza prices, not whole-order values — a subtly
wrong answer to a different question.
**Insight:** Order VALUE barely varies by day (a ~$1.30 spread) even though
order COUNT (Level 6) varies much more by day — busier days bring more
orders, not bigger ones.

### 🔴 Business Challenge
```sql
-- Top hours by revenue
SELECT
    EXTRACT(HOUR FROM o.order_time)::int AS order_hour,
    SUM(od.total_price)                   AS revenue
FROM pizza.orders o
JOIN pizza.order_details od ON o.order_id = od.order_id
GROUP BY order_hour ORDER BY revenue DESC LIMIT 3;

-- Top hours by order count
SELECT
    EXTRACT(HOUR FROM o.order_time)::int AS order_hour,
    COUNT(DISTINCT o.order_id)            AS n_orders
FROM pizza.orders o
JOIN pizza.order_details od ON o.order_id = od.order_id
GROUP BY order_hour ORDER BY n_orders DESC LIMIT 3;
```
**Result:** Both rankings put **12:00 (noon)** in 1st place (~$111,878
revenue, 2,520 orders), followed by 13:00, then 18:00.
**Explanation/Insight:** Here the two rankings agree — the lunch rush at
noon is both the busiest AND the highest-revenue hour, so staffing for
order count and staffing for revenue point the same direction. That
agreement isn't guaranteed in every dataset (a high-order-count hour full
of small orders could lose to a lower-count hour full of large ones) —
which is exactly why the question was worth checking rather than assuming.

---

## Level 6 — HAVING

### 🟢 Warm-up
```sql
SELECT pt.category, SUM(od.quantity) AS units
FROM pizza.order_details od
JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.category
HAVING SUM(od.quantity) > 3000
ORDER BY units DESC;
```
**Result:** All 4 categories qualify (Classic 14,888 down to Chicken
11,050) — HAVING correctly returns all of them because they all clear the
bar, not because we assumed it.

### 🟡 Analyst
```sql
SELECT pt.name, ROUND(AVG(od.total_price), 2) AS avg_line_item_value
FROM pizza.order_details od
JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
HAVING AVG(od.total_price) > 17
ORDER BY avg_line_item_value DESC;
```
**Result:** 17 of 32 flavors qualify, led by The Brie Carre Pizza ($24.14).

### 🔴 Business Challenge
```sql
SELECT
    pt.name,
    COUNT(DISTINCT od.order_id) AS n_orders,
    ROUND(AVG(od.total_price), 2) AS avg_line_item_value
FROM pizza.order_details od
JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
HAVING COUNT(DISTINCT od.order_id) > 300 AND AVG(od.total_price) > 15
ORDER BY n_orders DESC;
```
**Result:** 27 of 32 flavors qualify.
**Explanation:** `COUNT(DISTINCT order_id)` (not `COUNT(*)`) is required
because one order can contain the same flavor more than once across
different sizes/line-items — `COUNT(*)` would overcount how many distinct
orders actually included the flavor.
**Insight:** The 5 flavors that do NOT qualify — The Pepperoni Pizza (2,278
orders), The Hawaiian Pizza (2,280 orders), The Big Meat Pizza (1,811
orders), The Pepperoni Mushroom & Peppers Pizza, and The Green Garden
Pizza — all fail on the PRICE condition (avg $12.68-$14.14), not the order
count condition; several are actually among our most popular flavors by
order count. That's a genuinely useful, counter-intuitive finding: our
best-selling flavors tend to be our cheapest ones, so "reliable seller"
(popular) and "premium" (high ticket) are two different groups of
products — a menu strategist would treat them differently rather than
assuming popular always means high-value.
