"""Executive Overview KPI cards."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No data matches the current filters.")
        return

    total_revenue = df["total_price"].sum()
    total_orders = df["order_id"].nunique()
    total_pizzas = df["quantity"].sum()
    avg_order_value = total_revenue / total_orders if total_orders else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Pizzas Sold", f"{total_pizzas:,}")
    col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")
