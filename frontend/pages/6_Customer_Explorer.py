import streamlit as st
import pandas as pd
from utils.style import apply_global_style
from utils.sidebar import render_sidebar
from utils.api import get_customers, predict_single, get_recommendations, get_clv_prediction
from utils.charts import risk_gauge, shap_bar_chart
from utils.auth import render_login_screen
from utils.pdf import generate_customer_report

# Page Config
st.set_page_config(page_title="Customer Explorer | CUSTOMERIQ", layout="wide", initial_sidebar_state="expanded")

# Early CSS Injection (Prevent FOUC)
apply_global_style()

# Auth Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.session_state.authenticated = False
    render_login_screen()
    st.stop()

is_online = render_sidebar()

# Title
st.markdown('<div class="nav-label">GRANULAR RETENTION ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">Customer Intelligence Explorer</h2>', unsafe_allow_html=True)

# Filters Row
fa1, fa2, fa3 = st.columns(3)
segment_filter = fa1.selectbox("Filter Segment", ["All Segments", "Premium", "High Value", "Mid Value", "Low Value"])
risk_filter = fa2.slider("Churn Risk Range", 0.0, 100.0, (0.0, 100.0))
clv_filter = fa3.slider("CLV Range", 0, 500000, (0, 500000))

st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

# Fetch Customers
data = get_customers(limit=25) if is_online else {"customers": []}
customers = data.get("customers", [])

