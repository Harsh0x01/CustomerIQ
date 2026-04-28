import streamlit as st
import pandas as pd
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import predict_single, predict_batch, get_model_status
from utils.charts import risk_gauge, shap_bar_chart
from utils.auth import render_login_screen

# Page Config
st.set_page_config(page_title="Churn Prediction | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">FORK ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Churn Probability Modeling</h2>', unsafe_allow_html=True)

# Model Status
is_trained = get_model_status() if is_online else False
if not is_trained and is_online:
    st.warning("Model not trained. Please upload training data and train the model first.")
elif not is_online:
    st.warning("⚠️ Backend is offline. Predictions require a running FastAPI server on port 8000.")

# Tab Switcher (Custom)
if "mode" not in st.session_state:
    st.session_state.mode = "SINGLE"

c1, c2, _ = st.columns([1, 1, 4])
if c1.button("SINGLE PREDICT", use_container_width=True, type="primary" if st.session_state.mode == "SINGLE" else "secondary"):
    st.session_state.mode = "SINGLE"
if c2.button("BATCH PREDICT", use_container_width=True, type="primary" if st.session_state.mode == "BATCH" else "secondary"):
    st.session_state.mode = "BATCH"

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

if st.session_state.mode == "SINGLE":
    # Single Prediction Mode
    col_input, col_output = st.columns([3, 2])
    
    with col_input:
        st.markdown('<div class="nav-label">CUSTOMER PARAMETERS</div>', unsafe_allow_html=True)
        with st.form("single_predict_form"):
            c_id = st.text_input("Customer ID", "CUST0001")
            ca1, ca2 = st.columns(2)
            age = ca1.number_input("Age", 18, 100, 42)
            gender = ca2.selectbox("Gender", ["Male", "Female", "Other"])
            
            cb1, cb2 = st.columns(2)
            tenure = cb1.number_input("Tenure (Years)", 0, 20, 5)
            balance = cb2.number_input("Balance", 0.0, 500000.0, 125000.0)
            
            cc1, cc2 = st.columns(2)
            num_products = cc1.selectbox("Num Products", [1, 2, 3, 4])
            salary = cc2.number_input("Estimated Salary", 0.0, 500000.0, 85000.0)
            
            cd1, cd2 = st.columns(2)
            has_cc = cd1.checkbox("Has Credit Card", True)
            is_active = cd2.checkbox("Is Active Member", True)
            
            submit = st.form_submit_button("RUN PREDICTION")
            
        if submit:
            if not is_online:
                st.error("❌ Cannot predict: Backend server is offline.")
            elif not is_trained:
                st.error("❌ Cannot predict: Model is not trained yet.")
            else:
                payload = {
                    "customer_id": c_id, "age": age, "gender": gender,
                    "tenure": tenure, "balance": balance, "num_products": num_products,
                    "has_credit_card": 1 if has_cc else 0, "is_active_member": 1 if is_active else 0,
                    "estimated_salary": salary
                }
                with st.spinner("Running prediction engine..."):
                    res = predict_single(payload)
                
                if res and "_error" in res:
                    st.error(f"❌ Prediction failed: {res['_error']}")
                elif res and "churn_probability" in res:
                    st.session_state.last_res = res
                    st.rerun()
                else:
                    st.error("❌ Prediction returned an unexpected response. Check backend logs.")
    
    with col_output:
        st.markdown('<div class="nav-label">PREDICTION ENGINE OUTPUT</div>', unsafe_allow_html=True)
        if "last_res" in st.session_state:
            res = st.session_state.last_res
            prob = res.get("churn_probability", 0)
            risk = res.get("risk_level", "Unknown")
            
            # Gauge
            st.plotly_chart(risk_gauge(prob), use_container_width=True)
            
            # Risk Bar
            risk_color = "#FF4B4B" if risk == "High" else "#FFAA00" if risk == "Medium" else "#00FF00"
            st.markdown(f"""
            <div style="background-color: #111; border: 1px solid #1E1E1E; padding: 20px;">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #888; text-transform: uppercase;">Final Score</div>
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 32px; color: {risk_color};">{prob*100:.1f}%</div>
                <div style="font-family: 'DM Sans', sans-serif; font-size: 14px; margin-top: 5px;">Risk Level: <span style="font-weight: 700;">{risk}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mock SHAP (Since single predict normally returns this in advanced setups)
            st.markdown('<div style="margin-top: 2rem;" class="nav-label">SHAP FACTORS</div>', unsafe_allow_html=True)
            st.plotly_chart(shap_bar_chart({"Age": 0.45, "Is Active": -0.32, "Balance": 0.15, "Tenure": -0.08}), use_container_width=True)
        else:
            st.info("Form submitted output will appear here.")

else:
    # Batch Prediction Mode
    st.markdown('<div class="nav-label">BATCH PROCESSING</div>', unsafe_allow_html=True)
    batch_file = st.file_uploader("DROP BATCH CSV HERE", type=["csv"])
    
    if batch_file:
        if not is_online:
            st.error("❌ Backend is offline. Start the FastAPI server first.")
        elif not is_trained:
            st.error("❌ Model is not trained. Upload data and train the model first.")
        elif st.button("RUN BATCH PREDICTION"):
            with st.spinner("Processing large dataset..."):
                results = predict_batch(batch_file)
            
            if results and "_error" in results:
                st.error(f"❌ Batch prediction failed: {results['_error']}")
            elif results and isinstance(results, list):
                res_df = pd.DataFrame(results)
                
                # Distribution Summary
                st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="nav-label">BATCH RESULTS OVERVIEW</div>', unsafe_allow_html=True)
                
                # Risk Color Mapping
                def color_cells(val):
                    if isinstance(val, (int, float)):
                        if val > 0.7: return "background-color: rgba(255, 75, 75, 0.1); color: #FF4B4B;"
                        if val > 0.4: return "background-color: rgba(255, 170, 0, 0.1); color: #FFAA00;"
                        return "background-color: rgba(0, 255, 0, 0.1); color: #00FF00;"
                    return ""
                
                st.dataframe(res_df.style.map(color_cells, subset=["churn_probability"]), use_container_width=True)
                
                # Export
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="EXPORT FINAL BATCH REPORT",
                    data=csv,
                    file_name="churn_batch_results.csv",
                    mime="text/csv",
                )
            else:
                st.error("❌ Batch prediction returned an unexpected response.")
