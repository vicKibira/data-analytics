# Instructor Guide

For each module: learning objectives, prerequisites, lesson flow, how to
explain the concept simply, what to live-code, what students attempt
themselves, a stretch challenge, discussion questions, the expected
output, and common mistakes to watch for. Follow the rhythm **Learn →
Practice → Investigate → Build → Explain** throughout — avoid long
theoretical lectures; get to a real pizza-business query or chart fast.

---

## Module 0 — Kickoff: Meet the Business & the Data

**Learning objectives:** understand the Plato's Pizza narrative; know what
`pizza_sales.csv` actually contains before touching any tool.
**Prerequisites:** none.
**Lesson flow (20-30 min):** read the narrative aloud → open
`data/raw/pizza_sales.csv` in a text editor/spreadsheet → read
`data/README.md` together.
**Instructor explanation:** frame the whole course as one long assignment
from a manager, not a series of exercises. Point out explicitly that no
data dictionary was provided with this project — the class will build one
by inspection, which is normal in real analyst work.
**Live coding:** none — this is a reading/discussion module.
**Student exercise:** skim the raw CSV and write down 3 questions they
think the data could answer, and 1 question they suspect it can't.
**Challenge:** spot the mixed date formats in `order_date` by eye, before
being told about them.
**Discussion:** "What would you ask management before starting this
project?" (channel, customer ID, cost data — surface the limitations
students will hit later.)
**Expected outcome:** every student can state, in one sentence, what one
row of this dataset represents (one pizza line-item in one order).
**Common mistakes:** assuming a row is "one order" (it's one line-item —
one order can have several rows, verify with `order_id`).

---

## Module 1 — Data Engineering Foundation: Docker + Postgres + Schema Design

**Learning objectives:** explain what a database is and why analysts use
one instead of working from CSVs directly; read a schema diagram; explain
primary/foreign keys.
**Prerequisites:** Module 0; basic command line comfort (students already
know Docker and SQL per course prerequisites).
**Lesson flow (45 min):** why not just use the CSV? (discussion) → `docker
compose up -d` → walk `sql/01_schema.sql` top to bottom, explaining the
normalization decision in `data/README.md` → connect with `psql`.
**Instructor explanation:** a CSV has no rules — nothing stops a bad row
from being appended. A database enforces types, keys, and relationships,
so bad data is rejected instead of silently corrupting analysis. Schemas
are just namespaces (folders for tables). The 4-table design here mirrors
how this exact data is structured upstream in a real point-of-sale system.
**Live coding:** run `docker compose up -d`, `docker compose ps`, connect
with `psql`, run `\dt pizza.*` and `\d pizza.order_details`.
**Student exercise:** draw (on paper or in a doc) the 4-table schema and
its foreign keys from memory, then check against `sql/01_schema.sql`.
**Challenge:** why does `pizzas` (not `pizza_types`) hold `price`? (Because
price varies by size, which lives on `pizzas`, not by flavor alone.)
**Discussion:** "What would break if `total_price` were removed from
`order_details`?" (Nothing computationally — it's derived — but every
query would need to compute `quantity * price` itself. Trade-off between
normalization purity and query convenience.)
**Expected outcome:** a running Postgres container and a student who can
explain each of the 4 tables' grain in one sentence.
**Common mistakes:** forgetting `docker compose up -d` needs `-d`
(detached) or the terminal appears to hang; confusing `pizza_name_id`
(SKU) with `pizza_type_id` (flavor).

---

## Module 2 — Loading & Validating Data

