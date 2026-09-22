# Student Guide

Welcome to the analytics team at **Plato's Pizza**. Management just handed
you a year of raw sales data (`data/raw/pizza_sales.csv`) and a stack of
questions. This guide is your map through the project — read
`docs/course-roadmap.md` first for the full picture, then come back here
for how to actually work through each module.

## How this course works

Every module is a real business request, not an abstract exercise. Before
you write any code, you should be able to answer: **what question am I
trying to answer, and for whom?** If you can't answer that, re-read the
module's business request before touching the keyboard.

The rhythm is always: **Learn → Practice → Investigate → Build → Explain.**
You'll see a new concept demonstrated (in a `sql/0X_*.sql` file or a
notebook), then you'll practice it yourself, then you'll use it to answer
a real question, then you'll have to explain — in plain English — what you
found.

## The exercise pattern

Every practice problem, in SQL and Python alike, follows:

```
Business Question  →  Your Task  →  Hints  →  Expected Output
```

Try to answer the Business Question yourself, using the Hints only if
you're stuck, and check your work against the Expected Output — not
against the solution file. **Only open a solutions file after you've
genuinely attempted the problem.** Struggling productively for 10-15
minutes on a hard query teaches you far more than reading the answer
immediately.

- SQL practice: `docs/sql-exercises/` — solutions in `docs/sql-solutions/`.
- Python/notebook practice: each notebook's "Your Turn" section — no
  separate solution file; discuss with an instructor or peer, or compare
  your approach against the notebook's own worked examples above it.

## Difficulty tiers (SQL exercises)

- 🟢 **Warm-up** — straightforward application of what you just learned.
- 🟡 **Analyst** — combines two concepts, sometimes from different levels.
- 🔴 **Business Challenge** — you have to reason about the business
  question BEFORE you can even start writing SQL. These are meant to be
  hard. If you can't get one in 15-20 minutes, move on and come back later
  — don't let one query block your progress through the module.

## Setting up the project

```bash
git clone <this-repo>
cd data-analytics

docker compose up -d              # starts Postgres
cp .env.example .env              # first time only
pip install -r requirements.txt
python src/load_data.py           # loads and validates the data

jupyter lab notebooks/            # for the Python phase
streamlit run dashboard/app.py    # for the capstone dashboard
```

If anything fails, read the error message fully before asking for help —
`src/load_data.py` and `src/clean_data.py` are both written to fail with a
clear, specific message rather than a cryptic stack trace.

## Working through the modules

1. **Modules 0-2 (Data Engineering):** get the database running and
   understand WHY each table is shaped the way it is before moving on —
   the whole SQL phase depends on this schema making sense to you.
2. **Modules 3-6 (SQL):** work through `sql/03_basic_queries.sql` through
   `sql/07_advanced_analysis.sql` in order — read the comments, run every
   query yourself (don't just read the file), predict the result before
   you see it. Then do the matching exercises. Level 10 (window functions)
   is marked "Analyst Challenge" — genuinely optional, go for it if you
   want to go further.
3. **Modules 7-8 (Python foundation):** notice that Notebook 02 re-reads
   the RAW csv, not the database — that's intentional (see the notebook's
   first cell for why). Run every cell yourself; don't just read outputs.
4. **Modules 9-10 (EDA & storytelling):** before writing a single chart,
   write down: what's the question, what's the metric, what data do I
   need? Only then write code. Every chart needs a one-sentence Insight
   and Business Implication underneath it — a chart with no interpretation
   isn't finished.
5. **Module 11 (Dashboard):** this is where everything comes together.
   You are not writing new analysis — you're reusing what you already
   built (`src/extract_data.py`, `src/utils.py`'s color/style helpers) and
   wiring it to interactive filters.
6. **Module 12 (Capstone):** see `docs/capstone.md`.

## What "done" looks like for each phase

- **SQL:** you can write a 3-table JOIN with a GROUP BY and a HAVING
  clause from scratch, for a NEW business question you haven't seen before.
- **Python:** you can take an unfamiliar CSV and independently run the
  full data-quality checklist without being told to.
- **EDA/Storytelling:** you can look at a chart and write an Observation →
  Explanation → Implication → Next question without prompting.
- **Dashboard:** you can explain, to a non-technical person, what each
  filter does and why each chart is the form it is.

## Getting unstuck

1. Re-read the business question. What are you actually being asked?
2. Check `data/README.md` — is the column/relationship you need actually
   there?
3. Check the matching `sql/0X_*.sql` or notebook — is there a worked
   example close to what you need?
4. Try a smaller version of the problem (fewer columns, `LIMIT 10`, a
   single category) before the full question.
5. Ask — but bring what you've tried, not just "it doesn't work."
