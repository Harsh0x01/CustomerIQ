import streamlit as st
import pandas as pd
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_segments
from utils.charts import segment_scatter, donut_chart
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Customer Segments | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">COHORT CLASSIFICATION</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Behavioral Segmentation</h2>', unsafe_allow_html=True)

# Run Segmentation Settings
with st.expander("SEGMENTATION CONFIGURATION", expanded=False):
    n_clusters = st.slider("Number of Clusters", 2, 6, 4)
    run_btn = st.button("RECOMPUTE SEGMENTS")

# Fetch Segments
if "segments_data" not in st.session_state:
    st.session_state.segments_data = None

if (run_btn or st.session_state.segments_data is None) and is_online:
    with st.spinner("Clustering customer base..."):
        st.session_state.segments_data = get_segments(n_clusters)

if st.session_state.segments_data:
    data = st.session_state.segments_data
    summary = data.get("summary", [])
    segments_list = data.get("segments", [])
    
    col_chart, col_dist = st.columns([3, 2])
    
    with col_chart:
        # Scatter Plot - PCA (Mock PCA coords if not provided)
        df_seg = pd.DataFrame(segments_list)
        if "pca1" not in df_seg.columns:
            # Mock coords for scatter if PCA not in backend
            import numpy as np
            df_seg["pca1"] = np.random.randn(len(df_seg))
            df_seg["pca2"] = np.random.randn(len(df_seg))
        
        st.plotly_chart(segment_scatter(df_seg), use_container_width=True)
    
    with col_dist:
        # Distribution Donut
        labels = [s["segment"] for s in summary]
        values = [s["count"] for s in summary]
        st.plotly_chart(donut_chart(values, labels, "Cluster Distribution"), use_container_width=True)
        
    st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
    
    # Segment Summary Table with Expandables
    st.markdown('<div class="nav-label">SEGMENT PROFILES</div>', unsafe_allow_html=True)
    
    for seg in summary:
        seg_id = seg["segment"]
        count = seg["count"]
        # Use st.expander for expanded segment details
        with st.expander(f"{seg_id.upper()} — {count:,} CUSTOMERS", expanded=False):
            # Inline edit placeholder
            st.text_input(f"RENAME {seg_id.upper()}", f"Segment {seg_id}", key=f"rename_{seg_id}")
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("AVG CHURN RISK", f"{seg.get('avg_churn', 0)*100:.1f}%")
            sc2.metric("AVG CLV", f"${seg.get('avg_balance', 0):,.0f}")
            sc3.metric("TOP FEATURE", seg.get("top_feature", "Tenure"))
            
            # Feature Intensity Bar Chart (Mock)
            features = ["Age", "Balance", "Tenure", "Active", "Credit Score"]
            intensities = [0.8, 0.4, 0.6, 0.2, 0.5] if seg_id == 0 else [0.2, 0.9, 0.1, 0.7, 0.4]
            # (In a real app, this would be computed by the backend as 'cluster centroids')
            st.bar_chart(pd.DataFrame({"Feature": features, "Intensity": intensities}).set_index("Feature"))

else:
    st.info("Trigger segmentation using the configuration menu to visualize cohorts.")

if not is_online:
    st.warning("Backend offline. Connect for live clustering.")
