#!/usr/bin/env python3
"""
load_data.py — Business Request 1: "Get our historical sales data into the
analytics database."

This is the Phase 1 (Data Engineering) deliverable. It is intentionally the
FIRST script in the project because every later phase (SQL practice, Python
extraction, the dashboard) depends on the database it builds.

What it does, in order:
    1. Connect to Postgres using credentials from environment variables
       (never hardcoded — see .env.example).
    2. (Re)create the schema and tables by running sql/01_schema.sql.
    3. Read the raw CSV (data/raw/pizza_sales.csv).
    4. Validate it — never trust a file just because it opened.
    5. Transform it into the four normalized tables described in
       data/README.md (pizza_types, pizzas, orders, order_details),
       including parsing the mixed order_date formats (see
       utils.parse_mixed_dates) — this is fixed ONCE, here, upstream, so
       every SQL query and every pandas notebook downstream can simply
       trust that order_date is a real date.
    6. Load the four tables into Postgres in FK-safe order.
    7. Log progress and row counts; fail loudly and clearly on any error.

Run it from the project root, with the Postgres container already up:

    docker compose up -d
    cp .env.example .env            # first time only
    pip install -r requirements.txt
    python src/load_data.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, get_engine, parse_mixed_dates, setup_logging  # noqa: E402

logger = setup_logging("load_data")

REQUIRED_COLUMNS = [
    "pizza_id", "order_id", "pizza_name_id", "quantity", "order_date",
    "order_time", "unit_price", "total_price", "pizza_size",
    "pizza_category", "pizza_ingredients", "pizza_name",
]


def read_raw_csv(csv_path: Path) -> pd.DataFrame:
    logger.info(f"Reading raw CSV: {csv_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Read {len(df):,} rows, {len(df.columns)} columns")
    return df


def validate_raw(df: pd.DataFrame) -> None:
    """Fail fast and loudly if the raw file doesn't look like what we expect.

    This is deliberately simple (not a full validation framework) — the
    goal is to teach the HABIT of validating before loading, not to build
    a production data-quality tool.
    """
    logger.info("Validating raw data...")

    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")

    if df.empty:
        raise ValueError("Raw file has zero rows.")

    if df["pizza_id"].duplicated().any():
        raise ValueError("Duplicate pizza_id values found — expected a unique line-item id.")

    for col in ["quantity", "unit_price", "total_price"]:
        if (df[col] <= 0).any():
            raise ValueError(f"Found non-positive values in '{col}'.")

    calc_total = (df["quantity"] * df["unit_price"]).round(2)
    mismatches = (calc_total - df["total_price"]).abs() > 0.01
    if mismatches.any():
        raise ValueError(
            f"{mismatches.sum()} rows where total_price != quantity * unit_price."
        )

    n_nulls = df[REQUIRED_COLUMNS].isnull().sum().sum()
    if n_nulls:
        raise ValueError(f"Found {n_nulls} null values in required columns.")

    logger.info("Validation passed: no missing columns, no nulls, no duplicate ids, "
                "no non-positive values, total_price is internally consistent.")


def transform(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split the flat raw DataFrame into the four normalized tables."""
    logger.info("Transforming raw data into normalized tables...")

    df = df.copy()
    df["order_date_parsed"] = parse_mixed_dates(df["order_date"])
    df["pizza_type_id"] = df["pizza_name_id"].str.rsplit("_", n=1).str[0]

    pizza_types = (
        df[["pizza_type_id", "pizza_name", "pizza_category", "pizza_ingredients"]]
        .drop_duplicates(subset="pizza_type_id")
        .rename(columns={"pizza_name": "name", "pizza_category": "category", "pizza_ingredients": "ingredients"})
        .sort_values("pizza_type_id")
        .reset_index(drop=True)
    )

    pizzas = (
        df[["pizza_name_id", "pizza_type_id", "pizza_size", "unit_price"]]
        .drop_duplicates(subset="pizza_name_id")
        .rename(columns={"pizza_size": "size", "unit_price": "price"})
        .sort_values("pizza_name_id")
        .reset_index(drop=True)
    )

    orders = (
        df[["order_id", "order_date_parsed", "order_time"]]
        .drop_duplicates(subset="order_id")
        .rename(columns={"order_date_parsed": "order_date"})
        .sort_values("order_id")
        .reset_index(drop=True)
    )
    orders["order_id"] = orders["order_id"].astype(int)

    order_details = (
        df[["pizza_id", "order_id", "pizza_name_id", "quantity", "total_price"]]
        .rename(columns={"pizza_id": "order_details_id"})
        .sort_values("order_details_id")
        .reset_index(drop=True)
    )
    order_details["order_details_id"] = order_details["order_details_id"].astype(int)
    order_details["order_id"] = order_details["order_id"].astype(int)
    order_details["quantity"] = order_details["quantity"].astype(int)

    logger.info(
        f"Transformed into: pizza_types={len(pizza_types)}, pizzas={len(pizzas)}, "
        f"orders={len(orders)}, order_details={len(order_details)}"
    )
    return {
        "pizza_types": pizza_types,
        "pizzas": pizzas,
        "orders": orders,
        "order_details": order_details,
    }


def create_schema(engine) -> None:
    schema_sql_path = PROJECT_ROOT / "sql" / "01_schema.sql"
    logger.info(f"Creating schema from {schema_sql_path}")
    sql_text = schema_sql_path.read_text()
    with engine.begin() as conn:
        for statement in sql_text.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    logger.info("Schema created.")


def load_tables(engine, tables: dict[str, pd.DataFrame]) -> None:
    # Insert order matters: parents before children (FK constraints).
    load_order = ["pizza_types", "pizzas", "orders", "order_details"]
    for table_name in load_order:
        df = tables[table_name]
        logger.info(f"Loading {len(df):,} rows into pizza.{table_name} ...")
        df.to_sql(
            table_name,
            engine,
            schema="pizza",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )
    logger.info("All tables loaded.")


def verify_load(engine, tables: dict[str, pd.DataFrame]) -> None:
    logger.info("Verifying row counts in the database match the source data...")
    with engine.connect() as conn:
        for table_name, df in tables.items():
            count = conn.execute(text(f"SELECT COUNT(*) FROM pizza.{table_name}")).scalar()
            expected = len(df)
            status = "OK" if count == expected else "MISMATCH"
            logger.info(f"  pizza.{table_name}: {count:,} rows (expected {expected:,}) [{status}]")
            if count != expected:
                raise RuntimeError(f"Row count mismatch in pizza.{table_name}")
    logger.info("Verification passed. Database is ready for SQL practice (sql/02_data_quality.sql).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load pizza sales data into Postgres.")
    parser.add_argument(
        "--csv", type=Path, default=PROJECT_ROOT / "data" / "raw" / "pizza_sales.csv",
        help="Path to the raw pizza_sales.csv file.",
    )
    args = parser.parse_args()

    try:
        engine = get_engine()
        raw_df = read_raw_csv(args.csv)
        validate_raw(raw_df)
        tables = transform(raw_df)
        create_schema(engine)
        load_tables(engine, tables)
        verify_load(engine, tables)
        logger.info("SUCCESS: pizza_sales.csv is now live in the pizza_analytics database.")
    except Exception as exc:
        logger.error(f"FAILED to load data: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
