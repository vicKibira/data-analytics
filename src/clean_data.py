#!/usr/bin/env python3
"""
clean_data.py — Phase 3 data-quality-investigation-and-cleaning workflow.

WHY THIS SCRIPT RE-READS THE RAW CSV INSTEAD OF THE DATABASE
--------------------------------------------------------------
src/load_data.py already fixed the mixed date formats once, upstream, when
it built the database (see data/README.md — "clean once, at the source").
So why does this script do it AGAIN, here, in pandas?

Because in real analyst work you don't always receive data through a
perfectly-maintained warehouse. Often you're handed a raw export directly
(exactly what happened on this project: a single messy CSV). Part of being
a trustworthy analyst is being able to independently investigate and clean
a raw file yourself — never assuming someone upstream already checked it.
notebooks/01_data_exploration.ipynb and 02_data_cleaning.ipynb use the
functions in this file to practice exactly that skill against
data/raw/pizza_sales.csv. From notebooks/03_eda.ipynb onward, we switch to
querying the (already-clean) database via src/extract_data.py — the same
"SQL retrieves, Python analyzes" pattern used throughout the course.

Running this file also produces data/processed/pizza_sales_clean.csv — a
flat, feature-engineered file the dashboard can optionally read directly
for speed, without needing a live database connection.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, add_time_features, parse_mixed_dates, setup_logging  # noqa: E402

logger = setup_logging("clean_data")


# ----------------------------------------------------------------------------
# DATA QUALITY INVESTIGATION
# "Never trust a dataset just because it loaded successfully."
# Each function below checks ONE thing and returns a small, readable summary
# instead of silently fixing anything — investigation and cleaning are
# deliberately kept as separate steps.
# ----------------------------------------------------------------------------

def check_missing_values(df: pd.DataFrame) -> pd.Series:
    return df.isnull().sum()


def check_duplicates(df: pd.DataFrame, subset: str = "pizza_id") -> int:
    return int(df.duplicated(subset=subset).sum())


def check_date_formats(df: pd.DataFrame, col: str = "order_date") -> pd.Series:
    """Return counts of each date format pattern found in `col`.

    This is the check that originally surfaced the mixed-format issue
    documented in data/README.md — run it on any new raw file before
    assuming `pd.to_datetime` will parse it correctly.
    """
    is_slash = df[col].astype(str).str.contains("/")
    return pd.Series({
        "slash_format (M/D/YYYY)": is_slash.sum(),
        "dash_format (D-M-YYYY)": (~is_slash).sum(),
    })


def check_price_consistency(df: pd.DataFrame) -> int:
    """Return the count of rows where total_price != quantity * unit_price."""
    calc = (df["quantity"] * df["unit_price"]).round(2)
    return int(((calc - df["total_price"]).abs() > 0.01).sum())


def check_negative_or_zero(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    return pd.Series({c: int((df[c] <= 0).sum()) for c in cols})


def run_data_quality_report(df: pd.DataFrame) -> None:
    """Print the full data-quality checklist. Called from the CLI and from
    notebooks/01_data_exploration.ipynb."""
    logger.info("=" * 60)
    logger.info("DATA QUALITY REPORT")
    logger.info("=" * 60)
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Missing values per column:\n{check_missing_values(df)}")
    logger.info(f"Duplicate pizza_id rows: {check_duplicates(df)}")
    logger.info(f"Date format breakdown:\n{check_date_formats(df)}")
    logger.info(f"total_price mismatches: {check_price_consistency(df)}")
    logger.info(f"Non-positive values:\n{check_negative_or_zero(df, ['quantity', 'unit_price', 'total_price'])}")
    logger.info("=" * 60)


# ----------------------------------------------------------------------------
# CLEANING
# "Cleaning data" (fixing genuine defects: bad types, inconsistent formats)
# is kept distinct from "changing data" (altering actual business values,
# which we do NOT do here — every value in this dataset was already
# verified correct in data/README.md).
# ----------------------------------------------------------------------------

def clean_pizza_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the minimal, justified set of cleaning steps to the raw
    pizza_sales export. Each step is commented with WHY it's needed —
    a cleaning step with no justification doesn't belong here.
    """
    df = df.copy()

    # 1. Parse order_date: fixes the mixed M/D/YYYY vs D-M-YYYY formats
    #    found in check_date_formats(). Without this, ~60% of dates would
    #    either fail to parse or (worse) parse into the WRONG date silently.
    df["order_date"] = parse_mixed_dates(df["order_date"])

    # 2. Parse order_time into a proper time-of-day column instead of text.
    df["order_time"] = pd.to_datetime(df["order_time"], format="%H:%M:%S").dt.time

    # 3. Correct dtypes: these columns are whole numbers stored as floats
    #    by pandas' default CSV inference (e.g. 1.0 instead of 1) — not a
    #    business change, just representing the same values correctly.
    for col in ["pizza_id", "order_id", "quantity"]:
        df[col] = df[col].astype(int)

    # 4. Standardize text columns: strip stray whitespace. (Investigation
    #    confirmed 0 rows currently need this — but real raw exports
    #    routinely do, so we apply it defensively rather than skip it.)
    for col in ["pizza_size", "pizza_category", "pizza_name", "pizza_ingredients"]:
        df[col] = df[col].str.strip()

    # 5. Drop any exact duplicate rows, if present (0 found on this file —
    #    verified, not assumed).
    before = len(df)
    df = df.drop_duplicates(subset="pizza_id")
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} duplicate pizza_id rows.")

    return df.reset_index(drop=True)


# ----------------------------------------------------------------------------
# FEATURE ENGINEERING
# Only columns that make analytical sense given the ACTUAL data — no
# invented dimensions (no customer/channel features; this dataset has none).
# ----------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the analytical columns used throughout EDA, business analysis,
    and the dashboard. Reuses utils.add_time_features so the SAME logic
    (e.g. what counts as "weekend", how hours bucket into time_of_day) is
    never duplicated between this script, the notebooks, and the dashboard.
    """
    df = df.copy()
    df["order_time"] = df["order_time"].astype(str)  # add_time_features expects a parseable string/datetime
    df = add_time_features(df, date_col="order_date", time_col="order_time")

    # price_band: a simple, business-readable price tier per SKU (same
    # cutoffs as sql/04_aggregation.sql's Level 7 CASE example, so SQL and
    # Python agree on the same business definition).
    df["price_band"] = pd.cut(
        df["unit_price"],
        bins=[0, 12.5, 17.5, float("inf")],
        labels=["Budget", "Standard", "Premium"],
    )

    return df


def main() -> None:
    raw_path = PROJECT_ROOT / "data" / "raw" / "pizza_sales.csv"
    processed_path = PROJECT_ROOT / "data" / "processed" / "pizza_sales_clean.csv"

    logger.info(f"Reading raw file: {raw_path}")
    raw_df = pd.read_csv(raw_path)

    run_data_quality_report(raw_df)

    logger.info("Cleaning...")
    clean_df = clean_pizza_sales(raw_df)

    logger.info("Engineering features...")
    final_df = engineer_features(clean_df)

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(processed_path, index=False)
    logger.info(f"Wrote {len(final_df):,} rows, {len(final_df.columns)} columns to {processed_path}")


if __name__ == "__main__":
    main()
