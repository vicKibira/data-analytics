# Course Roadmap — Pizza Business Analytics

## Philosophy

You are the newest analyst on Plato's Pizza's analytics team. Every module
below is a real assignment from the business, in order, building on the
last. You will not learn a SQL clause or a pandas method because it's next
in a syllabus — you'll learn it because the business just asked a question
you can't answer without it. By the end, you will have taken one messy CSV
all the way to a live, interactive dashboard you could show a hiring
manager.

Two questions to keep asking yourself in every module: **"Why are we doing
this?"** and **"What business question does this help us answer?"**

## The Business Narrative

> You've just joined the analytics team at **Plato's Pizza**, a
> single-location pizza restaurant. Management has handed you a full
> year (2015) of raw sales data and wants to understand sales, product
> performance, and ordering patterns well enough to make decisions.

Every module maps to a specific request from that team:

| # | Business Request | Answered in |
|---|---|---|
| 1 | "Get our historical sales data into the analytics database." | Modules 1-2 |
| 2 | "What does the raw dataset look like?" | Module 3 |
| 3 | "Which pizzas/categories generate the most revenue?" | Modules 4-5 |
| 4 | "When are customers ordering the most?" | Modules 6, 9 |
| 5 | "Are there products that sell a lot but earn little?" | Modules 6, 10 |
| 6 | "What should management know about our sales performance?" | Module 10 |
| Final | "Build an executive dashboard management can explore." | Module 11 |

## Stage Progression

| Stage | The student can say... | Modules |
|---|---|---|
| 1 | "I can read the data." | 0-2 |
| 2 | "I can query the data." | 3-6 |
| 3 | "I can manipulate the data." | 7-8 |
| 4 | "I can analyze the data." | 9 |
| 5 | "I can visualize the data." | 9-10 |
| 6 | "I can explain what the data means." | 10 |
| 7 | "I can build an analytics product." | 11-12 |

## Module Map

| # | Module | Difficulty | Key files |
|---|---|---|---|
| 0 | Kickoff: meet the business & the data | Beginner | `data/README.md` |
| 1 | Data Engineering Foundation: Docker + Postgres + schema design | Beginner | `docker-compose.yml`, `sql/01_schema.sql` |
| 2 | Loading & validating data | Beginner | `src/load_data.py` |
| 3 | SQL Level 1-3: SELECT, WHERE, ORDER BY | Beginner | `sql/03_basic_queries.sql`, `docs/sql-exercises/01_*` |
| 4 | SQL Level 4-6: Aggregations, GROUP BY, HAVING | Beginner→Intermediate | `sql/04_aggregation.sql`, `docs/sql-exercises/02_*` |
| 5 | SQL Level 7-8: CASE, JOINs | Intermediate | `sql/04_aggregation.sql`, `sql/05_joins.sql`, `docs/sql-exercises/03_*` |
| 6 | SQL Level 9-10: CTEs, Window Functions (Analyst Challenge) | Intermediate | `sql/06_ctes.sql`, `sql/07_advanced_analysis.sql`, `docs/sql-exercises/04_*` |
| 7 | Python extraction: SQL → pandas bridge | Beginner→Intermediate | `src/extract_data.py`, `notebooks/01_*` |
| 8 | Data quality & cleaning | Intermediate | `src/clean_data.py`, `notebooks/02_*` |
| 9 | Feature engineering & EDA | Intermediate | `notebooks/03_eda.ipynb` |
| 10 | Business analysis & storytelling | Intermediate | `notebooks/04_business_analysis.ipynb`, `reports/insights.md` |
| 11 | Streamlit dashboard | Intermediate | `dashboard/` |
| 12 | Capstone project & presentation | Intermediate | `docs/capstone.md` |

## Full Progression Diagram

```
Docker → Postgres (star schema) → SQL (10 levels) → Python extraction →
Data quality & cleaning → Feature engineering → EDA → Visualization →
Storytelling → Streamlit dashboard → Capstone
```

## Where everything lives

- **Learn a concept:** `sql/0X_*.sql` (taught, worked examples) or the
  relevant `notebooks/0X_*.ipynb`.
- **Practice a concept:** `docs/sql-exercises/` (🟢🟡🔴 tiers) or a
  notebook's "Your Turn" section.
- **Check your work:** `docs/sql-solutions/` — only after attempting.
- **See the finished analysis:** `reports/insights.md`.
- **See the finished product:** `dashboard/app.py` (`streamlit run dashboard/app.py`).
- **Teach this course:** `docs/instructor-guide.md`.
- **Take this course:** `docs/student-guide.md`.
- **Be graded on this course:** `docs/rubric.md`.
- **Finish this course:** `docs/capstone.md`.
