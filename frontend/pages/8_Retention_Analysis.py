import streamlit as st
import pandas as pd
import plotly.express as px
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_customers
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Retention Analysis | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">VINTAGE RETENTION PERFORMANCE</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Customer Cohort Analysis</h2>', unsafe_allow_html=True)

if is_online:
    # Fetch Data
    with st.spinner("Analyzing cohort variance..."):
        res = get_customers(limit=1000)
        customers = res.get("customers", [])
    
    if customers:
        df = pd.DataFrame(customers)
        
        # 1. Cohort Generation (By Tenure)
        df["cohort"] = df["tenure"].apply(lambda x: f"Year {x}")
        
        # 2. Retention Metrics per Cohort
        cohort_summary = df.groupby("cohort").agg({
            "exited": ["count", "sum"],
            "balance": "mean",
            "estimated_salary": "mean"
        }).reset_index()
        
        cohort_summary.columns = ["Cohort", "Total", "Churned", "Avg Balance", "Avg Salary"]
        cohort_summary["Retention %"] = ((cohort_summary["Total"] - cohort_summary["Churned"]) / cohort_summary["Total"] * 100).round(1)
        
        # --- Visualization ---
        c1, c2 = st.columns([3, 2])
        
        with c1:
            st.markdown('<div class="nav-label">RETENTION BY TENURE VINTAGE</div>', unsafe_allow_html=True)
            # Standard Line Chart for Retention
            fig_ret = px.line(
                cohort_summary.sort_values("Cohort"), 
                x="Cohort", y="Retention %", 
                markers=True,
                title="Cohort Retention Decay Curve"
            )
            fig_ret.update_traces(line_color='#5B4FE9', marker_color='#5B4FE9')
            fig_ret.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#1E1E1E')
            )
            st.plotly_chart(fig_ret, use_container_width=True)
            
        with c2:
            st.markdown('<div class="nav-label">COHORT VALUE DISTRIBUTION</div>', unsafe_allow_html=True)
            fig_val = px.bar(
                cohort_summary,
                x="Cohort", y="Avg Balance",
                title="Average Capitalization per Vintage"
            )
            fig_val.update_traces(marker_color='#5B4FE9', opacity=0.8)
            fig_val.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="white"
            )
            st.plotly_chart(fig_val, use_container_width=True)

        st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
        
        # Detailed Grid
        st.markdown('<div class="nav-label">QUARTERLY COHORT PERFORMANCE MATRIX</div>', unsafe_allow_html=True)
        st.dataframe(
            cohort_summary.sort_values("Retention %", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Insufficient data for cohort maturation analysis.")

else:
    st.warning("Backend offline. Connect for cohort longitudinal study.")
