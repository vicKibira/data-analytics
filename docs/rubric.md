# Assessment Rubric — Pizza Business Analytics Capstone

Total: 100 points across 6 weighted categories. Each category lists what
"excellent" looks like — use it to calibrate partial credit, not as a
literal checklist to tick.

| Category | Weight |
|---|---|
| SQL | 20% |
| Python | 20% |
| Analysis | 20% |
| Visualization | 15% |
| Storytelling | 10% |
| Streamlit Dashboard | 15% |

## SQL — 20 points

- **Query correctness (6 pts):** queries return the right rows, joins use
  correct keys, no accidental row duplication from a bad join.
- **Aggregation & grouping (5 pts):** correct use of `GROUP BY`/`HAVING`;
  understands the WHERE-runs-before-grouping / HAVING-runs-after distinction.
- **JOINs (4 pts):** chooses INNER vs. LEFT deliberately, not by accident;
  can explain why a given join is needed.
- **CTEs (3 pts):** uses CTEs to make a multi-step query readable, not just
  to avoid a subquery.
- **Analytical reasoning (2 pts):** the 🔴 Business Challenge queries show
  evidence of reasoning about the business question before writing SQL
  (e.g. justified CASE cutoffs, not arbitrary round numbers).

**Excellent:** independently writes a new 3+ table JOIN with GROUP BY and
HAVING for a question not covered in the exercises, and can explain every
clause's purpose.

## Python — 20 points

- **pandas fluency (6 pts):** comfortable with filtering, grouping,
  `value_counts`/`describe`, merges where relevant.
- **Cleaning (5 pts):** every cleaning decision is justified by a
  preceding check (not "cleaned it because it looked cleaner"); correctly
  distinguishes cleaning data from changing data.
- **Transformations / feature engineering (4 pts):** engineered features
  are analytically justified by the actual columns available — no
  invented dimensions.
- **Reusable code (3 pts):** logic lives in `src/` functions and is
  imported, not copy-pasted across notebooks/dashboard.
- **Analytical workflow (2 pts):** investigates before cleaning, cleans
  before analyzing — doesn't skip straight to charts.

**Excellent:** could hand `src/clean_data.py` to another analyst and they
could explain every cleaning step from the comments alone.

## Analysis — 20 points

- **Quality of questions (6 pts):** questions are specific and answerable
  from the actual data (not generic "what insights can we find").
- **Correctness (6 pts):** numbers are actually right — spot-checked
  against a second method (e.g. SQL and pandas agreeing) where possible.
- **Depth (4 pts):** goes beyond the first obvious finding (e.g. not just
  "top 10 pizzas" but "are top-volume and top-revenue pizzas the same?").
- **Interpretation (4 pts):** correctly separates what the data shows from
  what it's being inferred to mean; flags assumptions.

**Excellent:** a finding like Module 10's "popular ≠ premium" — a real,
specific, evidence-backed pattern, not a restatement of a single number.

## Visualization — 15 points

- **Chart selection (5 pts):** the chosen form matches the analytical
  purpose (comparison → bar, trend → line, composition → stacked bar,
  distribution → histogram/boxplot, relationship → scatter).
- **Readability (4 pts):** titles, axis labels, units, sensible scales;
  no truncated/misleading axes.
- **Design (3 pts):** consistent colors across charts (same category =
  same color everywhere); no unnecessary chart junk (3D effects, unneeded
  gridlines, decorative pie charts with 8+ slices).
- **Communication (3 pts):** a reader who didn't build the chart can state
  its takeaway in one sentence without help.

**Excellent:** charts that look like they belong to the same
project/report — one visual system, not a different style per chart.

## Storytelling — 10 points

- **Explains findings (4 pts):** can walk a non-technical listener through
  a finding without jargon.
- **Business relevance (3 pts):** every finding connects to a decision or
  question a real stakeholder would care about.
- **Evidence-based conclusions (3 pts):** never claims causation the data
  can't support; explicitly states limitations where relevant.

**Excellent:** consistently uses Observation → Explanation → Implication →
Next question without being prompted to.

## Streamlit Dashboard — 15 points

- **Functionality (5 pts):** runs without errors; filters actually filter
  every chart and KPI, not just some of them.
- **UX (4 pts):** clear title, one-line business description, logical
  section order (Overview → Trends → Product → Patterns → Mix), no
  unnecessary filters.
- **Interactivity (2 pts):** filters respond correctly to edge cases (all
  categories deselected, a date range with no data).
- **Technical quality (2 pts):** presentation logic, data logic, and
  chart logic are separated into different files, not all crammed into
  `app.py`.
- **Presentation (2 pts):** the dashboard tells a story top to bottom, not
  just "here are all our charts."

**Excellent:** a stakeholder could open the dashboard cold, with no
explanation, and correctly answer "what's our best-performing category?"
within 10 seconds.

## Grade bands

| Score | Grade |
|---|---|
| 90-100 | Excellent — portfolio-ready |
| 75-89 | Strong — minor gaps |
| 60-74 | Passing — core skills present, execution inconsistent |
| < 60 | Needs revision — see instructor for a specific plan |
