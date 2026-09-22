# 🍕 Pizza Business Analytics Capstone

## Scenario

You are a junior data analyst at Plato's Pizza. Management wants to
understand historical sales performance and start making decisions with
data instead of gut feel. You've been given the company's 2015 sales
export (`data/raw/pizza_sales.csv`). Nothing else — no data dictionary, no
second dataset, no customer records. That's the job: take what you were
actually given and turn it into something decision-ready.

## Your job

1. Load the data into a database (`src/load_data.py`).
2. Validate it independently — don't trust it just because it loaded
   (`sql/02_data_quality.sql`).
3. Explore the database with SQL (`sql/03`-`08`).
4. Answer real business questions with SQL.
5. Extract analytical data into Python (`src/extract_data.py`).
6. Clean the data and justify every cleaning decision (`src/clean_data.py`).
7. Perform exploratory data analysis using the Question → Metric → Data →
   Transformation → Analysis → Visualization → Insight → Business
   implication framework.
8. Identify meaningful, evidence-based trends.
9. Create purposeful visualizations (not a slideshow of every chart you
   made along the way).
10. Develop a business narrative using Observation → Explanation →
    Implication → Next question.
11. Build an interactive Streamlit dashboard.
12. Present your findings to a non-technical audience.

This is not a new assignment — it's the assembly and polish of everything
Modules 0-11 already built. If you've done the modules honestly, the
capstone is mostly curation, not new work.

## Deliverables

| # | Deliverable | Where it lives |
|---|---|---|
| 1 | Dockerized database containing the dataset | `docker-compose.yml`, `sql/01_schema.sql` |
| 2 | Well-organized analytical SQL queries | `sql/02_data_quality.sql` → `sql/08_business_questions.sql` |
| 3 | Clean, reusable Python scripts | `src/load_data.py`, `src/extract_data.py`, `src/clean_data.py`, `src/utils.py` |
| 4 | EDA & analytical investigation notebook(s) | `notebooks/01`-`04` |
| 5 | Purposeful analytical charts | embedded in notebooks + `dashboard/` |
| 6 | Interactive Streamlit dashboard | `dashboard/app.py` |
| 7 | Project README | `README.md` |
| 8 | Executive summary | `reports/insights.md` |

Your own capstone submission should be this repository, in your own fork
or a copy, with your own additions/customizations layered on top — not
merely a clone with nothing added. At minimum, add:
- One new business question in `sql/08_business_questions.sql`, with the
  query, its result, and a written explanation.
- One new finding in `notebooks/04_business_analysis.ipynb`, following the
  Observation/Explanation/Implication/Next question structure.
- One new filter or chart in the dashboard (see Module 11's challenge).

## README requirements

Your `README.md` must explain, for a reader who has never seen this
project:
- **Project objective** — the business narrative in 2-3 sentences.
- **Dataset** — what it is, its size, and a link to `data/README.md`.
- **Architecture** — how the pieces connect (Docker → Postgres → SQL →
  Python → dashboard).
- **Technologies** — the stack and why each piece is there.
- **Setup instructions** — a new person must be able to clone and run this
  successfully by following your README alone.
- **Analysis & key findings** — summarize, don't paste the entire report.
- **Limitations** — copy forward from `data/README.md`/`reports/insights.md`,
  in your own words.
- **How to run the dashboard.**

## Presentation structure (10 slides, ~5-8 minutes)

Focus on the STORY. Assume your audience is Plato's Pizza's management —
not engineers. No live code walkthroughs unless demoing the dashboard.

1. **Business problem** — what were you asked to figure out?
2. **Dataset & methodology** — what you had, what you built (briefly).
3. **Data quality** — what you found wrong, and how you fixed it (the
   mixed date formats are a strong, concrete example).
4. **Key performance metrics** — revenue, orders, pizzas sold, AOV.
5. **Product insights** — what sells, what earns, where they differ.
6. **Time/order insights** — when customers order, and what that implies
   for staffing.
7. **Important visual findings** — 1-2 charts that carry real weight (e.g.
   the volume-vs-revenue scatter, the Thanksgiving-week anomaly).
8. **Business implications** — what should management actually DO with
   this?
9. **Dashboard demonstration** — live or screen-recorded.
10. **Recommendations for further investigation** — and be explicit about
    what this dataset CANNOT tell you (cost data, customer identity,
    channel, a second year for comparison).

## Grading

See `docs/rubric.md` for the full weighted rubric (SQL 20% / Python 20% /
Analysis 20% / Visualization 15% / Storytelling 10% / Dashboard 15%).
