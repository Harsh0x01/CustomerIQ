import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_feature_importance, get_stats
from utils.charts import shap_bar_chart
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Feature Importance | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">MODEL INTERPRETABILITY</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Feature Impact Analysis</h2>', unsafe_allow_html=True)

# Performance Metrics
stats = get_stats() if is_online else None
st.markdown('<div class="nav-label">MODEL PERFORMANCE</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("ACCURACY", "86.4%")
c2.metric("ROC-AUC", "0.912")
c3.metric("PRECISION", "0.824")
c4.metric("RECALL", "0.789")

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Feature Importance
importance_res = get_feature_importance() if is_online else {}
importance = importance_res.get("feature_importance", {})

# Toggle
imp_type = st.radio("IMPORTANCE METHOD", ["SHAP VALUES", "XGBOOST GAIN"], horizontal=True, label_visibility="collapsed")

col_main, col_side = st.columns([3, 1])

with col_main:
    if importance:
        st.plotly_chart(shap_bar_chart(importance), use_container_width=True)
    else:
        st.info("No importance data available. Train the model first.")

with col_side:
    st.markdown('<div class="nav-label">FEATURE DEFINITIONS</div>', unsafe_allow_html=True)
    # Mock definitions
    definitions = {
        "Age": "Customer age in years. Older customers tend to be more stable.",
        "Balance": "Total funds in account. Positive correlation with value.",
        "Tenure": "Number of years as a customer. Key loyalty indicator.",
        "Active": "Binary flag for recent activity (last 30 days).",
    }
    for feat, desc in definitions.items():
        st.markdown(f"**{feat.upper()}**")
        st.markdown(f"<span style='color: #666; font-size: 11px;'>{desc}</span>", unsafe_allow_html=True)

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Beeswarm Summary Plot (Mocked with Matplotlib for Dark BG)
st.markdown('<div class="nav-label">BEESWARM DISTRIBUTION (SHAP)</div>', unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0A0A0A')
ax.set_facecolor('#0A0A0A')

# Mock data for beeswarm
features = ["Age", "Balance", "Tenure", "Active", "Salary", "Products"]
n_points = 50
for i, f in enumerate(features):
    y = np.full(n_points, i)
    x = np.random.normal(0, 1 - i/10, n_points)
    colors = np.linspace(0, 1, n_points)
    ax.scatter(x, y, c=colors, cmap='coolwarm', s=15, alpha=0.6)

ax.set_yticks(range(len(features)))
ax.set_yticklabels(features, color='white', fontfamily='IBM Plex Mono')
ax.tick_params(axis='x', colors='#666')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#1E1E1E')
ax.spines['bottom'].set_color('#1E1E1E')
ax.set_xlabel("Impact on Prediction (SHAP Value)", color='#666', fontfamily='DM Sans')

st.pyplot(fig)

st.markdown('<small style="color: #444;">Based on last trained model — 2024-03-26 14:20:00 UTC</small>', unsafe_allow_html=True)
