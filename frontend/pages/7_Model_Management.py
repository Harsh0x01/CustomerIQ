import streamlit as st
import pandas as pd
import datetime
from utils.api import get_model_runs, train_model, activate_model_run, get_model_status
from utils.sidebar import render_sidebar
from utils.style import apply_global_style
from utils.auth import render_login_screen

# Page Config
st.set_page_config(
    page_title="Model Management | CustomerIQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

st.title("🤖 Model Lifecycle Management")
st.markdown("---")

# ── Training Controls ─────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Training Center")
    st.info("Train a new XGBoost model on the latest customer data.")
    
    if st.button("🚀 Start Training Run", use_container_width=True):
        with st.spinner("Training XGBoost model and logging to MLflow..."):
            success, result = train_model()
            if success:
                st.success("Training Complete!")
                st.json(result.get("metrics", {}))
                st.rerun()
            else:
                st.error(f"Training failed: {result}")

with col2:
    st.subheader("Current Status")
    status = get_model_status()
    if status:
        st.success("✅ Active Model: Operational")
    else:
        st.warning("⚠️ No Active Model: Training Required")
    
    st.markdown("""
    **Model Type:** XGBoost Classifier  
    **Framework:** MLflow Tracking (v1.0)  
    **Target:** Binary Churn Prediction  
    """)

st.markdown("---")

# ── MLflow Run History ────────────────────────────────────────
st.subheader("📊 Model Version History")
runs = get_model_runs()

if not runs:
    st.info("No training runs found. Start your first training run to see metrics.")
else:
    # Prepare data for display
    display_data = []
    for run in runs:
        # Extract metrics (keys starting with 'metrics.')
        acc = run.get("metrics.accuracy", 0)
        auc = run.get("metrics.roc_auc", 0)
        start_time = run.get("start_time")
        
        # Convert start_time if it's a timestamp
        if isinstance(start_time, (int, float)):
            start_time = datetime.datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        display_data.append({
            "Run ID": run.get("run_id")[:8],
            "Full ID": run.get("run_id"),
            "Timestamp": start_time,
            "Status": run.get("status"),
            "Accuracy": f"{acc:.4%}",
            "ROC-AUC": f"{auc:.4%}",
        })
    
    df_runs = pd.DataFrame(display_data)
    
    # Render table with action buttons
    for idx, row in df_runs.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
            c1.write(f"`{row['Run ID']}`")
            c2.write(row['Timestamp'])
            c3.write(f"**Acc:** {row['Accuracy']}")
            c4.write(f"**AUC:** {row['ROC-AUC']}")
            
            if c5.button("Activate", key=f"act_{row['Full ID']}"):
                with st.spinner("Rolling back model..."):
                    success, msg = activate_model_run(row['Full ID'])
                    if success:
                        st.toast(f"Switched to version {row['Run ID']}!", icon="✅")
                        st.rerun()
                    else:
                        st.error(msg)
            st.markdown("<hr style='margin: 0.5em 0; border-color: #222;'>", unsafe_allow_html=True)

# ── Metrics Comparison ────────────────────────────────────────
if len(runs) > 1:
    st.markdown("---")
    st.subheader("📈 Performance Benchmarking")
    
    plot_df = pd.DataFrame([
        {
            "Run": r.get("run_id")[:8],
            "Accuracy": r.get("metrics.accuracy", 0),
            "ROC-AUC": r.get("metrics.roc_auc", 0)
        } for r in reversed(runs[:10])  # Last 10 runs
    ])
    
    st.line_chart(plot_df.set_index("Run"))
