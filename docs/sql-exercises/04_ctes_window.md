# SQL Exercises — Levels 9-10: CTEs, Window Functions

Level 10 is explicitly marked "Analyst Challenge" — it goes beyond what's
required to complete the core course, for students who want to go further.
Reference: `sql/06_ctes.sql` and `sql/07_advanced_analysis.sql`. Solutions:
`docs/sql-solutions/04_ctes_window.md`.

---

## Level 9 — CTEs

### 🟢 Warm-up
**Business Question:** "Which categories generated more than $150,000 in
2015?"
**Your Task:** Write a CTE that computes revenue by category, then a
final `SELECT` that filters it with `WHERE` (not `HAVING` — the CTE
already did the grouping, so the outer query is filtering plain rows).
**Expected Output:** All 4 categories qualify, ranging $193,690-$220,053.

### 🟡 Analyst
**Business Question:** "What was our single best day of 2015, and what did
people actually order that day?"
**Your Task:** First CTE: daily revenue, to find the top day. Second step:
a query filtered to that specific date, joined to show flavor/size/
quantity, ordered by line-item value descending.
**Expected Output:** The top day had 259 line-items; the single highest-
value line-item was $41.00 (2 Large Italian Capocollo pizzas).

### 🔴 Business Challenge
**Business Question:** "Show each category's revenue AND what percentage
of TOTAL company revenue that category represents — in one result set,
without a second query or manual math."
**Your Task:** A CTE for per-category revenue, then a window function
(`SUM(...) OVER ()`, no `PARTITION BY`) in the outer query to get the
grand total as a denominator on every row.
**Expected Output:** 4 rows; percentages should sum to almost exactly 100%.

---

## Level 10 — Window Functions (Analyst Challenge)

### 🟢 Warm-up
**Business Question:** "Rank every pizza flavor by units sold, without
losing the underlying per-flavor rows."
**Your Task:** `RANK() OVER (ORDER BY SUM(quantity) DESC)`.
**Expected Output:** 32 rows, ranked 1-32; rank 1 = The Classic Deluxe
Pizza (2,453 units).

### 🟡 Analyst
**Business Question:** "What is each category's single best-selling
flavor by revenue — its 'flagship' pizza?"
**Your Task:** `RANK() OVER (PARTITION BY category ORDER BY
SUM(revenue) DESC)` inside a CTE, then filter the outer query to rank = 1
(or, for a top-3-per-category leaderboard, rank <= 3).
**Expected Output:** 4 rows (one flagship per category) if you filter to
rank = 1.

### 🔴 Business Challenge
**Business Question:** "Find the single day where actual revenue most
exceeded what a 'normal' recent trend would have predicted — a candidate
for a promotion, event, or press mention worth investigating further."
**Your Task:** Build a 7-day rolling average of daily revenue (window
frame: `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`), then compute how far
each day's actual revenue exceeded its own rolling average, and find the
single biggest positive gap.
**Expected Output:** The top day should stand out by roughly $1,900 above
its trailing 7-day average — worth asking "what happened that day?" in
`reports/insights.md`.
