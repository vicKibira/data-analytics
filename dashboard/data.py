"""
Dashboard data-loading layer.

Keeps DATABASE logic (how we get the data) separate from PRESENTATION logic
(components/kpis.py, components/charts.py, app.py). Every chart and KPI in
this dashboard is built from the SAME `load_data()` call defined here — the
same discipline as src/extract_data.py being the single source of truth for
notebooks.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DASHBOARD_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils import add_time_features  # noqa: E402


@st.cache_data(ttl=600, show_spinner="Loading sales data...")
def load_data() -> pd.DataFrame:
    """Return the full, feature-engineered sales fact used by every chart.

    Primary source: the live Postgres database (src/extract_data.py) — the
    same JOIN pattern taught in sql/05_joins.sql and used in every
    notebook. If the database isn't reachable (e.g. `docker compose up`
    hasn't been run), we fall back to the pre-computed
    data/processed/pizza_sales_clean.csv produced by src/clean_data.py, so
    the dashboard still runs for a quick look — but a warning banner makes
    clear which data source is actually in use.
    """
    try:
        from extract_data import load_sales_data

        df = load_sales_data()
        df = add_time_features(df, date_col="order_date", time_col="order_time")
        df.attrs["source"] = "database"
        return df
    except Exception:
        processed_path = PROJECT_ROOT / "data" / "processed" / "pizza_sales_clean.csv"
        if not processed_path.exists():
            raise RuntimeError(
                "Could not reach the database AND data/processed/pizza_sales_clean.csv "
                "does not exist. Run `docker compose up -d && python src/load_data.py`, "
                "or `python src/clean_data.py` to generate the fallback file."
            )
        df = pd.read_csv(processed_path, parse_dates=["order_date"])
        df.attrs["source"] = "processed CSV fallback"
        return df


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    categories: list[str],
    sizes: list[str],
) -> pd.DataFrame:
    """Apply the sidebar filters. Pure function, no Streamlit calls inside —
    keeps filtering logic testable independently of the UI."""
    start, end = date_range
    mask = (
        (df["order_date"] >= pd.Timestamp(start))
        & (df["order_date"] <= pd.Timestamp(end))
        & (df["pizza_category"].isin(categories))
        & (df["pizza_size"].isin(sizes))
    )
    return df.loc[mask]
