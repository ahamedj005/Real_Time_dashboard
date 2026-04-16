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
    --accent-cyan:   #00c8e0;
    --accent-amber:  #f5a623;
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

/* ─── CITY FILTER — Teal / Cyan Professional ──── */
/* Multiselect container */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) > div {
    background: rgba(0, 200, 224, 0.06) !important;
    border: 1px solid rgba(0, 200, 224, 0.35) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    box-shadow: 0 0 0 0px rgba(0,200,224,0.2);
    transition: box-shadow 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) > div:focus-within {
    box-shadow: 0 0 0 2px rgba(0,200,224,0.3) !important;
    border-color: rgba(0,200,224,0.6) !important;
}

/* City tags */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) span[data-baseweb="tag"] {
    background: linear-gradient(135deg, rgba(0,200,224,0.28), rgba(0,180,200,0.18)) !important;
    border: 1px solid rgba(0, 200, 224, 0.55) !important;
    border-radius: 6px !important;
    color: #7ef5ff !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-shadow: 0 0 8px rgba(0,200,224,0.4);
}

/* City tag close button */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) span[data-baseweb="tag"] svg {
    fill: rgba(0,200,224,0.75) !important;
}

/* City dropdown items hover */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) li[aria-selected="false"]:hover {
    background: rgba(0,200,224,0.12) !important;
    color: #7ef5ff !important;
}

/* City label */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) label {
    color: #00c8e0 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

/* ─── WEATHER FILTER — Amber / Gold Professional ─ */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) > div {
    background: rgba(245, 166, 35, 0.06) !important;
    border: 1px solid rgba(245, 166, 35, 0.35) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    box-shadow: 0 0 0 0px rgba(245,166,35,0.2);
    transition: box-shadow 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) > div:focus-within {
    box-shadow: 0 0 0 2px rgba(245,166,35,0.3) !important;
    border-color: rgba(245,166,35,0.65) !important;
}

/* Weather tags */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) span[data-baseweb="tag"] {
    background: linear-gradient(135deg, rgba(245,166,35,0.30), rgba(220,140,20,0.18)) !important;
    border: 1px solid rgba(245, 166, 35, 0.60) !important;
    border-radius: 6px !important;
    color: #ffd77a !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-shadow: 0 0 8px rgba(245,166,35,0.4);
}

/* Weather tag close button */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) span[data-baseweb="tag"] svg {
    fill: rgba(245,166,35,0.75) !important;
}

/* Weather dropdown items hover */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) li[aria-selected="false"]:hover {
    background: rgba(245,166,35,0.12) !important;
    color: #ffd77a !important;
}

/* Weather label */
[data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) label {
    color: #f5a623 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

/* ─── Sidebar filter section dividers ─────────── */
.filter-section-city {
    background: rgba(0, 200, 224, 0.06);
    border: 1px solid rgba(0, 200, 224, 0.2);
    border-radius: 10px;
    padding: 0.6rem 0.75rem 0.25rem 0.75rem;
    margin-bottom: 0.75rem;
}

.filter-section-weather {
    background: rgba(245, 166, 35, 0.06);
    border: 1px solid rgba(245, 166, 35, 0.2);
    border-radius: 10px;
    padding: 0.6rem 0.75rem 0.25rem 0.75rem;
    margin-bottom: 0.75rem;
}

.filter-label-city {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    color: #00c8e0;
    margin-bottom: 0.4rem;
}

.filter-label-weather {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    color: #f5a623;
    margin-bottom: 0.4rem;
}

/* Sidebar slider */
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

/* ─── Refresh badge ───────────────────────────── */
.refresh-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.72rem;
    color: #00c8e0;
    background: rgba(0,200,224,0.1);
    border: 1px solid rgba(0,200,224,0.25);
    border-radius: 20px;
    padding: 3px 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.refresh-dot {
    width: 6px; height: 6px;
    background: #00c8e0;
    border-radius: 50%;
    animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.7); }
}
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
            tickfont=dict(color="#8a96b0", size=11),
            title=dict(font=dict(color="#8a96b0")),
            zerolinecolor="rgba(255,255,255,0.05)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.08)",
            tickcolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#8a96b0", size=11),
            title=dict(font=dict(color="#8a96b0")),
            zerolinecolor="rgba(255,255,255,0.05)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.08)",
            borderwidth=1,
            font=dict(color="#8a96b0"),
        ),
        colorway=["#4f8ef7", "#00d4aa", "#ff8c42", "#a78bfa", "#f472b6", "#fbbf24"],
        margin=dict(l=40, r=20, t=40, b=40),
        hoverlabel=dict(
            bgcolor="#1a2540",
            bordercolor="rgba(79,142,247,0.4)",
            font=dict(color="#e8edf5", family="DM Sans"),
        ),
    )
)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.title("🚀 Enterprise Live Revenue Pulse")
with col_badge:
    st.markdown(
        '<div style="padding-top:0.6rem">'
        '<span class="refresh-badge"><span class="refresh-dot"></span>LIVE · 5s</span>'
        '</div>',
        unsafe_allow_html=True
    )

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = True

