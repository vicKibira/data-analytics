# SQL Solutions — Levels 9-10: CTEs, Window Functions

---

## Level 9 — CTEs

### 🟢 Warm-up
```sql
WITH category_revenue AS (
    SELECT pt.category, SUM(od.total_price) AS revenue
    FROM pizza.order_details od
    JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.category
)
SELECT * FROM category_revenue WHERE revenue > 150000 ORDER BY revenue DESC;
```
**Result:** Classic $220,053.10, Supreme $208,197.00, Chicken $195,919.50,
Veggie $193,690.45 — all 4 qualify.

### 🟡 Analyst
```sql
WITH daily_revenue AS (
    SELECT o.order_date, SUM(od.total_price) AS revenue
    FROM pizza.order_details od
    JOIN pizza.orders o ON od.order_id = o.order_id
    GROUP BY o.order_date
),
best_day AS (
    SELECT order_date FROM daily_revenue ORDER BY revenue DESC LIMIT 1
)
SELECT pt.name, p.size, od.quantity, od.total_price
FROM pizza.order_details od
JOIN pizza.orders o        ON od.order_id       = o.order_id
JOIN pizza.pizzas p        ON od.pizza_name_id   = p.pizza_name_id
JOIN pizza.pizza_types pt  ON p.pizza_type_id    = pt.pizza_type_id
WHERE o.order_date = (SELECT order_date FROM best_day)
ORDER BY od.total_price DESC;
```
**Result:** Best day = **2015-11-27** (the day after Thanksgiving in the
U.S.), revenue $4,422.45, 259 line-items. Top single line-item: 2 Large
Italian Capocollo pizzas, $41.00.
**Explanation:** The second `best_day` CTE builds directly on the first —
this chaining is the core CTE skill: each step is simple on its own, and
the final query reads almost like a sentence ("from the best day, show me
what sold").

### 🔴 Business Challenge
```sql
WITH category_revenue AS (
    SELECT pt.category, SUM(od.total_price) AS revenue
    FROM pizza.order_details od
    JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.category
)
SELECT
    category,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS pct_of_total
FROM category_revenue
ORDER BY revenue DESC;
```
**Result:** Classic 26.9%, Supreme 25.5%, Chicken 24.0%, Veggie 23.7% —
sums to 100.1% only due to rounding each row independently.
**Explanation:** `SUM(revenue) OVER ()` with no `PARTITION BY` and no
`ORDER BY` computes ONE total across every row in the CTE's output and
attaches that same total to every row — turning what would otherwise need
a second query (or a manual division) into a single pass.

---

## Level 10 — Window Functions (Analyst Challenge)

### 🟢 Warm-up
```sql
SELECT
    pt.name,
    SUM(od.quantity) AS units_sold,
    RANK() OVER (ORDER BY SUM(od.quantity) DESC) AS rnk
FROM pizza.order_details od
JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
GROUP BY pt.name
ORDER BY rnk;
```
**Result:** 32 rows; #1 The Classic Deluxe Pizza (2,453 units), #2 The
Barbecue Chicken Pizza (2,432), #3 The Hawaiian Pizza (2,422).

### 🟡 Analyst
```sql
WITH ranked AS (
    SELECT
        pt.category,
        pt.name,
        SUM(od.total_price) AS revenue,
        RANK() OVER (PARTITION BY pt.category ORDER BY SUM(od.total_price) DESC) AS rnk
    FROM pizza.order_details od
    JOIN pizza.pizzas p       ON od.pizza_name_id = p.pizza_name_id
    JOIN pizza.pizza_types pt ON p.pizza_type_id  = pt.pizza_type_id
    GROUP BY pt.category, pt.name
)
SELECT * FROM ranked WHERE rnk = 1;
```
**Result (one flagship per category):**
Chicken → The Thai Chicken Pizza ($43,434.25) · Classic → The Classic
Deluxe Pizza ($38,180.50) · Supreme → The Spicy Italian Pizza ($34,831.25)
· Veggie → The Four Cheese Pizza ($32,265.70).
**Explanation:** `PARTITION BY category` restarts the ranking for every
category independently — without it, a single `RANK()` would only surface
the overall #1 (a Chicken pizza), hiding the best performer in every other
category.

### 🔴 Business Challenge
```sql
WITH daily AS (
    SELECT o.order_date, SUM(od.total_price) AS revenue
    FROM pizza.order_details od
    JOIN pizza.orders o ON od.order_id = o.order_id
    GROUP BY o.order_date
),
rolling AS (
    SELECT
        order_date,
        revenue,
        AVG(revenue) OVER (ORDER BY order_date
                            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day_avg
    FROM daily
)
SELECT
    order_date,
    revenue,
    ROUND(rolling_7day_avg, 2) AS rolling_7day_avg,
    ROUND(revenue - rolling_7day_avg, 2) AS excess_over_trend
FROM rolling
ORDER BY excess_over_trend DESC
LIMIT 5;
```
**Result:** Top day is **2015-11-26** (Thanksgiving Day itself), revenue
$4,405.95 vs. a trailing 7-day average of $2,472.16 — about **$1,934
above trend**, the single biggest spike in the dataset. The very next day,
2015-11-27, is also in the top 3 (from Level 9's "best single day"
question) — together they show a two-day Thanksgiving-week spike, not a
one-off fluke.
**Explanation:** `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` defines a
7-row moving window ending at the current row, which is what makes this
a genuine "trailing average," not an average of the whole year. This is
the query pattern that would feed a real anomaly-detection or promotion-
effectiveness analysis in a production analytics team.
