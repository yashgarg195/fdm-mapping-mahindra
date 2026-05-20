"""
Penetration Tab — Zone gauges, product readiness, specialist density.
Fixed: Proper penetration calculation using unique trained employees,
handles missing columns gracefully, accurate specialist count.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.constants import BRAND_RED, BRAND_CHARCOAL
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
        if zones:
            # Limit to max 6 columns per row
            rows_needed = (len(zones) + 5) // 6
            z_idx = 0
            for row_num in range(rows_needed):
                batch = zones[z_idx:z_idx + 6]
                cols = st.columns(len(batch))
                for i, zone in enumerate(batch):
                    zdf = unified_df[unified_df["Zone"] == zone]
                    total = zdf["Star ID"].nunique() if "Star ID" in zdf.columns else len(zdf)
                    if "Training year" in zdf.columns and "Star ID" in zdf.columns:
                        trained = zdf[zdf["Training year"].notna()]["Star ID"].nunique()
                    else:
                        trained = 0
                    pct = round(trained / max(total, 1) * 100, 1)
                    with cols[i]:
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=pct,
                            title={"text": zone, "font": {"size": 14, "color": "#231F20"}},
                            number={"suffix": "%", "font": {"color": "#231F20"}},
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
                        fig.update_layout(
                            height=200, margin=dict(t=40, b=10, l=20, r=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                        )
                        st.plotly_chart(fig, key=f"gauge_{zone}_{row_num}")
                z_idx += 6
    else:
        st.info("Zone data not available.")

    # ── Dealership Penetration Table ────────────────────────────────────────
    st.markdown("#### Dealership Penetration Table")
    pen = dealership_penetration(unified_df)
    if not pen.empty:
        st.dataframe(pen, height=400)
    else:
        st.info("No dealership penetration data.")

    # ── Product Readiness / L3-L4 Density ───────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Product Readiness")
        prod = product_readiness(unified_df)
        if not prod.empty:
            st.dataframe(prod.head(20), height=300)
        else:
            st.info("No product readiness data.")

    with chart2:
        st.markdown("#### L3/L4 Specialist Density by State")
        if "State" in unified_df.columns and "SKILL LEVEL - POST" in unified_df.columns:
            spec = unified_df[unified_df["SKILL LEVEL - POST"].isin(["L3", "L4"])]
            if not spec.empty and "Star ID" in spec.columns:
                state_counts = spec.groupby("State")["Star ID"].nunique().reset_index()
                state_counts.columns = ["State", "Specialist_Count"]
                state_counts = state_counts.sort_values("Specialist_Count", ascending=True)
                fig = px.bar(
                    state_counts,
                    y="State", x="Specialist_Count", orientation="h",
                    color_discrete_sequence=[BRAND_RED],
                )
                fig.update_layout(
                    plot_bgcolor="white",
                    margin=dict(t=20, b=20, l=20, r=20),
                    yaxis_title="",
                )
                st.plotly_chart(fig, key="specialist_density")
            else:
                st.info("No L3/L4 specialists found.")
        else:
            st.info("Required columns not available.")
