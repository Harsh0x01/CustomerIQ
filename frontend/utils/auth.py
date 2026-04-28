import requests
import streamlit as st
import os
from dotenv import load_dotenv

# Explicitly load from root to ensure Streamlit finds it
root_path = os.path.join(os.path.dirname(__file__), "..", "..")
load_dotenv(os.path.join(root_path, ".env"))

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def supabase_login(email, password):
    """Logs in a user via Supabase GoTrue API."""
    email = email.strip()
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        # Debugging
        print(f"DEBUG LOGIN: URL={url}")
        print(f"DEBUG LOGIN: EMAIL='{email}'")
        print(f"DEBUG LOGIN: PASS_LEN={len(password)}")
        print(f"DEBUG LOGIN: KEY_PREFIX={SUPABASE_ANON_KEY[:10]}...")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"DEBUG LOGIN: STATUS={response.status_code}")
        print(f"DEBUG LOGIN: ERROR={response.json().get('error', 'none')}")
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = data["user"]
            st.session_state.token = data["access_token"]
            return True, "Login successful"
        else:
            error = response.json().get("error_description", "Invalid login credentials")
            return False, error
    except Exception as e:
        print(f"DEBUG LOGIN ERROR: {str(e)}")
        return False, str(e)

def supabase_signup(email, password):
    """Signs up a new user via Supabase GoTrue API."""
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True, "Signup successful. Please check your email for confirmation."
        else:
            error = response.json().get("msg", "Signup failed")
            return False, error
    except Exception as e:
        return False, str(e)

def sign_out():
    """Clears the authentication state."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.rerun()

def render_login_screen():
    """Renders a professional, terminal-style login/signup interface."""
    st.markdown('<div class="nav-label">CUSTOMERIQ ACCESS CONTROL</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top: 0; margin-bottom: 2rem;">System Authentication</h2>', unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["EXISTING USER", "NEW REGISTRATION"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Corporate Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("INITIALIZE SESSION")
            
            if submitted:
                if not email or not password:
                    st.error("Credentials required.")
                else:
                    success, msg = supabase_login(email, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                        
    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Work Email")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("CREATE ACCOUNT")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Security requirement: Minimum 6 characters.")
                else:
                    success, msg = supabase_signup(new_email, new_password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
