"""
Penetration Tab — Zone gauges, product readiness, specialist density.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.constants import BRAND_RED, BRAND_CHARCOAL, ZONE_STATE_MAP
from analytics.penetration import dealership_penetration, product_readiness


def render_penetration(unified_df, filters):
    """Render the Product Penetration tab."""
    if unified_df is None or unified_df.empty:
        st.info("No data available for penetration analysis.")
        return

    # ── Zone Penetration Gauges ─────────────────────────────────────────────
    st.markdown("#### Zone Training Penetration")
    if "Zone" in unified_df.columns:
        zones = sorted(unified_df["Zone"].dropna().unique())
        cols = st.columns(min(len(zones), 6))
        for i, zone in enumerate(zones):
            zdf = unified_df[unified_df["Zone"] == zone]
            total = zdf["Star ID"].nunique() if "Star ID" in zdf.columns else len(zdf)
            trained = zdf[zdf["Training year"].notna()]["Star ID"].nunique() if "Star ID" in zdf.columns and "Training year" in zdf.columns else 0
            pct = trained / max(total, 1) * 100
            with cols[i % len(cols)]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct,
                    title={"text": zone, "font": {"size": 14}},
                    number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": BRAND_RED},
                        "steps": [
                            {"range": [0, 50], "color": "#FFCCCC"},
                            {"range": [50, 75], "color": "#FFE0A0"},
                            {"range": [75, 100], "color": "#CCFFCC"},
                        ],
                    },
                ))
                fig.update_layout(height=200, margin=dict(t=40, b=10, l=20, r=20))
                st.plotly_chart(fig, key=f"gauge_{zone}", use_container_width=True)
    else:
        st.info("Zone data not available.")

    # ── Dealership Penetration Table ────────────────────────────────────────
    st.markdown("#### Dealership Penetration Table")
    pen = dealership_penetration(unified_df)
    if not pen.empty:
        st.dataframe(pen, use_container_width=True, height=400)
    else:
        st.info("No dealership penetration data.")

    # ── Product Readiness / L3-L4 Density ───────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Product Readiness")
        prod = product_readiness(unified_df)
        if not prod.empty:
            st.dataframe(prod.head(20), use_container_width=True, height=300)
        else:
            st.info("No product readiness data.")

    with chart2:
        st.markdown("#### L3/L4 Specialist Density by State")
        if "State" in unified_df.columns and "SKILL LEVEL - POST" in unified_df.columns:
            spec = unified_df[unified_df["SKILL LEVEL - POST"].isin(["L3", "L4"])]
            if not spec.empty:
                state_counts = spec.groupby("State")["Star ID"].nunique().reset_index() if "Star ID" in spec.columns else spec.groupby("State").size().reset_index(name="Star ID")
                state_counts.columns = ["State", "Specialist_Count"]
                fig = px.bar(
                    state_counts.sort_values("Specialist_Count", ascending=True),
                    y="State", x="Specialist_Count", orientation="h",
                    color_discrete_sequence=[BRAND_RED],
                )
                fig.update_layout(plot_bgcolor="white", margin=dict(t=20, b=20, l=20, r=20), yaxis_title="")
                st.plotly_chart(fig, key="specialist_density", use_container_width=True)
            else:
                st.info("No L3/L4 specialists found.")
        else:
            st.info("Required columns not available.")
