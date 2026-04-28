import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Global Layout Configuration
CHART_LAYOUT = {
    "plot_bgcolor": "#0A0A0A",
    "paper_bgcolor": "#0A0A0A",
    "font": {"family": "IBM Plex Mono, monospace", "color": "#888888", "size": 11},
    "xaxis": {"gridcolor": "#1E1E1E", "zeroline": False, "showgrid": False},
    "yaxis": {"gridcolor": "#1E1E1E", "zeroline": False, "showgrid": False},
    "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
}

ACCENT_COLOR = "#5B4FE9"

def churn_trend_chart(df):
    """Line chart for churn trend."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["churn_rate"],
        mode="lines+markers",
        line=dict(color=ACCENT_COLOR, width=2),
        marker=dict(size=4, color=ACCENT_COLOR),
        name="Churn Rate %"
    ))
    fig.update_layout(**CHART_LAYOUT, title={"text": "CHURN TREND %", "font": {"color": "#FFFFFF", "size": 13, "family": "IBM Plex Mono"}})
    return fig

def donut_chart(values, labels, title):
    """Donut chart for segment distribution."""
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=.6,
        marker=dict(colors=[ACCENT_COLOR, "#2A2A2A", "#1E1E1E", "#3A3A3A"]),
        textinfo="none"
    )])
    fig.update_layout(**CHART_LAYOUT, title={"text": title.upper(), "font": {"color": "#FFFFFF", "size": 13, "family": "IBM Plex Mono"}})
    return fig

def segment_scatter(df):
    """PCA/Scatter plot for segments."""
    fig = px.scatter(
        df, x="pca1", y="pca2", color="segment",
        color_discrete_sequence=[ACCENT_COLOR, "#444444", "#666666", "#888888"],
    )
    fig.update_layout(**CHART_LAYOUT, title={"text": "CUSTOMER SEGMENT CLUSTERS", "font": {"color": "#FFFFFF", "size": 13, "family": "IBM Plex Mono"}})
    fig.update_traces(marker=dict(size=6))
    return fig

def shap_bar_chart(importance_dict):
    """SHAP global feature importance bar chart."""
    features = list(importance_dict.keys())
    values = list(importance_dict.values())
    
    fig = go.Figure(go.Bar(
        x=values, y=features,
        orientation="h",
        marker=dict(color=ACCENT_COLOR),
    ))
    
    # Merge global layout with local overrides to avoid multiple value errors
    layout = CHART_LAYOUT.copy()
    layout.update({
        "title": {"text": "GLOBAL FEATURE IMPORTANCE", "font": {"color": "#FFFFFF", "size": 13, "family": "IBM Plex Mono"}},
        "yaxis": {"autorange": "reversed", "showgrid": False},
        "xaxis": {"title": "Mean Absolute SHAP value", "showgrid": False}
    })
    fig.update_layout(layout)
    return fig

def risk_gauge(score):
    """Indicator/Gauge for churn risk score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "CHURN RISK", 'font': {'color': '#FFFFFF', 'size': 13, 'family': 'IBM Plex Mono'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#444", 'tickfont': {'color': '#444'}},
            'bar': {'color': ACCENT_COLOR},
            'bgcolor': "#111",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#111'},
                {'range': [40, 70], 'color': '#111'},
                {'range': [70, 100], 'color': '#111'}
            ],
            'threshold': {
                'line': {'color': "#FF4B4B", 'width': 2},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig.update_layout(**CHART_LAYOUT, height=250)
    return fig
