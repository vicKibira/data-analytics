"""
Plato's Pizza — Executive Analytics Dashboard (capstone deliverable).

Run with:  streamlit run dashboard/app.py

Architecture: data access lives in dashboard/data.py, filter widgets in
dashboard/components/filters.py, KPI cards in components/kpis.py, and every
chart in components/charts.py. app.py only wires these together and lays
out the page — it contains no SQL, no data transformation, and no chart
code of its own.
"""

from __future__ import annotations

import streamlit as st

from components.charts import (
    render_orders_by_hour,
    render_orders_by_weekday,
    render_product_mix,
    render_revenue_by_dimension,
    render_sales_trend,
    render_top_bottom_products,
)
from components.filters import render_filters
from components.kpis import render_kpis
from data import apply_filters, load_data

st.set_page_config(page_title="Plato's Pizza — Sales Analytics", page_icon="🍕", layout="wide")

st.title("🍕 Plato's Pizza — Executive Sales Analytics")
st.markdown(
    "Interactive view of 2015 sales performance, built on the same "
    "database and analysis pipeline used throughout this course "
    "(`sql/` → `src/extract_data.py` → this dashboard). "
    "Use the filters in the sidebar to explore by date range, category, and size."
)

try:
    raw_df = load_data()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

if raw_df.attrs.get("source") == "processed CSV fallback":
    st.warning(
        "Could not reach the Postgres database — showing data from "
        "`data/processed/pizza_sales_clean.csv` instead. Run "
        "`docker compose up -d && python src/load_data.py` for live data.",
        icon="⚠️",
    )

filters = render_filters(raw_df)
df = apply_filters(raw_df, filters["date_range"], filters["categories"], filters["sizes"])

st.header("Executive Overview")
render_kpis(df)

st.divider()
st.header("Sales Trends")
freq_label = st.radio("Aggregate by", ["Daily", "Weekly", "Monthly"], index=2, horizontal=True)
render_sales_trend(df, freq_label)

st.divider()
st.header("Product Performance")
tab1, tab2 = st.tabs(["Top & Bottom Pizzas", "By Category & Size"])
with tab1:
    render_top_bottom_products(df, n=10)
with tab2:
    render_revenue_by_dimension(df)

st.divider()
st.header("Order Patterns")
col1, col2 = st.columns(2)
with col1:
    render_orders_by_hour(df)
with col2:
    render_orders_by_weekday(df)

st.divider()
st.header("Product Mix Over Time")
render_product_mix(df)

st.divider()
with st.expander("Data notes & limitations"):
    st.markdown(
        "- Single restaurant location, single calendar year (2015) — no store or year-over-year comparison.\n"
        "- No customer identifier, order channel, or cost/margin data — every figure here is **revenue**, not profit.\n"
        "- The source file had mixed date formats (`M/D/YYYY` and `D-M-YYYY`); this was identified and corrected "
        "during loading — see `data/README.md` and `sql/02_data_quality.sql`.\n"
        "- Full analysis, SQL, and narrative write-up: `reports/insights.md`, `notebooks/`, and `sql/`."
    )
