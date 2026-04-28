import streamlit as st
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_stats
from utils.charts import churn_trend_chart, donut_chart
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="CustomerIQ | AI Intelligence Platform", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None

# Authentication Router
if not st.session_state.get("authenticated", False):
    render_login_screen()
    st.stop()

# Connection Status & Sidebar
is_online = render_sidebar()

if not is_online:
    st.error("📡 Cannot establish secure link to backend (Port 8000). Some features may be restricted.")
    st.info("💡 Ensure the FastAPI backend is running with `.\\start_backend.ps1` or `uvicorn`.")

# Hero Section
st.markdown('<div class="nav-label">CUSTOMERIQ V1.0.0</div>', unsafe_allow_html=True)
st.markdown('<h1 style="font-size: 3.5rem; line-height: 1.1; margin-top: 10px;">Artificial Intelligence for<br><span style="color: #5B4FE9;">Customer Intelligence</span></h1>', unsafe_allow_html=True)

st.markdown("""
<div style="font-family: 'DM Sans', sans-serif; font-size: 1.1rem; color: #666; max-width: 600px; margin-top: 1.5rem;">
Predict churn with XGBoost & SHAP. Segment your user base with KMeans.
Analyze granular customer profiles with professional precision.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Features Grid
st.markdown('<div class="nav-label">CORE ARCHITECTURE</div>', unsafe_allow_html=True)
st.markdown('<h3 style="margin-top: 5px;">Analytical Modules</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="border: 1px solid #1E1E1E; padding: 24px;">
        <div style="color: #5B4FE9; font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin-bottom: 10px;">MODULE-01</div>
        <div style="font-weight: 500; font-size: 18px; margin-bottom: 10px; color: #FFF;">CHURN PREDICTION</div>
        <div style="color: #444; font-size: 13px;">XGBoost models with probabilistic outputs and risk tiering based on behavior.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="border: 1px solid #1E1E1E; padding: 24px;">
        <div style="color: #5B4FE9; font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin-bottom: 10px;">MODULE-02</div>
        <div style="font-weight: 500; font-size: 18px; margin-bottom: 10px; color: #FFF;">BEHAVIORAL SEGMENTS</div>
        <div style="color: #444; font-size: 13px;">Unsupervised KMeans clustering to identify high-value vs high-risk cohorts automatically.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="border: 1px solid #1E1E1E; padding: 24px;">
        <div style="color: #5B4FE9; font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin-bottom: 10px;">MODULE-03</div>
        <div style="font-weight: 500; font-size: 18px; margin-bottom: 10px; color: #FFF;">SHAP EXPLAINABILITY</div>
        <div style="color: #444; font-size: 13px;">Transparent AI: understand every model decision with feature impact scores.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Onboarding Section
left, right = st.columns([3, 2])

with left:
    st.markdown('<div class="nav-label">QUICKSTART PROTOCOL</div>', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top: 5px;">Initialization Sequence</h3>', unsafe_allow_html=True)
    
    steps = [
        ("01", "INGESTION", "Upload your raw customer CSV in the Upload Data module."),
        ("02", "CALIBRATION", "Train the XGBoost engine via the Prediction dashboard."),
        ("03", "ANALYSIS", "Explore segments and global feature importance metrics."),
        ("04", "RETENTION", "Use Customer Explorer to identify high-risk individuals.")
    ]
    
    for num, title, desc in steps:
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span style="font-family: 'IBM Plex Mono', monospace; color: #5B4FE9; font-size: 13px; margin-right: 15px;">{num}</span>
            <span style="font-weight: 500; color: #FFF; font-size: 15px;">{title}</span>
            <div style="margin-left: 35px; color: #444; font-size: 13px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="nav-label">SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top: 5px;">Architecture Status</h3>', unsafe_allow_html=True)
    
    status_color = "#00FF00" if is_online else "#FF4B4B"
    st.markdown(f"""
    <div style="border: 1px solid #1E1E1E; padding: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <span style="color: #666; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">BACKEND STATUS</span>
            <span style="color: {status_color}; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">{"ONLINE" if is_online else "OFFLINE"}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <span style="color: #666; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">MODEL STATUS</span>
            <span style="color: #444; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">ACTIVE</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="color: #666; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">API VERSION</span>
            <span style="color: #444; font-size: 11px; font-family: 'IBM Plex Mono', monospace;">V1.0.0-PRO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="margin-top: 4rem; text-align: center; color: #222; font-family: \'IBM Plex Mono\', monospace; font-size: 9px;">PRIVATE ENTERPRISE INSTANCE &nbsp;|&nbsp; UNAUTHORIZED ACCESS PROHIBITED</div>', unsafe_allow_html=True)
