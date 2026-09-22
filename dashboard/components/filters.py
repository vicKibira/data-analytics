"""Sidebar filter controls. Renders the filter widgets and returns the
selections app.py needs — no data loading or charting happens here."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_filters(df: pd.DataFrame) -> dict:
    st.sidebar.header("Filters")
    st.sidebar.caption("Applied to every KPI and chart on this page.")

    min_date, max_date = df["order_date"].min().date(), df["order_date"].max().date()
    date_range = st.sidebar.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    # st.date_input returns a single date while the user is mid-selection;
    # guard against that instead of crashing the page.
    if not isinstance(date_range, tuple) or len(date_range) != 2:
        date_range = (min_date, max_date)

    categories = sorted(df["pizza_category"].unique())
    selected_categories = st.sidebar.multiselect(
        "Pizza category", options=categories, default=categories,
    )

    sizes = ["S", "M", "L", "XL", "XXL"]
    sizes = [s for s in sizes if s in df["pizza_size"].unique()]
    selected_sizes = st.sidebar.multiselect(
        "Pizza size", options=sizes, default=sizes,
    )

    if st.sidebar.button("Reset filters"):
        st.rerun()

    return {
        "date_range": date_range,
        "categories": selected_categories or categories,
        "sizes": selected_sizes or sizes,
    }
