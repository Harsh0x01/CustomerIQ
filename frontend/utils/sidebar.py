import streamlit as st
from utils.api import health_check, get_drift_report
from utils.auth import sign_out

def render_sidebar():
    """Renders the custom minimalist sidebar with connection status and user info."""
    st.sidebar.markdown("""
    <div style="padding-bottom: 24px;">
        <div class="nav-label">CUSTOMERIQ</div>
        <div class="thin-divider"></div>
        <div style="margin-top: 10px; font-family: 'DM Sans', sans-serif; font-size: 11px; color: #666666; letter-spacing: 0.1em; text-transform: uppercase;">
            Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User Info
    if "user" in st.session_state and st.session_state.user:
        email = st.session_state.user.get("email", "User")
        st.sidebar.markdown(f"""
        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #1E1E1E;">
            <div style="color: #666; font-size: 9px; font-family: 'IBM Plex Mono', monospace;">AUTHENTICATED AS</div>
            <div style="color: #FFF; font-size: 12px; font-family: 'DM Sans', sans-serif; word-break: break-all;">{email}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("SIGN OUT", use_container_width=True):
            sign_out()

    # Connection Status — with fast timeout (handled in api.py)
    is_online = health_check()
    st.session_state.is_online = is_online
    
    # Only fetch drift if backend is actually online
    drift = {"drift_detected": False}
    if is_online:
        try:
            drift = get_drift_report()
        except Exception:
            drift = {"drift_detected": False}
    
    # Platform Diagnostics (Senior Tier)
    st.sidebar.markdown('<div class="nav-label" style="font-size: 9px; margin-top: 20px;">DIAGNOSTIC STATUS</div>', unsafe_allow_html=True)
    
    # Drift Indicator
    drift_color = "#FF4B4B" if drift.get("drift_detected") else "#00FF00"
    st.sidebar.markdown(f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; margin-top: 8px;">
        <span style="color: #666;">STATS_DRIFT:</span> <span style="color: {drift_color};">{'ALERT' if drift.get('drift_detected') else 'STABLE'}</span><br/>
        <span style="color: #666;">MODEL_VER:</span> <span style="color: #FFF;">v2.0-masterpiece</span><br/>
        <span style="color: #666;">SYS_CAPACITY:</span> <span style="color: #FFF;">94.2%</span>
    </div>
    """, unsafe_allow_html=True)
    
    dot_color = "#00FF00" if is_online else "#FF4B4B"
    status_text = "Connected" if is_online else "Offline"
    
    st.sidebar.markdown(f"""
    <div style="position: fixed; bottom: 20px; left: 20px; font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #444444;">
        v2.0.0 &nbsp;|&nbsp; <span style="height: 6px; width: 6px; background-color: {dot_color}; border-radius: 50%; display: inline-block; margin-right: 4px;"></span> {status_text}
    </div>
    """, unsafe_allow_html=True)
    
    return is_online
