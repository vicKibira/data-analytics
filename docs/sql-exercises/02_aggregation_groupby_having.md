# SQL Exercises — Levels 4-6: Aggregations, GROUP BY, HAVING

Reference: `sql/04_aggregation.sql`. Solutions: `docs/sql-solutions/02_aggregation_groupby_having.md`.

---

## Level 4 — Aggregations

### 🟢 Warm-up
**Business Question:** "How many distinct sizes do we offer, and how many
orders have we taken in total?"
**Your Task:** Two separate single-number queries: `COUNT(DISTINCT size)`
on `pizzas`, and `COUNT(*)` on `orders`.
**Expected Output:** 5 sizes; 21,350 orders.

### 🟡 Analyst
**Business Question:** "Give finance total revenue and the average
line-item value in one query."
**Your Task:** `SUM` and `AVG` on `order_details.total_price`, in a single
`SELECT`.
**Expected Output:** total ≈ $817,860.05; average ≈ $16.82.

### 🔴 Business Challenge
**Business Question:** "Finance is debating switching to a flat $15 price
for every pizza regardless of size or flavor. Before they decide, show
them: what was ACTUAL 2015 revenue, and what would revenue have been under
a flat-$15 policy (same quantities sold)?"
**Your Task:** Think about what stays the same (units sold) and what
changes (price) between the two scenarios before writing one query that
returns both numbers side by side.
**Expected Output:** Two columns, one row. Which scenario made more money?
By how much (in dollars and as a percentage)?

---

## Level 5 — GROUP BY

### 🟢 Warm-up
**Business Question:** "How much revenue does each pizza size generate?"
**Your Task:** `GROUP BY size`, `SUM(total_price)`, joined from
`order_details` to `pizzas`.
**Expected Output:** 5 rows; L should be the largest by a wide margin.

### 🟡 Analyst
**Business Question:** "Does the average order's value change depending on
the day of the week?"
**Your Task:** First compute each order's total value (one row per
`order_id`), THEN group those order totals by day of week and average
them. (Hint: this needs a subquery or CTE — grouping by day directly on
`order_details` would average line-items, not whole orders. If CTEs feel
unfamiliar, skim the intro in `sql/06_ctes.sql` — you're allowed to borrow
the pattern early.)
**Expected Output:** 7 rows; values should all be fairly close together
(within about a dollar of each other) — a useful finding in itself.

### 🔴 Business Challenge
**Business Question:** "Ops wants to know: is the busiest hour of the day
(by order COUNT) also the highest-revenue hour? If they're different
hours, staffing plans based on order count alone could miss the real
revenue peak."
**Your Task:** Write two queries — one ranking hours by total revenue, one
ranking hours by distinct order count — and compare the top 3 of each.
**Expected Output:** Two 3-row result sets. State in a comment whether the
#1 hour matches between the two rankings.

---

## Level 6 — HAVING

### 🟢 Warm-up
**Business Question:** "Which pizza categories sold more than 3,000 pizzas
(units) in the year?"
**Your Task:** `GROUP BY category`, `SUM(quantity)`, `HAVING SUM(quantity)
> 3000`.
**Expected Output:** All 4 categories qualify — but the query should still
use `HAVING`, not a hardcoded assumption.

### 🟡 Analyst
**Business Question:** "Which pizza flavors have an average line-item
value above $17? These are candidates for a 'premium' marketing push."
**Your Task:** `GROUP BY` flavor name, `HAVING AVG(total_price) > 17`.
**Expected Output:** 17 of the 32 flavors qualify.

### 🔴 Business Challenge
**Business Question:** "Identify 'reliable sellers': flavors ordered in
more than 300 distinct orders AND averaging more than $15 per line-item.
We want flavors that are both popular AND not being heavily discounted or
under-ordered."
**Your Task:** This needs `COUNT(DISTINCT order_id)` and `AVG(total_price)`
combined with `AND` inside a single `HAVING` clause — reason about why
`COUNT(DISTINCT order_id)`, not `COUNT(*)`, is the right measure of
"ordered in how many orders" before you write it.
**Expected Output:** 27 of the 32 flavors qualify — a useful signal about
which 5 flavors DON'T, and why a manager might want to investigate them.
