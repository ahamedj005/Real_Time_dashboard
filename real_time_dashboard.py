import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Enterprise Live Revenue Pulse",
    layout="wide",
    page_icon="📊"
)

# -------------------------------------------------
# POWER BI PROFESSIONAL THEME CSS
# -------------------------------------------------
st.markdown("""
<style>
/* ─── Google Font ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

/* ─── Root Variables ──────────────────────────── */
:root {
    --bg-primary:    #0e1525;
    --bg-secondary:  #141d30;
    --bg-card:       #1a2540;
    --bg-card-hover: #1e2d4d;
    --border:        rgba(255,255,255,0.07);
    --text-primary:  #e8edf5;
    --text-muted:    #8a96b0;
    --accent-blue:   #4f8ef7;
    --accent-green:  #00d4aa;
    --accent-orange: #ff8c42;
    --accent-purple: #a78bfa;
    --gradient-rev:  linear-gradient(135deg, #1a3a6b 0%, #0f2444 60%, #0a1a33 100%);
    --gradient-ord:  linear-gradient(135deg, #0d4f3c 0%, #063328 60%, #041f1a 100%);
    --gradient-avg:  linear-gradient(135deg, #5a2d00 0%, #3d1e00 60%, #241100 100%);
}

/* ─── Global App Background ───────────────────── */
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a2a4a 0%, #0e1525 40%, #080e1a 100%);
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* ─── Hide Streamlit Branding ─────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ─── Main Content Padding ────────────────────── */
.main .block-container {
    padding: 1.5rem 2.5rem 2rem 2.5rem;
    max-width: 1600px;
}

/* ─── Dashboard Title ─────────────────────────── */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.5px;
    padding-bottom: 0.25rem;
    border-bottom: 2px solid rgba(79,142,247,0.3);
    margin-bottom: 0.25rem !important;
}

h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px;
    margin-bottom: 0.5rem !important;
}

/* ─── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1829 0%, #0e1525 100%) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Sidebar toggle */
[data-testid="stSidebar"] [data-testid="stToggle"] {
    background: rgba(79,142,247,0.12) !important;
    border: 1px solid rgba(79,142,247,0.3) !important;
    border-radius: 8px;
    padding: 0.4rem 0.75rem;
}

/* Sidebar multiselect */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: rgba(79,142,247,0.25) !important;
    border: 1px solid rgba(79,142,247,0.5) !important;
    border-radius: 4px !important;
    color: #a0bfff !important;
    font-size: 0.78rem !important;
}

/* Sidebar slider */
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {
    color: var(--text-muted) !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background: var(--accent-blue) !important;
    border-color: var(--accent-blue) !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderTrack"] > div:first-child {
    background: rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderTrack"] > div:nth-child(2) {
    background: var(--accent-blue) !important;
}

/* Sidebar header label */
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] [data-testid="stHeader"] {
    color: var(--accent-blue) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(79,142,247,0.2);
    padding-bottom: 0.4rem;
    margin-bottom: 1rem !important;
}

/* ─── KPI METRIC CARDS ────────────────────────── */
/* Revenue card — Blue */
[data-testid="stMetric"]:nth-child(1) {
    background: var(--gradient-rev) !important;
    border: 1px solid rgba(79,142,247,0.35) !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(79,142,247,0.12), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}

[data-testid="stMetric"]:nth-child(1)::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4f8ef7, #7eb8ff);
    border-radius: 14px 14px 0 0;
}

/* Orders card — Green */
[data-testid="stMetric"]:nth-child(2) {
    background: var(--gradient-ord) !important;
    border: 1px solid rgba(0,212,170,0.35) !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,212,170,0.12), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}

[data-testid="stMetric"]:nth-child(2)::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00d4aa, #00ffd0);
    border-radius: 14px 14px 0 0;
}

/* Avg Order card — Orange */
[data-testid="stMetric"]:nth-child(3) {
    background: var(--gradient-avg) !important;
    border: 1px solid rgba(255,140,66,0.35) !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(255,140,66,0.12), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}

[data-testid="stMetric"]:nth-child(3)::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ff8c42, #ffb380);
    border-radius: 14px 14px 0 0;
}

/* KPI label & value text */
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    line-height: 1.2;
}

[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ─── Divider ─────────────────────────────────── */
hr {
    border-color: rgba(255,255,255,0.07) !important;
    margin: 1rem 0 !important;
}

/* ─── Download Button ─────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: rgba(79,142,247,0.15) !important;
    border: 1px solid rgba(79,142,247,0.4) !important;
    color: #7eb8ff !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: rgba(79,142,247,0.28) !important;
    border-color: rgba(79,142,247,0.7) !important;
    color: #fff !important;
}

/* ─── DataFrame / Table ───────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid var(--border) !important;
}

[data-testid="stDataFrame"] thead tr th {
    background: rgba(79,142,247,0.15) !important;
    color: #a0bfff !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(79,142,247,0.2) !important;
}

[data-testid="stDataFrame"] tbody tr td {
    color: var(--text-primary) !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(79,142,247,0.07) !important;
}

/* ─── Chart Containers ────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card) !important;
    border-radius: 14px !important;
    border: 1px solid var(--border) !important;
    padding: 0.75rem !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.25) !important;
}

/* ─── Caption / Footer ────────────────────────── */
[data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-align: right;
    margin-top: 1rem;
    border-top: 1px solid var(--border);
    padding-top: 0.5rem;
}

/* ─── Scrollbar ───────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: rgba(79,142,247,0.35); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,142,247,0.6); }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# PLOTLY DARK THEME TEMPLATE
# -------------------------------------------------
PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#8a96b0", size=12),
        title=dict(font=dict(color="#e8edf5", size=14, family="Space Grotesk")),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.08)",
            tickcolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#8a96b0
