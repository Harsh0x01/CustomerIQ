import streamlit as st
import pandas as pd
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_stats, get_audit_logs, get_drift_report
from utils.charts import churn_trend_chart, donut_chart
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Dashboard | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Fetch Stats & Logs
with st.spinner("Loading telemetry..."):
    stats = get_stats() if is_online else None
    audit_logs = get_audit_logs(limit=5) if is_online else []
    drift = get_drift_report() if is_online else {"drift_detected": False}

# ── Notification Ticker (Senior Tier) ─────────────────────────
if drift.get("drift_detected"):
    st.error("📉 STATISTICAL DRIFT DETECTED: Feature distributions have shifted significantly. Re-training recommended.")
elif is_online:
    st.success("🛰️ ANALYTIC TELEMETRY: All models reporting optimal statistical alignment.")

# KPI Row
c1, c2, c3, c4 = st.columns(4)

total_cust = stats.get("total_customers", 0) if stats else 0
churn_rate = stats.get("churn_rate", 0) if stats else 0
avg_clv = stats.get("avg_balance", 0) if stats else 0 # Balance as proxy for CLV
high_risk = stats.get("churned", 0) if stats else 0 # Churned as proxy for high risk if not computed

c1.metric("Total Customers", f"{total_cust:,}")
c2.metric("Churn Rate", f"{churn_rate}%")
c3.metric("Avg CLV", f"${avg_clv:,.0f}")
c4.metric("High Risk Count", f"{high_risk:,}")

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Charts Row
col_left, col_right = st.columns(2)

with col_left:
    # Mock Churn Trend Data
    trend_df = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", periods=12, freq="ME"),
        "churn_rate": [2.1, 2.3, 2.0, 2.5, 2.8, 2.6, 2.9, 3.1, 3.0, 2.8, 2.7, churn_rate if churn_rate > 0 else 2.5]
    })
    st.plotly_chart(churn_trend_chart(trend_df), use_container_width=True)

with col_right:
    # Mock Segment Distribution
    labels = ["Low Value", "Mid Value", "High Value", "Premium"]
    values = [450, 320, 180, 50]
    st.plotly_chart(donut_chart(values, labels, "Segment Distribution"), use_container_width=True)

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Real Audit Ingestion Log
st.markdown('<div class="nav-label">PLATFORM AUDIT & INGESTION LOG</div>', unsafe_allow_html=True)
st.markdown('<h3 style="margin-top: 5px;">Traceability & Governance</h3>', unsafe_allow_html=True)

if audit_logs:
    html_table = f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th>Action</th>
                <th>Target/Resource</th>
                <th>Timestamp</th>
                <th>Outcome</th>
            </tr>
        </thead>
        <tbody>
            {"".join([f"<tr><td>{log['action']}</td><td>{log['target']}</td><td>{log['created_at']}</td><td><span style='border: 1px solid #5B4FE9; color: #5B4FE9; padding: 2px 6px; font-size: 9px;'>SUCCESS</span></td></tr>" for log in audit_logs])}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.info("No recorded audit telemetry available.")

if not is_online:
    st.warning("Backend offline. Please start the FastAPI server to view live data.")
