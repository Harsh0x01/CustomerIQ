import streamlit as st

def apply_global_style(render: bool = True):
    """Injects custom CSS for a Bloomberg-meets-Linear aesthetic."""
    css = """
    <style>
    /* Global Base - Force Black Background Immediately */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0A0A0A !important;
        color: #CCCCCC !important;
        font-family: 'DM Sans', sans-serif;
    }

    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    /* CSS logic remains unchanged ... */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
    }

    /* Hide Default Header/Footer */
    header[data-testid="stHeader"], [data-testid="stFooter"] {
        display: none !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0D0D0D !important;
        border-right: 1px solid #1E1E1E !important;
    }
    
    /* Navigation Items */
    [data-testid="stSidebarNav"] ul {
        padding-top: 2rem;
    }
    [data-testid="stSidebarNav"] ul li a {
        background-color: transparent !important;
        color: #666666 !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        letter-spacing: 0.15em !important;
        font-family: 'IBM Plex Mono', monospace !important;
        padding: 10px 20px !important;
        transition: color 0.2s ease;
    }
    [data-testid="stSidebarNav"] ul li a:hover {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebarNav"] ul li a[data-active="true"] {
        color: #5B4FE9 !important;
        border-left: 2px solid #5B4FE9;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        border: 1px solid #1E1E1E !important;
        padding: 24px !important;
        border-radius: 0px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 32px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'DM Sans', sans-serif !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        letter-spacing: 0.1em !important;
        color: #888888 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #5B4FE9 !important;
        color: white !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 0.5rem 1.5rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        transition: opacity 0.2s ease;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
    }

    /* Text Inputs / Selectboxes */
    div[data-baseweb="input"], div[data-baseweb="select"], .stFileUploader {
        background-color: #0A0A0A !important;
        border: 1px solid #1E1E1E !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #5B4FE9 !important;
    }

    /* Tables (Dataframe) */
    [data-testid="stDataFrame"] {
        font-family: 'IBM Plex Mono', monospace !important;
        border: 1px solid #1E1E1E !important;
    }

    /* Alerts */
    .stAlert {
        background-color: transparent !important;
        border-radius: 0 !important;
        border: none !important;
        border-left: 4px solid #1E1E1E !important;
        padding: 1rem !important;
    }
    .stAlert[data-baseweb="notification"] {
        border-left-color: #5B4FE9 !important;
    }
    div[data-testid="stNotificationContentSuccess"] { color: #FFFFFF !important; border-left: 4px solid #5B4FE9 !important; }
    div[data-testid="stNotificationContentError"] { color: #FFFFFF !important; border-left: 4px solid #FF4B4B !important; }
    div[data-testid="stNotificationContentWarning"] { color: #FFFFFF !important; border-left: 4px solid #FFAA00 !important; }

    /* Custom Tables */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: #CCCCCC;
    }
    .custom-table th {
        text-align: left;
        padding: 12px;
        border-bottom: 1px solid #1E1E1E;
        color: #888888;
        text-transform: uppercase;
        font-size: 10px;
        letter-spacing: 0.1em;
    }
    .custom-table td {
        padding: 12px;
        border-bottom: 1px solid #1E1E1E;
    }
    .custom-table tr:nth-child(even) { background-color: #0F0F0F; }
    .custom-table tr:nth-child(odd) { background-color: #141414; }

    /* Status Dot */
    .status-dot {
        height: 6px;
        width: 6px;
        background-color: #00FF00;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }

    /* Divider */
    .thin-divider {
        height: 1px;
        background-color: #1E1E1E;
        margin: 1rem 0;
    }

    /* Navigation Label */
    .nav-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        letter-spacing: 0.15em;
        color: #5B4FE9;
        font-weight: 500;
        margin-bottom: 5px;
    }
    </style>
    """
    if render:
        st.markdown(css, unsafe_allow_html=True)
    return css