if "last_revenue" not in st.session_state:
    st.session_state.last_revenue = 0

# -------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------
st.sidebar.markdown("""
<div style="
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8edf5;
    padding: 0.25rem 0 1rem 0;
    border-bottom: 1px solid rgba(79,142,247,0.25);
    margin-bottom: 1.25rem;
    letter-spacing: -0.3px;
">⚙️ Dashboard Controls</div>
""", unsafe_allow_html=True)

st.session_state.running = st.sidebar.toggle("▶️ Run Simulation", value=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
refresh_rate = st.sidebar.slider("⏱ Refresh Speed (sec)", 5, 60, 5)   # ← DEFAULT 5s

# ── City Filter ─────────────────────────────────
st.sidebar.markdown("""
<div style="margin-top:1.2rem; margin-bottom:0.3rem;">
  <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
               letter-spacing:1.4px; color:#00c8e0;">
    🏙 Filter by City
  </span>
</div>
""", unsafe_allow_html=True)

city_filter = st.sidebar.multiselect(
    label="Filter by City",
    options=["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"],
    default=[],
    label_visibility="collapsed",
)

# ── Weather Filter ───────────────────────────────
st.sidebar.markdown("""
<div style="margin-top:1.1rem; margin-bottom:0.3rem;">
  <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
               letter-spacing:1.4px; color:#f5a623;">
    🌦 Filter by Weather
  </span>
</div>
""", unsafe_allow_html=True)

weather_filter = st.sidebar.multiselect(
    label="Filter by Weather",
    options=["Rain 🌧️", "Cloudy ☁️", "Heat ☀️", "Normal 🌤️", "Unknown"],
    default=[],
    label_visibility="collapsed",
)

st.sidebar.markdown("""
<div style="
    margin-top: 2rem;
    padding: 0.75rem;
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 10px;
    font-size: 0.78rem;
    color: #8a96b0;
    line-height: 1.6;
">
📡 Live data streams every <b style='color:#4f8ef7'>5 seconds</b>.<br>
All transactions are stored in <b style='color:#4f8ef7'>sales.db</b>.
</div>
""", unsafe_allow_html=True)

if st.session_state.running:
    st_autorefresh(interval=refresh_rate * 1000, key="refresh")   # ← uses slider value (default 5s)

# -------------------------------------------------
# DATABASE (cached connection)
# -------------------------------------------------
@st.cache_resource
def get_db():
    conn = sqlite3.connect("sales.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        product TEXT,
        price REAL,
        city TEXT,
        weather TEXT
    )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# -------------------------------------------------
# DATA CONFIG
# -------------------------------------------------
products = ["Laptop","Mobile","Headphones","Keyboard","Monitor","Mouse","Tablet","Smart Watch"]
cities   = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi","Pune"]
prices   = [25000, 35000, 1500, 2000, 12000, 800, 22000, 7000]

# -------------------------------------------------
# WEATHER API
# -------------------------------------------------
@st.cache_data(ttl=300)
def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=3)
        data = r.json()
        condition = data["current_condition"][0]["weatherDesc"][0]["value"].lower()
        if "rain"  in condition: return "Rain 🌧️"
        if "cloud" in condition: return "Cloudy ☁️"
        if "sun"   in condition: return "Heat ☀️"
        return "Normal 🌤️"
    except:
        return "Unknown"

# -------------------------------------------------
# GENERATE SALE
# -------------------------------------------------
def generate_sale():
    product = random.choice(products)
    price   = random.choice(prices)
    city    = random.choice(cities)
    weather = get_weather(city)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO sales(time,product,price,city,weather) VALUES(?,?,?,?,?)",
        (time_now, product, price, city, weather)
    )
    conn.commit()

if st.session_state.running:
    generate_sale()

