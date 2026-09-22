# SQL Solutions — Levels 1-3: SELECT, WHERE, ORDER BY

Every query below was executed against the real loaded database; row counts
and values are actual results, not estimates. If your result differs,
compare your `WHERE`/`JOIN` logic against the query here before assuming
the answer key is wrong.

---

## Level 1 — SELECT

### 🟢 Warm-up
```sql
SELECT pizza_name_id, size, price
FROM pizza.pizzas
ORDER BY pizza_name_id;
```
**Result:** 91 rows.
**Explanation:** `SELECT` chose only the three columns the chef actually
needs; `ORDER BY pizza_name_id` makes the printed list predictable.

### 🟡 Analyst
```sql
SELECT
    name,
    array_length(string_to_array(ingredients, ','), 1) AS n_ingredients
FROM pizza.pizza_types
ORDER BY n_ingredients DESC;
```
**Result:** 32 rows; ingredient counts range 2-8, average ~5.5.
**Explanation:** `string_to_array` splits the comma-separated text into an
array; `array_length(..., 1)` counts its elements. This is the SQL-side
version of `len(ingredients.split(','))` you'll write in pandas later —
same idea, different toolset.

### 🔴 Business Challenge
```sql
SELECT DISTINCT name, category
FROM pizza.pizza_types
ORDER BY name;
```
**Result:** 32 rows, no repeats.
**Explanation:** `pizzas` has 91 rows because it has one row per
(flavor, size) combination — querying it directly for "menu at a glance"
would repeat every flavor 2-5 times (once per size it's offered in).
`pizza_types` already has exactly one row per flavor, so no `DISTINCT` is
even needed there — but if you queried `pizzas` and reached for `DISTINCT`
on `pizza_type_id` joined back to `pizza_types`, that also works and shows
you understand why the duplication happened.

---

## Level 2 — WHERE

### 🟢 Warm-up
```sql
SELECT * FROM pizza.pizza_types WHERE category = 'Supreme';
```
**Result:** 9 rows.

### 🟡 Analyst
```sql
SELECT COUNT(*) FROM pizza.orders
WHERE order_date BETWEEN '2015-07-01' AND '2015-07-31';
```
**Result:** 1,860 orders.
**Explanation:** `BETWEEN` is inclusive on both ends, so this correctly
includes July 31st. An equivalent (and equally correct) version:
`WHERE order_date >= '2015-07-01' AND order_date < '2015-08-01'`.

### 🔴 Business Challenge
```sql
SELECT name, category, ingredients
FROM pizza.pizza_types
WHERE ingredients ILIKE '%garlic%'
  AND category <> 'Classic'
ORDER BY category, name;
```
**Result:** 17 rows (2 Chicken, 8 Supreme, 7 Veggie).
**Explanation:** Both conditions must hold for every returned row — that's
what `AND` means. Using `ILIKE` (case-insensitive) instead of `LIKE`
protects you from missing a match because of inconsistent capitalization
in the ingredients text.

---

## Level 3 — ORDER BY

### 🟢 Warm-up
```sql
SELECT pizza_name_id, size, price
FROM pizza.pizzas
ORDER BY price DESC;
```
**Result:** 91 rows; first row is `the_greek_xxl` at $35.95.

### 🟡 Analyst
```sql
SELECT p.pizza_name_id, p.size, p.price
FROM pizza.pizzas p
JOIN pizza.pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE pt.category = 'Chicken'
ORDER BY p.price ASC
LIMIT 10;
```
**Result:** 10 rows, cheapest first.
**Explanation:** The `WHERE` clause needs `pizza_types.category`, which
doesn't exist on `pizzas` directly — hence the JOIN, even though this is
"only" an ORDER BY exercise. Real business questions rarely respect our
neat level boundaries.

### 🔴 Business Challenge
```sql
SELECT pt.category, p.pizza_name_id, p.price
FROM pizza.pizzas p
JOIN pizza.pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
ORDER BY pt.category ASC, p.price DESC;
```
**Result:** 91 rows, sorted first by category (Chicken, Classic, Supreme,
Veggie), then descending by price within each category block.
**Explanation:** Multi-column `ORDER BY` sorts by the first column, and
only uses the second column to break ties within groups that share the
first column's value — exactly the "sort within category" behavior the
chef asked for.
