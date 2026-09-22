#!/usr/bin/env python3
"""
extract_data.py — "We know how to ask the database questions. Now let's
bring the data into Python so we can investigate it more deeply."

This module is the bridge between Phase 2 (SQL) and Phase 3 (Python). The
key lesson it teaches: SQL is used to retrieve and JOIN data close to the
database (it's what the database is good at); pandas is used to continue
the analysis once the data is small enough to live in memory.

Every notebook, and the Streamlit dashboard, import functions from this
module instead of writing raw SQL inline — one reusable, tested source of
truth for "how do we get sales data out of Postgres."

Usage as a script (prints a quick sanity check):
    python src/extract_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import get_engine, setup_logging  # noqa: E402

logger = setup_logging("extract_data")


def get_connection():
    """Return a SQLAlchemy engine connected to the pizza_analytics database.

    A thin, explicitly-named wrapper around utils.get_engine() — kept here
    so this module is self-contained and its public API matches what an
    analyst would expect: get_connection(), run_query(), load_*().
    """
    return get_engine()


def run_query(query: str, params: dict | None = None) -> pd.DataFrame:
    """Run any SQL query against the database and return the result as a
    pandas DataFrame. This is the one function every other function in this
    file (and every notebook) is built on top of.
    """
    engine = get_connection()
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


def load_sales_data() -> pd.DataFrame:
    """Return the full, analysis-ready sales fact: one row per pizza
    line-item, with every dimension (pizza flavor, category, size, order
    date/time) already joined in. This is the main dataset the EDA and
    business-analysis notebooks and the dashboard are built on.

    Equivalent to the JOIN pattern taught in sql/05_joins.sql.
    """
    query = """
        SELECT
            od.order_details_id,
            od.order_id,
            o.order_date,
            o.order_time,
            p.pizza_name_id,
            pt.pizza_type_id,
            pt.name        AS pizza_name,
            pt.category    AS pizza_category,
            pt.ingredients,
            p.size          AS pizza_size,
            p.price          AS unit_price,
            od.quantity,
            od.total_price
        FROM pizza.order_details od
        JOIN pizza.orders      o  ON od.order_id       = o.order_id
        JOIN pizza.pizzas      p  ON od.pizza_name_id   = p.pizza_name_id
        JOIN pizza.pizza_types pt ON p.pizza_type_id    = pt.pizza_type_id
        ORDER BY od.order_details_id;
    """
    logger.info("Extracting full sales fact (order_details JOIN orders JOIN pizzas JOIN pizza_types)...")
    df = run_query(query)
    logger.info(f"Extracted {len(df):,} rows, {len(df.columns)} columns.")
    return df


def load_orders() -> pd.DataFrame:
    """Return one row per order (no pizza-level detail) — useful for
    order-level metrics like average order value and items-per-order."""
    query = """
        SELECT
            o.order_id,
            o.order_date,
            o.order_time,
            COUNT(od.order_details_id) AS n_line_items,
            SUM(od.quantity)           AS n_pizzas,
            SUM(od.total_price)        AS order_value
        FROM pizza.orders o
        JOIN pizza.order_details od ON o.order_id = od.order_id
        GROUP BY o.order_id, o.order_date, o.order_time
        ORDER BY o.order_id;
    """
    return run_query(query)


def load_pizza_catalog() -> pd.DataFrame:
    """Return the pizza dimension (flavor x size) on its own — useful for
    product-catalog questions that don't need any sales data."""
    query = """
        SELECT
            p.pizza_name_id,
            pt.pizza_type_id,
            pt.name     AS pizza_name,
            pt.category AS pizza_category,
            pt.ingredients,
            p.size,
            p.price
        FROM pizza.pizzas p
        JOIN pizza.pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
        ORDER BY pt.pizza_type_id, p.price;
    """
    return run_query(query)


if __name__ == "__main__":
    sales = load_sales_data()
    print(sales.head())
    print(f"\nShape: {sales.shape}")
    print(f"Total revenue: ${sales['total_price'].sum():,.2f}")