# -------------------------------------------------
# LOAD & FILTER DATA
# -------------------------------------------------
df = pd.read_sql("SELECT * FROM sales", conn)
df["time"] = pd.to_datetime(df["time"], errors="coerce")

if city_filter:
    df = df[df["city"].isin(city_filter)]
if weather_filter:
    df = df[df["weather"].isin(weather_filter)]

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------
total_revenue = df["price"].sum()
total_orders  = len(df)
avg_order     = df["price"].mean() if total_orders > 0 else 0

delta = total_revenue - st.session_state.last_revenue
st.session_state.last_revenue = total_revenue

c1, c2, c3 = st.columns(3)
c1.metric("💰 Total Revenue",   f"₹{int(total_revenue):,}", f"₹{int(delta):,}")
c2.metric("📦 Total Orders",    total_orders)
c3.metric("📊 Avg Order Value", f"₹{int(avg_order):,}")

st.divider()

# -------------------------------------------------
# EXPORT BUTTON
# -------------------------------------------------
st.download_button(
    "⬇️ Export Sales Data as CSV",
    data=df.to_csv(index=False),
    file_name="sales_data.csv",
    mime="text/csv"
)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# LIVE FEED TABLE
# -------------------------------------------------
st.subheader("🟢 Live Sales Feed")
st.dataframe(
    df.sort_values("id", ascending=False).head(15),
    use_container_width=True,
    hide_index=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# CHARTS — Revenue by City  |  Weather Impact
# -------------------------------------------------
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.subheader("📈 Revenue by City")
    city_chart = df.groupby("city")["price"].sum().reset_index().sort_values("price", ascending=False)
    fig = px.bar(
        city_chart, x="city", y="price",
        text=city_chart["price"].apply(lambda x: f"₹{int(x):,}"),
        color="price",
        color_continuous_scale=[[0,"#1a3a6b"],[0.5,"#4f8ef7"],[1.0,"#7eb8ff"]],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#e8edf5", size=11),
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        xaxis_title="", yaxis_title="Revenue (₹)",
        height=320, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌦 Weather Impact")
    weather_chart = df.groupby("weather")["price"].sum().reset_index()
    fig2 = px.pie(
        weather_chart, names="weather", values="price",
        hole=0.55,
        color_discrete_sequence=["#4f8ef7","#00d4aa","#ff8c42","#a78bfa","#f472b6"],
        template=PLOTLY_TEMPLATE,
    )
    fig2.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(color="#e8edf5", size=11),
        marker=dict(line=dict(color="#0e1525", width=3)),
        hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig2.update_layout(
        height=320,
        legend=dict(font=dict(color="#8a96b0"), orientation="h", y=-0.15),
        annotations=[dict(
            text="Sales<br>Mix", x=0.5, y=0.5, showarrow=False,
            font=dict(color="#e8edf5", size=13, family="Space Grotesk"),
        )],
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# TREND ANALYSIS
# -------------------------------------------------
st.subheader("📊 Revenue Trend (per minute)")

if not df.empty and df["time"].notna().any():
    trend = df.set_index("time").resample("1min")["price"].sum().reset_index()
    fig3 = go.Figure()
    fig3.add_traces([
        go.Scatter(
            x=trend["time"], y=trend["price"],
            mode="lines",
            line=dict(color="rgba(79,142,247,0.25)", width=0),
            fill="tozeroy",
            fillcolor="rgba(79,142,247,0.08)",
            showlegend=False,
            hoverinfo="skip",
        ),
        go.Scatter(
            x=trend["time"], y=trend["price"],
            mode="lines+markers",
            line=dict(color="#4f8ef7", width=2.5, shape="spline", smoothing=0.8),
            marker=dict(color="#7eb8ff", size=7, line=dict(color="#0e1525", width=2)),
            name="Revenue",
            hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>",
        ),
    ])
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        height=300,
        xaxis_title="Time",
        yaxis_title="Revenue (₹)",
        showlegend=False,
        hovermode="x unified",
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# CITY × WEATHER MATRIX
# -------------------------------------------------
st.subheader("🌍 City × Weather Matrix")
matrix = df.groupby(["city", "weather"]).size().reset_index(name="Orders")
st.dataframe(matrix, use_container_width=True, hide_index=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.caption(f"🕒 Last Updated: {datetime.now().strftime('%d %b %Y · %H:%M:%S')}  |  Built with Streamlit + Plotly")
