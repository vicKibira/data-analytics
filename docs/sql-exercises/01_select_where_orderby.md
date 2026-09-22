# SQL Exercises — Levels 1-3: SELECT, WHERE, ORDER BY

Work these against the database created by `python src/load_data.py`. Read the
taught examples in `sql/03_basic_queries.sql` first if you haven't already.
Don't peek at `docs/sql-solutions/01_select_where_orderby.md` until you've
genuinely tried each one.

Legend: 🟢 Warm-up (straightforward application) · 🟡 Analyst (combine two
concepts) · 🔴 Business Challenge (think about the business question first)

---

## Level 1 — SELECT

### 🟢 Warm-up
**Business Question:** The head chef wants a simple printable price list.
**Your Task:** Select the `pizza_name_id`, `size`, and `price` for every row
in `pizza.pizzas`, ordered alphabetically by `pizza_name_id`.
**Hints:** You need `SELECT`, column names, and `ORDER BY` (covered in
Level 3, but you'll need it to make this useful — try it now).
**Expected Output:** 91 rows.

### 🟡 Analyst
**Business Question:** "How many ingredients does each pizza actually have?
Some pizzas market themselves as 'loaded' — let's check."
**Your Task:** From `pizza.pizza_types`, select `name` and a calculated
column that counts the ingredients in `ingredients` (hint: ingredients are
comma-separated — counting commas and adding 1 gives you the ingredient
count; look up Postgres's `array_length` and `string_to_array`, or a simpler
string function of your choice).
**Hints:** This is a calculated column, same idea as the price-increase
example in `sql/03_basic_queries.sql`, just with string functions instead
of arithmetic.
**Expected Output:** 32 rows; ingredient counts should range from 2 to 8.

### 🔴 Business Challenge
**Business Question:** "Management wants a 'menu at a glance' — one row per
pizza NAME with its category, not one row per size."
**Your Task:** Before writing SQL, think: why would a plain `SELECT name,
category FROM pizzas` (note: not `pizza_types`) give you more rows than
management wants? Then write a query on the correct table(s) that returns
exactly 32 rows.
**Expected Output:** 32 rows, no repeats.

---

## Level 2 — WHERE

### 🟢 Warm-up
**Business Question:** "Show me everything in the Supreme category."
**Your Task:** Return all columns from `pizza_types` where `category =
'Supreme'`.
**Expected Output:** 9 rows.

### 🟡 Analyst
**Business Question:** "How many orders came in during July 2015?"
**Your Task:** Filter `orders` to `order_date` in July 2015 and return the
count. (You'll need `BETWEEN` or two comparisons with `AND`.)
**Expected Output:** A single number.

### 🔴 Business Challenge
**Business Question:** "A supplier is discontinuing garlic. Which pizzas
need a new recipe — specifically, pizzas that use garlic but are NOT in
the 'Classic' category (Classic recipes are being redesigned anyway, so
they don't need this fix)?"
**Your Task:** Reason about which predicates you need and how they combine
(hint: two conditions, both must hold) before writing the query. Use `LIKE`
or `ILIKE` to search `ingredients`.
**Expected Output:** 17 rows, spanning Chicken, Supreme, and Veggie
categories — if your result includes any Classic pizzas, re-check your
`WHERE` clause.

---

## Level 3 — ORDER BY

### 🟢 Warm-up
**Business Question:** "What are our most expensive pizzas?"
**Your Task:** List every SKU in `pizzas`, most expensive first.
**Expected Output:** 91 rows, first row price = $35.95.

### 🟡 Analyst
**Business Question:** "What are our 10 cheapest Chicken-category pizzas?"
**Your Task:** Combine a `WHERE` filter (needs a JOIN to `pizza_types` to
filter by category), `ORDER BY`, and `LIMIT`.
**Hints:** This is the first exercise that needs a JOIN — if you haven't
reached Level 8 yet, it's fine to peek at the JOIN syntax in
`sql/05_joins.sql`; you're combining concepts, which is the point of the
🟡 tier.
**Expected Output:** 10 rows, cheapest Chicken pizza first.

### 🔴 Business Challenge
**Business Question:** "The head chef is redesigning the physical menu
board and wants pizzas grouped by category, with the most expensive option
in each category shown first — a natural 'good/better/best' layout within
each category block."
**Your Task:** Write a single query, joining `pizzas` and `pizza_types`,
that sorts by category (alphabetically) and then by price (descending)
within each category.
**Expected Output:** 91 rows; within each category block, price should
count down.