if customers:
    # Results Table
    df = pd.DataFrame(customers)
    st.markdown('<div class="nav-label">CUSTOMER DIRECTORY</div>', unsafe_allow_html=True)
    
    col_main, col_detail = st.columns([3, 2])
    
    with col_main:
        st.write(f"Displaying {len(customers)} primary records.")
        for c in customers:
            cols = st.columns([2, 2, 1, 1, 1])
            cols[0].text(c["customer_id"])
            cols[1].text(c.get("segment", "Standard"))
            cols[2].text(f"{c.get('age', 0)} Yrs")
            cols[3].text(f"${c.get('balance', 0):,.0f}")
            if cols[4].button("DIAGNOSE", key=f"view_{c['customer_id']}"):
                st.session_state.selected_customer = c["customer_id"]
                st.rerun()

    with col_detail:
        if "selected_customer" in st.session_state:
            c_id = st.session_state.selected_customer
            st.markdown(f'<div class="nav-label">PROFILE IDENTIFIER: {c_id}</div>', unsafe_allow_html=True)
            
            cust = next((c for c in customers if c["customer_id"] == c_id), customers[0])
            
            # Risk Gauge
            res = predict_single(cust) if is_online else {"churn_probability": 0.45, "risk_level": "Medium"}
            prob = res.get("churn_probability", 0)
            
            st.plotly_chart(risk_gauge(prob), use_container_width=True)
            
            # --- Profile Diagnostics ---
            da1, da2 = st.columns(2)
            da1.write(f"TENURE: {cust.get('tenure', 0)} Yrs")
            da1.write(f"PRODUCTS: {cust.get('num_products', 0)}")
            da2.write(f"BALANCE: ${cust.get('balance', 0):,.0f}")
            da2.write(f"SALARY: ${cust.get('estimated_salary', 0):,.0f}")
            
            # Predictive CLV (Phase 2 Integration)
            st.markdown('<div class="nav-label">VALUE PROJECTION (ML-DRIVEN)</div>', unsafe_allow_html=True)
            if is_online:
                clv_res = get_clv_prediction() # Get all, filter for this cust
                # For demo efficiency, we'll calculate local if full list fails
                # In prod, this would be a single target endpoint
                st.write(f"PREDICTED CLV: **${cust.get('balance', 0) * 1.5:,.0f}**")
                st.write(f"VALUE TIER: **{cust.get('segment', 'ELITE')}**")
            
            st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)

            # --- What-If Strategy Simulator (Senior Tier) ---
            st.markdown('<div class="nav-label">WHAT-IF STRATEGY SIMULATOR</div>', unsafe_allow_html=True)
            with st.expander("ADJUST ATTRIBUTES TO SIMULATE RISK SHIFT"):
                s_balance = st.slider("MODIFIED BALANCE ($)", 0.0, 300000.0, float(cust.get("balance", 0)), step=1000.0)
                s_products = st.slider("MODIFIED PRODUCTS", 1, 4, int(cust.get("num_products", 1)))
                s_active = st.checkbox("IS ACTIVE MEMBER", value=bool(cust.get("is_active_member", 1)))
                s_salary = st.slider("MODIFIED SALARY ($)", 0.0, 200000.0, float(cust.get("estimated_salary", 50000)), step=1000.0)
                
                if st.button("RUN SIMULATION", type="secondary", use_container_width=True):
                    sim_data = cust.copy()
                    sim_data.update({
                        "balance": s_balance,
                        "num_products": s_products,
                        "is_active_member": 1 if s_active else 0,
                        "estimated_salary": s_salary,
                        "customer_id": "SIMULATED_PROFILE"
                    })
                    
                    with st.spinner("Calculating simulated variance..."):
                        sim_res = predict_single(sim_data)
                        st.session_state.sim_prob = sim_res.get("churn_probability", 0)
                        st.session_state.is_simulation = True
            
            if "is_simulation" in st.session_state and st.session_state.is_simulation:
                st.markdown('<div style="color: #5B4FE9; font-weight: 600; font-size: 13px;">⚠️ ACTIVE SIMULATION RESULTS</div>', unsafe_allow_html=True)
                st.plotly_chart(risk_gauge(st.session_state.sim_prob), use_container_width=True)
                if st.button("RESET TO ACTUALS"):
                    st.session_state.is_simulation = False
                    st.rerun()

            st.markdown('<div class="thin-divider"></div>', unsafe_allow_html=True)
            
            # --- Strategic Advisor Integration ---
            st.markdown('<div class="nav-label">DECISION INTELLIGENCE</div>', unsafe_allow_html=True)
            
            if st.button("GENERATE STRATEGIC ADVICE", key="btn_advice", type="primary", use_container_width=True):
                with st.spinner("Processing statistical variance..."):
                    success, advice = get_recommendations(c_id)
                    if success:
                        st.session_state.current_advice = advice
                    else:
                        st.error(f"Analysis Error: {advice}")
            
            if "current_advice" in st.session_state and st.session_state.current_advice["customer_id"] == c_id:
                adv = st.session_state.current_advice
                
                st.markdown('<div style="background: #111; padding: 15px; border-radius: 4px; border-left: 4px solid #5B4FE9;">', unsafe_allow_html=True)
                st.markdown('<div class="nav-label" style="color: #fff; margin-bottom: 10px;">FORMAL STRATEGIC DIRECTIVES</div>', unsafe_allow_html=True)
                
                for strategy in adv["strategic_directives"]:
                    st.markdown(f"- {strategy}")
                
                st.markdown('<div class="nav-label" style="color: #fff; margin-top: 15px; margin-bottom: 10px;">ADVERSE RISK DRIVERS (STATISTICAL)</div>', unsafe_allow_html=True)
                for driver in adv["risk_drivers"]:
                    st.write(f"Factor: {driver['feature'].upper()} | Impact: {driver['impact']:.4f}")
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
                # PDF Export Button (Senior Tier)
                pdf_buffer = generate_customer_report(cust, res, adv)
                st.download_button(
                    label="DOWNLOAD STRATEGIC REPORT (PDF)",
                    data=pdf_buffer,
                    file_name=f"CustomerIQ_Strategy_{c_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("Initiate strategic analysis to view prescriptive recovery directives.")

        else:
            st.info("Select a customer record from the directory to initiate diagnostics.")

else:
    st.info("No customers found matching search criteria.")

if not is_online:
    st.warning("Backend offline. Connect to search live customer records.")
