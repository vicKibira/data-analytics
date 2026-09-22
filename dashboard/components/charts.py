"""Chart-rendering functions. Each function takes the (already filtered)
sales DataFrame and renders ONE chart via st.pyplot — no filtering or data
loading happens here, so these functions are reused as-is regardless of
which filters are active.

Reuses the exact same color palette and matplotlib style
(src/utils.py: CATEGORY_COLORS, SIZE_COLORS, WEEKEND_COLORS,
apply_chart_style) as the notebooks, so a chart here and the equivalent
chart in notebooks/03_eda.ipynb look like they came from the same system —
because they did.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from utils import CATEGORY_COLORS, SIZE_COLORS, SIZE_ORDER, WEEKEND_COLORS, apply_chart_style  # noqa: E402

apply_chart_style()

CATEGORY_ORDER = ["Classic", "Chicken", "Supreme", "Veggie"]
_DOLLARS = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")


def render_sales_trend(df: pd.DataFrame, freq_label: str) -> None:
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
    freq = freq_map[freq_label]
    trend = df.set_index("order_date").resample(freq)["total_price"].sum()

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(trend.index, trend.values, color=CATEGORY_COLORS["Classic"], linewidth=2)
    ax.fill_between(trend.index, trend.values, color=CATEGORY_COLORS["Classic"], alpha=0.08)
    ax.set_xlim(trend.index.min(), trend.index.max())
    ax.set_title(f"{freq_label} Revenue")
    ax.set_ylabel("Revenue")
    ax.yaxis.set_major_formatter(_DOLLARS)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_top_bottom_products(df: pd.DataFrame, n: int = 10) -> None:
    flavor_revenue = df.groupby("pizza_name")["total_price"].sum().sort_values(ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        top = flavor_revenue.head(n)
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.barh(top.index[::-1], top.values[::-1], color=CATEGORY_COLORS["Classic"])
        ax.set_title(f"Top {n} Pizzas by Revenue")
        ax.xaxis.set_major_formatter(_DOLLARS)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)

    with col2:
        bottom = flavor_revenue.tail(n).sort_values()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.barh(bottom.index, bottom.values, color=CATEGORY_COLORS["Chicken"])
        ax.set_title(f"Bottom {n} Pizzas by Revenue")
        ax.xaxis.set_major_formatter(_DOLLARS)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)


def render_revenue_by_dimension(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        cat_rev = df.groupby("pizza_category")["total_price"].sum()
        cat_rev = cat_rev.reindex([c for c in CATEGORY_ORDER if c in cat_rev.index])
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.bar(cat_rev.index, cat_rev.values, color=[CATEGORY_COLORS[c] for c in cat_rev.index])
        ax.set_title("Revenue by Category")
        ax.yaxis.set_major_formatter(_DOLLARS)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)

    with col2:
        size_rev = df.groupby("pizza_size")["total_price"].sum()
        size_rev = size_rev.reindex([s for s in SIZE_ORDER if s in size_rev.index])
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.bar(size_rev.index, size_rev.values, color=[SIZE_COLORS[s] for s in size_rev.index])
        ax.set_title("Revenue by Size")
        ax.yaxis.set_major_formatter(_DOLLARS)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)


def render_orders_by_hour(df: pd.DataFrame) -> None:
    hourly = df.groupby("order_hour")["order_id"].nunique()
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(hourly.index, hourly.values, color=CATEGORY_COLORS["Classic"])
    ax.set_title("Orders by Hour of Day")
    ax.set_xlabel("Hour (24h)")
    ax.set_ylabel("Orders")
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_orders_by_weekday(df: pd.DataFrame) -> None:
    from utils import WEEKDAY_ORDER

    daily = df.drop_duplicates("order_id")
    counts = daily.groupby("order_day_name", observed=True)["order_id"].nunique()
    counts = counts.reindex([d for d in WEEKDAY_ORDER if d in counts.index])
    colors = [WEEKEND_COLORS["Weekend"] if d in ("Saturday", "Sunday") else WEEKEND_COLORS["Weekday"] for d in counts.index]

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(counts.index, counts.values, color=colors)
    ax.set_title("Orders by Day of Week")
    ax.set_ylabel("Orders")
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
    st.caption("🔵 Weekday · 🟠 Weekend")


def render_product_mix(df: pd.DataFrame) -> None:
    mix = df.groupby([pd.Grouper(key="order_date", freq="ME"), "pizza_category"])["total_price"].sum().unstack("pizza_category")
    present = [c for c in CATEGORY_ORDER if c in mix.columns]
    mix = mix[present].fillna(0)
    if mix.empty:
        st.info("Not enough data in the selected range to show product mix.")
        return
    share = mix.div(mix.sum(axis=1).replace(0, 1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 4.5))
    bottom = None
    for cat in present:
        ax.bar(share.index, share[cat], bottom=bottom, label=cat, color=CATEGORY_COLORS[cat], width=20)
        bottom = share[cat] if bottom is None else bottom + share[cat]
    ax.set_title("Revenue Mix by Category, by Month")
    ax.set_ylabel("% of monthly revenue")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), title="Category")
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
