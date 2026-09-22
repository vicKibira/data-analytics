# SQL Exercises — Levels 7-8: CASE, JOINs

Reference: `sql/04_aggregation.sql` (CASE) and `sql/05_joins.sql` (JOIN).
Solutions: `docs/sql-solutions/03_case_joins.md`.

---

## Level 7 — CASE

### 🟢 Warm-up
**Business Question:** "For packaging purposes, classify every SKU as
'Small Format' (size S) or 'Large Format' (M, L, XL, or XXL)."
**Your Task:** A single `CASE` expression on `pizzas.size`.
**Expected Output:** 91 rows; 30 Small Format (S), 61 Large Format (M/L/XL/XXL).

### 🟡 Analyst
**Business Question:** "How many orders come in on weekdays vs. weekends?"
**Your Task:** Use `EXTRACT(ISODOW FROM order_date)` inside a `CASE` (ISO
day-of-week: 6=Saturday, 7=Sunday) to bucket each order, then `GROUP BY`
the bucket.
**Expected Output:** 2 rows. Weekday orders should heavily outnumber
weekend orders — think about why, given the restaurant is open every day
of the week.

### 🔴 Business Challenge
**Business Question:** "Management wants every pizza FLAVOR bucketed into
Low / Medium / High revenue tiers for 2015 — but they haven't told you
where the cutoffs should go. You decide, based on the actual data."
**Your Task:** First run `MIN`, `AVG`, and `MAX` on per-flavor total
revenue to see the real distribution (min ≈ $11,589, avg ≈ $25,558, max ≈
$43,434). Then choose two cutoff values that split the 32 flavors into
three genuinely useful groups (not one giant bucket and two tiny ones),
and write the `CASE` + `GROUP BY` query. Document your chosen cutoffs and
why in a SQL comment.
**Expected Output:** 3 rows (Low/Medium/High) with counts that sum to 32.
There's no single "correct" cutoff — but a Low bucket of 30 flavors and a
High bucket of 1 is a bad answer; aim for roughly balanced groups.

---

## Level 8 — JOINs

### 🟢 Warm-up
**Business Question:** "Show me the flavor, category, and size for the 10
largest single line-item quantities we've ever sold."
**Your Task:** `INNER JOIN` `order_details` → `pizzas` → `pizza_types`,
`ORDER BY quantity DESC`, `LIMIT 10`.
**Expected Output:** 10 rows, quantity 4 (the maximum in this dataset) at
the top.

### 🟡 Analyst
**Business Question:** "Print every pizza sold on 2015-06-15, with its
flavor name, category, and what time the order came in."
**Your Task:** Three-table `JOIN` (`order_details` → `orders`,
`order_details` → `pizzas` → `pizza_types`), filtered with `WHERE`.
**Expected Output:** 150 rows, sorted by `order_time`.

### 🔴 Business Challenge
**Business Question:** "The chef is deciding which flavors are good
candidates to ALSO offer in a new size. Which flavors currently come in
only ONE size — meaning we've never given the customer a size choice for
that flavor at all?"
**Your Task:** This needs `pizzas` JOINed to `pizza_types`, `GROUP BY`
flavor, `HAVING COUNT(DISTINCT size) = 1` — notice this combines JOIN,
GROUP BY, and HAVING, concepts from three different levels, which is
exactly what real business questions do.
**Expected Output:** 3 rows: The Big Meat Pizza (S only), The Brie Carre
Pizza (S only), The Five Cheese Pizza (L only).
