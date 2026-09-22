"""
Shared utilities: database connections, logging, and time-feature helpers
used across load_data.py, extract_data.py, clean_data.py, the notebooks, and
the Streamlit dashboard.

Centralizing these here means every part of the project builds a DB
connection and computes date/time features exactly the same way — a
recurring theme of this course: don't repeat business logic, reuse it.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Weekday order used everywhere a chart or groupby needs Monday-first sorting
# instead of pandas' default alphabetical order.
WEEKDAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# ----------------------------------------------------------------------------
# SHARED CHART STYLE
# One palette, used everywhere a chart is drawn (every notebook + the
# Streamlit dashboard) so the project reads as one visual system instead of
# a different color scheme per chart. Hues are fixed, validated categorical
# steps (not picked by eye) — the SAME pizza_category always gets the SAME
# color in every chart in this project, and colors are assigned by fixed
# slot order, never re-cycled when a filter changes which categories show.
# ----------------------------------------------------------------------------
CATEGORY_COLORS = {
    "Classic": "#2a78d6",   # slot 1 - blue
    "Chicken": "#eb6834",   # slot 2 - orange
    "Supreme": "#1baf7a",   # slot 3 - aqua
    "Veggie":  "#eda100",   # slot 4 - yellow
}
WEEKEND_COLORS = {
    "Weekday": "#2a78d6",   # slot 1 - blue
    "Weekend": "#eb6834",   # slot 2 - orange
}
# Size is ordinal (S < M < L < XL < XXL), so it gets a single-hue sequential
# ramp (light -> dark blue) instead of unrelated categorical hues.
SIZE_ORDER = ["S", "M", "L", "XL", "XXL"]
SIZE_COLORS = dict(zip(SIZE_ORDER, ["#9ec5f4", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]))

CHART_INK = "#0b0b0b"
CHART_MUTED = "#898781"
CHART_GRID = "#e1e0d9"
CHART_SURFACE = "#fcfcfb"


def apply_chart_style() -> None:
    """Apply one consistent, low-clutter matplotlib/seaborn style for every
    chart in this project: light surface, muted gridlines only on the value
    axis, no chart border box. Call this once per notebook/script, right
    after importing matplotlib — every chart drawn afterward inherits it.
    """
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": CHART_SURFACE,
        "axes.facecolor": CHART_SURFACE,
        "axes.edgecolor": CHART_GRID,
        "axes.labelcolor": CHART_INK,
        "axes.titleweight": "bold",
        "text.color": CHART_INK,
        "xtick.color": CHART_MUTED,
        "ytick.color": CHART_MUTED,
        "grid.color": CHART_GRID,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "font.family": "sans-serif",
        "font.size": 11,
    })


def setup_logging(name: str = "pizza_analytics") -> logging.Logger:
    """Return a logger that prints timestamped, leveled messages to stdout.

    Every script in this project calls this instead of bare `print()` so
    that output is consistent and can be redirected/filtered like a real
    pipeline's logs.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # avoid duplicate handlers on re-import
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_db_config() -> dict:
    """Read DB connection settings from environment variables (.env).

    We NEVER hardcode credentials in code. `load_dotenv()` reads a local
    `.env` file (git-ignored) into the environment; in production the same
    variables would simply be set by the deployment platform instead.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "name": os.getenv("DB_NAME", "pizza_analytics"),
        "user": os.getenv("DB_USER", "pizza_admin"),
        "password": os.getenv("DB_PASSWORD", "pizza_pw"),
    }


def get_engine() -> Engine:
    """Build a SQLAlchemy engine from environment variables.

    SQLAlchemy (rather than a bare psycopg2 connection) is used because
    pandas' `read_sql` / `to_sql` are built to work with it directly.
    """
    cfg = get_db_config()
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['name']}"
    )
    return create_engine(url)


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse `order_date` values that mix TWO real formats found in the raw
    export (see data/README.md "Data quality findings"):

        - slash format:  'M/D/YYYY'   e.g. '1/1/2015'   (19,587 rows)
        - dash format:    'D-M-YYYY'   e.g. '13-01-2015'  (29,033 rows)

    The two formats are interleaved by order_id, not a clean batch cutover,
    so a single `pd.to_datetime(series, format=...)` call cannot parse the
    whole column. We detect the format per-row from the separator character
    (a `/` only ever appears in the slash format in this file) and parse
    each subset with its own explicit format.
    """
    is_slash = series.astype(str).str.contains("/")
    out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    out.loc[is_slash] = pd.to_datetime(series[is_slash], format="%m/%d/%Y")
    out.loc[~is_slash] = pd.to_datetime(series[~is_slash], format="%d-%m-%Y")
    return out


def add_time_features(df: pd.DataFrame, date_col: str = "order_date", time_col: str = "order_time") -> pd.DataFrame:
    """Add the standard set of analytical date/time columns used throughout
    the course (EDA notebooks, business-analysis notebook, dashboard).

    Expects `date_col` to already be a proper datetime64 column (parsed by
    clean_data.parse_mixed_dates or already a DATE type coming back from
    Postgres) and `time_col` to be a proper time/datetime column.

    Returns a NEW DataFrame (does not mutate the input) with:
        order_month      -- 'January', ..., 'December' (categorical, ordered)
        order_day_name    -- 'Monday', ..., 'Sunday' (categorical, ordered)
        order_hour        -- 0-23
        is_weekend        -- bool, Saturday/Sunday
        time_of_day       -- Morning / Afternoon / Evening / Late Night bucket
    """
    out = df.copy()
    dt = pd.to_datetime(out[date_col])
    # Normalize date_col itself to real datetime64 — a DATE column coming
    # back from Postgres via psycopg2 arrives as plain datetime.date
    # objects (object dtype), which silently breaks anything expecting
    # .dt accessors, resample(), or comparisons against pd.Timestamp.
    out[date_col] = dt
    out["order_month"] = pd.Categorical(dt.dt.month_name(), categories=MONTH_ORDER, ordered=True)
    out["order_day_name"] = pd.Categorical(dt.dt.day_name(), categories=WEEKDAY_ORDER, ordered=True)
    out["is_weekend"] = dt.dt.day_name().isin(["Saturday", "Sunday"])

    hour = pd.to_datetime(out[time_col].astype(str), format="mixed").dt.hour
    out["order_hour"] = hour
    out["time_of_day"] = pd.cut(
        hour,
        bins=[-1, 10, 14, 17, 21, 24],
        labels=["Morning", "Lunch", "Afternoon", "Dinner", "Late Night"],
    )
    return out
