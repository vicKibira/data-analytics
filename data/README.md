# Data Dictionary — Plato's Pizza Sales (2015)

## Source

`data/raw/pizza_sales.csv` — one row per **pizza line-item** within a customer order, for a single
pizza restaurant, covering the full 2015 calendar year (Jan 1 – Dec 31, 358 distinct order days).

**48,620 rows × 12 columns. No separate data dictionary file was supplied with this project** —
the dictionary below was produced by directly inspecting the CSV (dtypes, value ranges, null
counts, duplicate checks, cross-column consistency). Where the source data is ambiguous, the
assumption is called out explicitly. No column, value, or relationship below was invented — every
statement is backed by a check anyone can re-run against `data/raw/pizza_sales.csv`.

## Columns (raw file)

| Column | Raw type | Range / cardinality | Description |
|---|---|---|---|
| `pizza_id` | float (whole numbers) | 1–48,620, 48,620 unique, sequential | Surrogate id for the line-item row itself. Not a business key. |
| `order_id` | float (whole numbers) | 1–21,350, 21,350 unique | Groups one or more line-items into a single customer order. |
| `pizza_name_id` | string | 91 unique, e.g. `hawaiian_m` | Composite code: `{pizza flavor slug}_{size code}`. Size code is the last `_`-separated token (`s`, `m`, `l`, `xl`, `xxl`) and matches `pizza_size` 1:1 for every row. |
| `quantity` | float (whole numbers) | 1–4 | Units of that `pizza_name_id` ordered in this line-item. |
| `order_date` | string | 358 unique days, spans 2015-01-01 → 2015-12-31 | **Data quality issue:** two different date formats are mixed in the same column — see below. |
| `order_time` | string, `HH:MM:SS` (24h) | 09:00:xx – 23:59:xx | Consistently formatted across all 48,620 rows. |
| `unit_price` | float | $9.75 – $35.95 | Price per unit of the specific `pizza_name_id` (flavor + size). Verified constant for every `pizza_name_id` (0 pizza_name_id values have more than one distinct unit_price). |
| `total_price` | float | — | Verified equal to `quantity × unit_price` for all 48,620 rows (0 mismatches). Fully derived — carried in the raw file but not treated as an independent fact. |
| `pizza_size` | string | `S`, `M`, `L`, `XL`, `XXL` | S=14,137, M=15,385, L=18,526, XL=544, XXL=28 rows. |
| `pizza_category` | string | `Classic`, `Veggie`, `Supreme`, `Chicken` | 4 categories, consistent per pizza flavor. |
| `pizza_ingredients` | string | comma-separated, 2–8 ingredients per pizza | Consistent for every row sharing the same base flavor (size does not change ingredients). |
| `pizza_name` | string | 32 unique | Human-readable pizza name. Consistent per base flavor. |

## Data quality findings (verified against the raw file)

1. **Mixed date formats in `order_date`.** 19,587 rows use `M/D/YYYY` (e.g. `1/1/2015`) and
   29,033 rows use `D-M-YYYY` (e.g. `13-01-2015`). The two formats are **interleaved by
   `order_id`**, not a clean batch cutover (e.g. slash-format rows appear up to `order_id`
   20,399, dash-format rows start at `order_id` 737) — so a naive single-format parse
   (`pd.to_datetime(..., format='%m/%d/%Y')`) silently fails or silently mis-parses roughly
   60% of the file. This is the course's primary cleaning exercise (`src/clean_data.py`,
   `notebooks/02_data_cleaning.ipynb`).
2. **`total_price` is fully redundant.** It always equals `quantity * unit_price`. We keep it in
   `order_details` as a stored, validated column (useful for teaching the "trust but verify"
   habit and for simple business queries) rather than silently dropping it.
3. **No missing values** in any of the 12 columns.
4. **No duplicate rows** (`df.duplicated().sum() == 0`) and no duplicate `pizza_id`.
5. **No invalid values**: no zero/negative `quantity`, `unit_price`, or `total_price`.
6. **`pizza_id` is a simple row sequence**, not a meaningful business key — it is only used as
   the surrogate primary key for the fact table.

## Normalization decision (assumption, documented)

The provided file is a single **flat/denormalized** table — no separate tables were supplied.
Rather than load one wide table (which would make JOINs, foreign keys, and star-schema concepts
impossible to teach honestly), we normalize it into four tables that mirror how a real point-of-
sale export like this is actually modeled upstream. This is a **design decision made by
inspecting the data's functional dependencies**, not invented data:

- Every `pizza_name_id` implies exactly one `pizza_size` and one `unit_price` → size + price
  belong on a `pizzas` (flavor × size) table.
- Every base flavor (the part of `pizza_name_id` before the size suffix) implies exactly one
  `pizza_name`, `pizza_category`, and `pizza_ingredients` → those belong on a `pizza_types` table.
- Every `order_id` implies exactly one `order_date` and `order_time` → those belong on an
  `orders` table.
- The remaining `pizza_id`, `order_id`, `pizza_name_id`, `quantity`, `total_price` form the
  transactional fact table, `order_details`.

See `sql/01_schema.sql` for the resulting DDL and `data/processed/` for the four CSVs produced by
`src/clean_data.py` immediately prior to loading.

## Known limitations (things this dataset cannot answer)

- **No customer identifier** — no repeat-customer, loyalty, or lifetime-value analysis is possible.
- **No order channel** (dine-in / delivery / pickup) — cannot analyze channel mix.
- **No cost or margin data** — only revenue, never profit, can be measured. "High revenue" is not
  the same as "high margin," and the course is explicit about this distinction.
- **Single location, single year (2015)** — no store comparison, no year-over-year trend.
- **No payment/discount data** — no promotion or discount-effectiveness analysis.

These limitations are carried into `reports/insights.md` and the dashboard as explicit caveats,
not silently ignored.