**Learning objectives:** understand an ETL script's responsibilities;
explain why validation happens BEFORE loading; understand environment
variables for credentials.
**Prerequisites:** Module 1.
**Lesson flow (45 min):** read `.env.example` and explain never hardcoding
credentials → walk `src/load_data.py` function by function (read → validate
→ transform → load → verify) → run it live.
**Instructor explanation:** a script finishing without an error only means
nothing crashed — it does NOT mean the data is correct. Point at
`validate_raw()` and ask "what would happen if we skipped this and loaded
garbage?" Emphasize the mixed-date-format fix happens here, upstream,
once — not repeated by every downstream consumer.
**Live coding:** `cp .env.example .env`, `python src/load_data.py`, watch
the log output row-count-verify at the end.
**Student exercise:** intentionally break something (e.g. delete a
required column from a copy of the CSV) and run the script — confirm it
fails loudly with a clear message rather than silently loading bad data.
**Challenge:** modify `validate_raw()` to also check that no `order_date`
is in the future (relative to some reference date) — should it be needed
here? Why or why not?
**Discussion:** "Why re-parse dates here in Python instead of just fixing
them in the CSV by hand?" (Reproducibility — the fix must run the same way
every time, for any raw file, not as a one-off manual edit.)
**Expected outcome:** all 4 tables loaded with row counts verified against
source (32 / 91 / 21,350 / 48,620).
**Common mistakes:** running the script without the Postgres container up;
editing `.env.example` instead of a copied `.env`.

---

## Module 3 — SQL Level 1-3: SELECT, WHERE, ORDER BY

**Learning objectives:** retrieve, filter, and sort rows; distinguish
`WHERE`'s row-filtering from `ORDER BY`'s result-sorting.
**Prerequisites:** Module 2 (a loaded database).
**Lesson flow (60 min):** live-run `sql/03_basic_queries.sql` top to
bottom, pausing to predict output before running each query → Level 1-3
exercises (`docs/sql-exercises/01_select_where_orderby.md`) in pairs.
**Instructor explanation:** SQL execution doesn't run top-to-bottom like
Python — `WHERE` filters happen conceptually before `SELECT`'s column list
is applied, which is why you can filter on a column you don't display.
**Live coding:** build the Level 3 "menu board" business challenge query
live, thinking aloud about `ORDER BY category, price DESC`.
**Student exercise:** the full 🟢🟡🔴 set in `docs/sql-exercises/01_*`.
**Challenge:** the 🔴 garlic-ingredient question — reason about the `AND`
before writing any SQL.
**Discussion:** "Why did `SELECT DISTINCT name, category FROM pizza_types`
return fewer rows than the same columns queried from `pizzas`?"
**Expected outcome:** every student can independently write a 3-condition
`WHERE` clause and a 2-column `ORDER BY`.
**Common mistakes:** `WHERE column = NULL` (always empty — must be `IS
NULL`); forgetting `LIMIT` on exploratory `SELECT *` queries against large
tables.

---

## Module 4 — SQL Level 4-6: Aggregations, GROUP BY, HAVING

