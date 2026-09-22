# Plato's Pizza — 2015 Sales Analysis
**Prepared by:** Analytics Team · **Data:** `data/raw/pizza_sales.csv` (Jan 1 – Dec 31, 2015)

## Executive Summary

In 2015, Plato's Pizza generated **$817,860.05** in revenue across **21,350
orders** (49,574 pizzas sold, average order value **$38.31**). Revenue is
broadly spread across a 32-flavor menu rather than concentrated in a
handful of hero products, demand peaks predictably at lunch and dinner,
and revenue is essentially flat month over month across the year. The
clearest actionable finding is a two-day Thanksgiving-week spike, the
single largest deviation from trend in the dataset.

## Key Metrics

| Metric | Value |
|---|---|
| Total revenue | $817,860.05 |
| Total orders | 21,350 |
| Total pizzas sold | 49,574 |
| Average order value | $38.31 |
| Average pizzas per order | 2.32 |
| Distinct pizza flavors | 32 |
| Distinct SKUs (flavor × size) | 91 |

## Product Insights

- **Revenue is not concentrated.** The top 5 of 32 flavors generate only
  **24.5%** of total revenue — there is no small set of "hero" products the
  business is dependent on. This is a resilience strength: no single
  flavor falling out of favor would meaningfully damage revenue.
- **Category revenue is close to even**: Classic $220,053 (26.9%), Supreme
  $208,197 (25.5%), Chicken $195,920 (24.0%), Veggie $193,690 (23.7%) —
  and this mix is stable month to month across 2015.
- **Size drives revenue far more than flavor choice**: Large pizzas alone
  generate $375,319 (45.9% of all revenue) vs. just $1,007 (0.1%) from
  XXL, which — along with XL — is only offered on one flavor (The Greek).
- **Popular ≠ high-value.** The flavors selling in the highest volume
  (The Pepperoni Pizza, The Hawaiian Pizza, The Big Meat Pizza) are also
  among the cheapest, averaging $12.70–$14.14 per line-item versus a
  $16.82 overall average. These flavors function as volume/traffic
  drivers rather than revenue drivers. **We cannot say whether they are
  more or less profitable** — this dataset has no cost data (see
  Limitations).
- Only **3 of 32 flavors** (The Big Meat Pizza, The Brie Carre Pizza, The
  Five Cheese Pizza) are offered in just one size — candidates for the
  chef to evaluate for a size expansion.

## Time Insights

- Demand has a clear **double peak**: lunch (12:00–13:00) and dinner
  (18:00–19:00), with the single busiest hour, noon, matching by *both*
  order count and revenue — staffing built around order count alone would
  not miss the true revenue peak.
- **Weekday orders (15,514) far outnumber weekend orders (5,836)** in raw
  count, but average order value is nearly flat across every day of the
  week ($37.58–$38.90) — Friday and Saturday bring more orders, not
  bigger ones.
- Revenue is essentially flat across all 12 months (a ~$61K–$72K band, no
  strong seasonality at the monthly level).
- **The single clearest anomaly in the dataset**: 2015-11-26 (Thanksgiving
  Day) and 2015-11-27 (the day after) both spike well above their
  trailing 7-day average — Thanksgiving Day revenue was **~$1,934 above
  trend**, the largest gap of the year (identified independently in both
  `sql/07_advanced_analysis.sql` and `notebooks/04_business_analysis.ipynb`,
  giving two independent confirmations of the same finding).
- The restaurant recorded **zero orders on 2015-12-25** (Christmas Day) —
  most plausibly a closure day, not a data error (every other day of the
  year has orders).

## Order Behavior Insights

- A typical order contains **2.32 pizzas**; the largest single order in
  the dataset contained 28 pizzas (verified as a legitimate multi-line
  order, not a data error — see `data/README.md`).
- Order VALUE is far more stable across day-of-week and category than
  order COUNT is — the business's day-to-day and category-to-category
  variation is driven by how many orders come in, not by how big each one is.

## Business Opportunities (evidence-based)

1. **Investigate holiday-week staffing and prep**, given the confirmed
   Thanksgiving-week revenue spike — if this pattern repeats in future
   years' data, it justifies proactive planning rather than reactive.
2. **Evaluate expanding sizes for single-size flavors** (Big Meat, Brie
   Carre, Five Cheese) — these may be leaving size-upsell revenue on the
   table, though customer demand for a size change is not directly
   testable from this dataset.
3. **Clarify the actual profitability of high-volume/low-price flavors**
   (Pepperoni, Hawaiian, Big Meat) with real cost data — they may be
   valuable traffic drivers or a margin drag, and this dataset cannot
   distinguish between the two.
4. **The XL/XXL size tier is essentially untested** outside one flavor
   (The Greek) — too little data exists to say whether demand exists for
   it elsewhere, only that it hasn't been offered.

## Limitations

This analysis is bounded by what `data/raw/pizza_sales.csv` actually
contains (see `data/README.md` for the full verified data dictionary):

- **No customer identifier** — no repeat-customer, loyalty, or retention
  analysis is possible.
- **No order channel** (dine-in/delivery/pickup) — channel mix is unknown.
- **No cost or margin data** — every "high revenue" or "high volume"
  finding above is a revenue statement only; we cannot speak to
  profitability.
- **Single location, single year (2015)** — no store comparison and no
  year-over-year trend; the Thanksgiving spike is a single observation,
  not a confirmed repeating pattern.
- **No discount/promotion data** — we cannot separate organic demand from
  promotional effects on any given day.
- **Original file had a data-quality defect** (mixed `M/D/YYYY` and
  `D-M-YYYY` date formats in 60%+ of rows) which was identified and
  corrected during loading (`src/load_data.py`) — every date-based finding
  in this report depends on that fix being correct, and it was
  independently re-verified in `sql/02_data_quality.sql`.

## Questions this dataset cannot answer

- Are our best customers driving repeat revenue, or is growth from new customers?
- Which flavors are actually most *profitable* (vs. highest revenue)?
- Does channel (delivery vs. dine-in) affect order size or timing?
- Would the Thanksgiving spike repeat in a second year of data?
