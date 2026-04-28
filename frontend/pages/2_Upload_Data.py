import streamlit as st
import pandas as pd
import io
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import upload_csv, get_customers
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Upload Data | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">DATA INGESTION</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Ingest Customer Data</h2>', unsafe_allow_html=True)

# Required Columns
REQUIRED_COLS = [
    "customer_id", "age", "gender", "tenure", "balance",
    "num_products", "has_credit_card", "is_active_member",
    "estimated_salary", "exited"
]

# File Uploader
uploaded_file = st.file_uploader("DROP CSV HERE OR CLICK TO UPLOAD", type=["csv"], label_visibility="visible")

if uploaded_file:
    # Read and Preview
    try:
        df = pd.read_csv(uploaded_file)
        
        st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-label">PREVIEW - FIRST 10 ROWS</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        
        # Validation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="nav-label">COLUMN SUMMARY</div>', unsafe_allow_html=True)
            summary_df = pd.DataFrame({
                "Column": df.columns,
                "Dtype": [str(d) for d in df.dtypes],
                "Missing Values": df.isnull().sum()
            })
            st.table(summary_df)
            
        with col2:
            st.markdown('<div class="nav-label">COLUMN VALIDATION</div>', unsafe_allow_html=True)
            missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                st.success("All required columns detected.")
                
                # Confirm Upload
                if st.button("CONFIRM UPLOAD"):
                    with st.status("Uploading data to server...", expanded=True) as status:
                        st.write("Checking connection...")
                        if is_online:
                            st.write("Sending request...")
                            result = upload_csv(uploaded_file)
                            if result:
                                status.update(label="Upload Complete!", state="complete", expanded=False)
                                st.success(f"Finalized: Saved {result.get('saved', 0)} new records.")
                            else:
                                status.update(label="Upload Failed", state="error")
                        else:
                            status.update(label="Backend Offline", state="error")
    except Exception as e:
        st.error(f"Fatal Error: {e}")

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Upload History
st.markdown('<div class="nav-label">INGESTION HISTORY</div>', unsafe_allow_html=True)
st.markdown('<h3 style="margin-top: 5px;">Recent Ingestions</h3>', unsafe_allow_html=True)

# Mocked Upload History for UI demonstration
history_data = [
    {"timestamp": "2024-03-24 14:20", "filename": "q4_customers.csv", "rows": 1204},
    {"timestamp": "2024-03-22 09:15", "filename": "training_v2.csv", "rows": 5000},
    {"timestamp": "2024-03-20 18:45", "filename": "leads_raw.csv", "rows": 840},
]

# Render History with Delete Buttons
for item in history_data:
    cols = st.columns([2, 3, 1, 1])
    cols[0].markdown(f"**{item['timestamp']}**")
    cols[1].text(item['filename'])
    cols[2].text(f"{item['rows']} rows")
    if cols[3].button("DELETE", key=f"del_{item['timestamp']}"):
        st.warning(f"Delete requested for {item['filename']}")

if not is_online:
    st.warning("Backend offline. Connection required for active data ingestion.")