**Learning objectives:** collapse rows into summary statistics; group by
one or more columns; filter GROUPS (not rows) with `HAVING`.
**Prerequisites:** Module 3.
**Lesson flow (75 min):** `COUNT`/`SUM`/`AVG` cold open with no `GROUP BY`
→ introduce `GROUP BY` as "now do that math separately per bucket" →
`HAVING` as "the `WHERE` clause that runs after grouping."
**Instructor explanation:** the #1 conceptual trap is `WHERE
SUM(total_price) > 1000` — walk through WHY that fails (SUM doesn't exist
yet when WHERE runs) before showing `HAVING` as the fix.
**Live coding:** build revenue-by-category live, then add `HAVING
SUM(...) > 30000` on top of it, narrating the WHERE-vs-HAVING distinction.
**Student exercise:** `docs/sql-exercises/02_aggregation_groupby_having.md`.
**Challenge:** the 🔴 HAVING challenge (COUNT DISTINCT + AVG combined) —
this is genuinely the hardest single query so far; expect it to take time.
**Discussion:** walk through the real finding that Pepperoni/Hawaiian/Big
Meat are top SELLERS but fail the $15 avg-value bar — "popular ≠ premium."
Ask: "Is that good or bad for the business?"
**Expected outcome:** students can explain, unprompted, why `HAVING`
exists when `WHERE` already exists.
**Common mistakes:** using `WHERE` where `HAVING` is needed (and vice
versa — an eager `HAVING category = 'Classic'` works but is wasteful,
since that's a row-level filter that `WHERE` handles more cheaply).

---

## Module 5 — SQL Level 7-8: CASE, JOINs

**Learning objectives:** bucket continuous/many-valued data into business
categories; combine data from multiple tables; choose INNER vs. LEFT JOIN.
**Prerequisites:** Module 4.
**Lesson flow (75 min):** CASE for price tiers (live-code the cutoff
discussion, don't just hand students numbers) → why JOINs exist (show a
query that NEEDS `pizza_types` data but only has `order_details`) → INNER
vs LEFT with the "flavor that never sold" thought experiment.
**Instructor explanation:** every JOIN answers "where does this data
actually live, and how do I connect back to it?" Draw the FK relationships
on a board before writing SQL. For LEFT JOIN, the litmus test is "could
the right side legitimately have zero matches?" — if yes, LEFT JOIN; if
you're certain otherwise, INNER JOIN is fine (they'll return the same rows
here, since every flavor did sell — the CHOICE still matters as a habit).
**Live coding:** the 3-table JOIN answering "what sold on 2015-06-15."
**Student exercise:** `docs/sql-exercises/03_case_joins.md`.
**Challenge:** the 🔴 CASE challenge — students must look at MIN/AVG/MAX
revenue themselves before choosing tier cutoffs; do not give them the
cutoffs.
**Discussion:** "Why does `pizzas` need `pizza_type_id` as a foreign key
instead of just repeating `name`/`category`/`ingredients` on every row?"
(Ties back to Module 1's normalization discussion.)
**Expected outcome:** a working 3-table JOIN with a WHERE filter, written
without looking at the reference file.
**Common mistakes:** forgetting a JOIN condition (producing a cartesian
product — huge row counts are the tell); joining on the wrong column pair
(e.g. `pizza_name_id` to `pizza_type_id` — different grains).

---

## Module 6 — SQL Level 9-10: CTEs, Window Functions (Analyst Challenge)

**Learning objectives:** name and chain multi-step queries with `WITH`;
rank/partition/run totals without collapsing rows.
**Prerequisites:** Module 5.
**Lesson flow (75-90 min, can span 2 sessions):** rewrite a nested
subquery as a CTE live, showing the readability gain → RANK/ROW_NUMBER →
PARTITION BY → running totals → mark Level 10 explicitly as optional/
stretch content.
**Instructor explanation:** a CTE is just "give this subquery a name so
the final SELECT reads like English." Window functions are the hardest
new mental model in the course — spend real time on "GROUP BY collapses
rows; a window function doesn't" with a live side-by-side comparison.
**Live coding:** the Business Request 5 query (volume rank vs. revenue
rank, `sql/06_ctes.sql`) — this is the module's centerpiece; it's also the
first time multiple SQL concepts genuinely compose into one answer.
**Student exercise:** `docs/sql-exercises/04_ctes_window.md`. Levels
9 🟢🟡 are required; Level 10 (all tiers) is explicitly optional/stretch.
**Challenge:** the Level 10 🔴 rolling-average anomaly query — this
surfaces the real Thanksgiving-week spike; treat finding it as a genuine
"aha" moment, not just a syntax drill.
**Discussion:** "We found the exact same Thanksgiving spike in SQL here
and again in Python in Module 10. Why is that agreement reassuring?"
(Two independent methods reaching the same answer is stronger evidence
than either alone.)
**Expected outcome:** every student can write a 2-CTE query; window
functions are "seen and understood," not necessarily fluent yet — that's
fine, they'll see the same functions again in a business context in
Module 10.
**Common mistakes:** forgetting `PARTITION BY` and being confused why
ranking doesn't reset per group; treating a window function's `ORDER BY`
as sorting the whole result set (it only defines window order, not output
order — a separate outer `ORDER BY` is often still needed).

---

## Module 7 — Python Extraction: The SQL → pandas Bridge

**Learning objectives:** explain the division of labor between SQL and
pandas; use `extract_data.py`'s functions; interrogate an unfamiliar
DataFrame.
**Prerequisites:** Module 6 (or at least Module 5 — Level 10 isn't a hard
requirement to proceed).
**Lesson flow (60 min):** the explicit transition line — "we know how to
ask the database questions; now let's bring data into Python for deeper
investigation" → walk `src/extract_data.py` → run `notebooks/01_data_exploration.ipynb` live.
**Instructor explanation:** SQL is efficient at retrieving/joining/
aggregating AT the database; pandas is efficient at flexible, iterative
exploration once data is small enough for memory. Neither replaces the
other — the real skill is knowing which tool a given step belongs to.
**Live coding:** `df.head()`, `df.info()`, `df.describe()`,
`value_counts()` on a column students haven't seen queried yet.
**Student exercise:** Notebook 01's "Your Turn" section.
**Challenge:** compare `df['pizza_ingredients'].nunique()` against
`df['pizza_name'].nunique()` — explain in one sentence why they're equal.
**Discussion:** "`extract_data.py`'s `load_sales_data()` runs the exact
JOIN from `sql/05_joins.sql`. Why keep that logic in ONE place instead of
writing the JOIN fresh in every notebook?"
**Expected outcome:** students can call `load_sales_data()` and describe
the resulting DataFrame's shape and columns unprompted.
**Common mistakes:** trying to query the raw CSV and the database
interchangeably without noticing they're not currently in the same state
(this is intentional — flag it explicitly, don't let it be a silent
confusion; see Module 8).

---

## Module 8 — Data Quality & Cleaning

**Learning objectives:** run a systematic data-quality checklist; state
the difference between cleaning data and changing data; justify every
cleaning decision explicitly.
**Prerequisites:** Module 7.
**Lesson flow (75 min):** explain WHY `notebooks/02_data_cleaning.ipynb`
re-reads the RAW csv instead of the (already-clean) database → live
discover the mixed date-format bug via `check_date_formats()` → clean →
feature-engineer → save.
**Instructor explanation:** "never trust a dataset just because it loaded
successfully" is the module's thesis. Walk the checklist (missing values,
duplicates, inconsistent categories, invalid values, wrong dtypes,
impossible dates) as a habit to run on ANY new dataset, not just this one.
Be explicit: every step in `clean_pizza_sales()` has a comment justifying
it — a cleaning step with no justification doesn't belong in real code.
**Live coding:** trigger the naive `pd.to_datetime(..., format='%m/%d/%Y')`
failure live before showing the fix — the error message IS the lesson.
**Student exercise:** Notebook 02's "Your Turn," especially the price-band
cutoff re-derivation challenge.
**Challenge:** recompute `price_band` cutoffs from quantiles instead of
the hardcoded $12.50/$17.50 and discuss whether the business story changes.
**Discussion:** "`src/load_data.py` already fixed these dates once. Why
do it again here?" (Real analysts often receive raw files directly, not
through a perfect pipeline — this IS that scenario, faithfully preserved.)
**Expected outcome:** `data/processed/pizza_sales_clean.csv` regenerated
by the student, with all 6 engineered columns present and correct.
**Common mistakes:** "cleaning" by dropping rows that look unusual without
verifying they're actually wrong (e.g. the 28-pizza order is a real,
verified order — not an error to be dropped).

---

## Module 9 — Feature Engineering & EDA

**Learning objectives:** apply the Question → Metric → Data →
Transformation → Analysis → Visualization → Insight → Business implication
framework; choose chart form by analytical purpose, not habit.
**Prerequisites:** Module 8.
**Lesson flow (90 min, can span 2 sessions):** state the framework on a
board FIRST → walk `notebooks/03_eda.ipynb` theme by theme, pausing after
each chart to fill in all 8 framework steps out loud before revealing the
notebook's own insight text.
**Instructor explanation:** "let's make some charts" is banned language in
this module. Every chart must be traceable back to a named business
question. Drill the chart-form rule: comparison→bar, trend→line,
composition→stacked bar, distribution→histogram/boxplot,
relationship→scatter — never a pie/donut with more than a couple of slices.
**Live coding:** the volume-vs-revenue scatter plot — predict the shape
before running it.
**Student exercise:** Notebook 03's "Your Turn," writing out all 8
framework steps in markdown for their chosen question.
**Challenge:** the time-of-day × category mix cross-tab question.
**Discussion:** "Revenue is nearly flat month-to-month. Does that mean
timing doesn't matter for this business?" (No — it means the real
timing signal is intraday, not seasonal; a student who stops at the
monthly chart would miss it.)
**Expected outcome:** a student-authored chart with a written Insight and
Business Implication that isn't just restating the chart's numbers.
**Common mistakes:** treating a chart as the deliverable instead of the
insight; confusing correlation with causation (call this out explicitly
every time it's tempting — e.g. the anomaly-day finding is real, but its
CAUSE (Thanksgiving) is an inference from a US calendar, not something the
data itself proves).

---

## Module 10 — Business Analysis & Storytelling

**Learning objectives:** write an evidence-based finding using
Observation → Explanation → Implication → Next question; distinguish a
finding from a mere fact.
**Prerequisites:** Module 9.
**Lesson flow (75 min):** contrast "Revenue was $817,860" against a full
4-part finding from `notebooks/04_business_analysis.ipynb` → walk 2-3 of
the notebook's 5 findings live → students write their own for the
remaining "Your Turn" prompts.
**Instructor explanation:** a fact is not an insight. Push students past
the Observation step every time — "so what?" is the question a stakeholder
actually asks. Equally important: model INTELLECTUAL HONESTY about limits
— this dataset cannot prove causation or profitability; say so out loud
whenever a finding brushes against that boundary.
**Live coding:** the product-concentration finding (top-5-flavors-of-32
= 24.5% of revenue) end to end, including the chart.
**Student exercise:** pick one of Notebook 04's "Your Turn" prompts and
write all 4 storytelling steps.
**Challenge:** the Independence Day (2015-07-04) anomaly check — does the
same holiday-spike pattern repeat?
**Discussion:** "We can't tell whether Pepperoni is profitable. What data
would we need to answer that, and where would it come from?"
**Expected outcome:** `reports/insights.md`-quality writing from each
student for at least one finding — evidence-based, limitation-aware, no
overclaiming.
**Common mistakes:** stopping at Explanation without stating a Business
Implication; asserting causation from a single year of data.

---

## Module 11 — Streamlit Dashboard

**Learning objectives:** separate data/presentation logic; wire filters to
recompute KPIs and charts; reuse existing analysis code instead of
rewriting it for the app.
**Prerequisites:** Module 10.
**Lesson flow (90-120 min):** walk `dashboard/` architecture
(`data.py` / `components/filters.py` / `components/kpis.py` /
`components/charts.py` / `app.py`) → run it live with `streamlit run
dashboard/app.py` → change a filter and watch every chart update.
**Instructor explanation:** the dashboard is NOT new analysis — it's the
SAME functions and the SAME color system (`src/utils.py`:
`CATEGORY_COLORS`, `apply_chart_style`) as the notebooks, wired to
widgets. Emphasize this reuse explicitly: "you already wrote the hard
part; this module is about presentation and interactivity."
**Live coding:** add one new KPI or chart to the dashboard live (e.g. "% of
revenue from weekend orders").
**Student exercise:** implement one new filter or chart not already in the
starter dashboard; a good default is a single-flavor drill-down view.
**Challenge:** make the dashboard degrade gracefully with no data source —
inspect `dashboard/data.py`'s fallback-to-CSV logic and explain why it
exists.
**Discussion:** "Why does the KPI row use `st.metric` instead of a
matplotlib chart?" (Right form for a single headline number — see the
Level 4 visualization-form discussion in Module 9.)
**Expected outcome:** a working local dashboard the student can navigate
end to end, with at least one original addition.
**Common mistakes:** duplicating chart logic instead of importing from
`components/charts.py`; forgetting filters must return NEW filtered
DataFrames, not mutate the cached original (`st.cache_data`-wrapped data
must never be mutated in place).

---

## Module 12 — Capstone Project & Presentation

See `docs/capstone.md` for the full specification and `docs/rubric.md`
for grading. This module is primarily independent work with instructor
office hours, not new lecture content — students are assembling and
polishing what Modules 0-11 already built, not starting over.
**Lesson flow:** kickoff (review capstone deliverables) → 2-4 work
sessions with instructor spot-checks → presentation day (`docs/capstone.md`'s
10-slide structure, ~5-8 minutes per student).
**Instructor explanation:** the capstone is deliberately NOT a new dataset
or new tool — it's proof the student can assemble everything already
built into a coherent, presentable, portfolio-quality story.
**Discussion (presentation day):** after each presentation, ask "what
would you investigate next with one more dataset?" — reinforces that good
analysis generates new questions, it doesn't just close old ones.
**Common mistakes:** presenting code instead of the story (the rubric
explicitly rewards storytelling — remind students the audience is
"management," not other engineers); skipping the Limitations slide.
