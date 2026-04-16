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
# POWER BI PROFESSIONAL THEME — CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary:     #0d1117;
    --bg-secondary:   #161b22;
    --bg-card:        #1c2333;
    --bg-card-hover:  #21293a;
    --accent-gold:    #f2c811;
    --accent-blue:    #118dff;
    --accent-teal:    #01b8aa;
    --accent-orange:  #fd7b4d;
    --accent-purple:  #8764b8;
    --accent-green:   #107c10;
    --text-primary:   #e6edf3;
    --text-muted:     #8b949e;
    --border:         #30363d;
    --shadow-glow:    0 0 24px rgba(17, 141, 255, 0.15);
    --radius:         12px;
    --radius-sm:      8px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── App Background ── */
.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, rgba(17,141,255,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(1,184,170,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(242,200,17,0.03) 0%, transparent 70%),
        linear-gradient(160deg, #0d1117 0%, #111827 50%, #0d1117 100%);
    background-attachment: fixed;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stSlider > div > div {
    background: var(--accent-blue) !important;
}

/* ── Main Title ── */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.9rem !important;
    background: linear-gradient(90deg, #f2c811 0%, #118dff 50%, #01b8aa 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.5px !important;
    margin-bottom: 4px !important;
}

/* ── Section Headings ── */
h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
    border-left: 3px solid var(--accent-blue);
    padding-left: 10px !important;
    margin-top: 0.5rem !important;
}

/* ── KPI METRIC CARDS ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-hover) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.4rem 1.6rem !important;
    box-shadow: var(--shadow-glow), 0 4px 16px rgba(0,0,0,0.4) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 32px rgba(17,141,255,0.22), 0 8px 24px rgba(0,0,0,0.5) !important;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal));
    border-radius: var(--radius) var(--radius) 0 0;
}

/* KPI Label */
[data-testid="metric-container"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
}

/* KPI Value */
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--accent-gold) !important;
    line-height: 1.1 !important;
}

/* KPI Delta */
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDeltaIcon-Up"] { color: #3dba4e !important; }
[data-testid="stMetricDeltaIcon-Down"] { color: #f85149 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
iframe[data-testid="stDataFrameResizable"] {
    border-radius: var(--radius) !important;
}

/* ── Plotly Charts Wrapper ── */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 0.5rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}

/* ── Download Button ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(90deg, #118dff, #01b8aa) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 1.2rem !important;
    letter-spacing: 0.4px !important;
    transition: opacity 0.2s, transform 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 1rem 0 !important;
}

/* ── Multiselect Tags ── */
[data-baseweb="tag"] {
    background-color: rgba(17, 141, 255, 0.2) !important;
    border: 1px solid rgba(17, 141, 255, 0.4) !important;
    color: #60b0ff !important;
    border-radius: 4px !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] span {
    background-color: var(--accent-blue) !important;
}

/* ── Caption / Footer ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.3px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# POWER BI COLOR PALETTE for charts
# -------------------------------------------------
POWERBI_COLORS = [
    "#118dff",  # blue
    "#01b8aa",  # teal
    "#f2c811",  # gold
    "#fd7b4d",  # orange
    "#8764b8",  # purple
    "#374649",  # dark slate
    "#fd625e",  # red
    "#33c7f5",  # sky
]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8b949e", size=11),
    title_font=dict(family="Space Grotesk", color="#e6edf3", size=14),
    legend=dict(
        bgcolor="rgba(22,27,34,0.8)",
        bordercolor="#30363d",
        borderwidth=1,
        font=dict(color="#e6edf3")
    ),
    margin=dict(l=16, r=16, t=40, b=16),
    colorway=POWERBI_COLORS,
)

AXIS_STYLE = dict(
    gridcolor="#21293a",
    zerolinecolor="#30363d",
    tickfont=dict(color="#8b949e"),
    linecolor="#30363d",
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🚀 Enterprise Live Revenue Pulse")
st.markdown(
    "<p style='color:#8b949e;font-size:0.82rem;margin-top:-12px;margin-bottom:16px;'>"
    "Real-time sales intelligence · Auto-refreshing · India Market</p>",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = True
if "last_revenue" not in st.session_state:
    st.session_state.last_revenue = 0

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown("### ⚙️ Dashboard Controls")
st.sidebar.markdown("---")

st.session_state.running = st.sidebar.toggle("▶️ Live Simulation", value=True)
refresh_rate = st.sidebar.slider("⏱ Refresh Speed (sec)", 5, 60, 15)

st.sidebar.markdown("#### 🔍 Filters")
city_filter = st.sidebar.multiselect(
    "🏙 City",
    ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"],
    default=[]
)
weather_filter = st.sidebar.multiselect(
    "🌦 Weather",
    ["Rain 🌧️", "Cloudy ☁️", "Heat ☀️", "Normal 🌤️", "Unknown"],
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color:#484f58;font-size:0.72rem;text-align:center;'>Powered by Streamlit · v2.0</p>",
    unsafe_allow_html=True
)

if st.session_state.running:
    st_autorefresh(interval=refresh_rate * 1000, key="refresh")

# -------------------------------------------------
# DATABASE
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
products = ["Laptop", "Mobile", "Headphones", "Keyboard", "Monitor", "Mouse", "Tablet", "Smart Watch"]
cities   = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"]
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
    product  = random.choice(products)
    price    = random.choice(prices)
    city     = random.choice(cities)
    weather  = get_weather(city)
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

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue",   f"₹{int(total_revenue):,}",  f"₹{int(delta):,}")
c2.metric("📦 Total Orders",    total_orders)
c3.metric("📊 Avg Order Value", f"₹{int(avg_order):,}")
c4.metric("🏙 Active Cities",
          len(df["city"].unique()) if not df.empty else 0)

st.divider()

# -------------------------------------------------
# EXPORT
# -------------------------------------------------
col_export, col_info = st.columns([1, 5])
with col_export:
    st.download_button(
        "⬇️ Export CSV",
        data=df.to_csv(index=False),
        file_name="sales_data.csv",
        mime="text/csv"
    )
with col_info:
    st.markdown(
        f"<p style='color:#8b949e;font-size:0.78rem;padding-top:10px;'>"
        f"📅 Last updated: <b style='color:#e6edf3;'>{datetime.now().strftime('%d %b %Y · %H:%M:%S')}</b> &nbsp;|&nbsp; "
        f"Rows loaded: <b style='color:#e6edf3;'>{len(df):,}</b></p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# LIVE FEED
# -------------------------------------------------
st.subheader("🟢 Live Sales Feed")
st.dataframe(
    df.sort_values("id", ascending=False).head(15),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -------------------------------------------------
# CHARTS ROW 1 — Bar + Pie
# -------------------------------------------------
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📈 Revenue by City")
    city_chart = df.groupby("city")["price"].sum().reset_index().sort_values("price", ascending=False)

    fig_bar = px.bar(
        city_chart, x="city", y="price",
        text=city_chart["price"].apply(lambda x: f"₹{int(x):,}"),
        color="city",
        color_discrete_sequence=POWERBI_COLORS,
    )
    fig_bar.update_traces(
        textposition="outside",
        textfont=dict(color="#e6edf3", size=11),
        marker_line_width=0,
        width=0.55,
    )
    fig_bar.update_layout(
        **CHART_LAYOUT,
        xaxis=dict(title="", **AXIS_STYLE),
        yaxis=dict(title="Revenue (₹)", **AXIS_STYLE),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🌦 Weather Impact")
    weather_chart = df.groupby("weather")["price"].sum().reset_index()

    fig_pie = px.pie(
        weather_chart, names="weather", values="price",
        color_discrete_sequence=POWERBI_COLORS,
        hole=0.55,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont=dict(color="#e6edf3", size=11),
        marker=dict(line=dict(color="#0d1117", width=2)),
    )
    fig_pie.update_layout(
        **CHART_LAYOUT,
        showlegend=True,
        annotations=[dict(
            text="Revenue",
            x=0.5, y=0.5,
            font=dict(family="Space Grotesk", size=13, color="#8b949e"),
            showarrow=False
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------------------------
# CHARTS ROW 2 — Trend + Product
# -------------------------------------------------
col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("📊 Sales Trend")
    if not df.empty:
        trend = df.set_index("time").resample("1min")["price"].sum().reset_index()
        trend.columns = ["time", "revenue"]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["time"], y=trend["revenue"],
            mode="lines+markers",
            line=dict(color="#118dff", width=2.5, shape="spline"),
            marker=dict(size=5, color="#f2c811", line=dict(color="#118dff", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(17,141,255,0.08)",
            name="Revenue",
        ))
        fig_trend.update_layout(
            **CHART_LAYOUT,
            xaxis=dict(title="", **AXIS_STYLE),
            yaxis=dict(title="Revenue (₹)", **AXIS_STYLE),
            showlegend=False,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

with col4:
    st.subheader("🛍 Top Products")
    if not df.empty:
        prod_chart = df.groupby("product")["price"].sum().reset_index().sort_values("price")

        fig_prod = px.bar(
            prod_chart, x="price", y="product",
            orientation="h",
            color="price",
            color_continuous_scale=[[0, "#1c2333"], [0.4, "#118dff"], [1, "#f2c811"]],
            text=prod_chart["price"].apply(lambda x: f"₹{int(x):,}"),
        )
        fig_prod.update_traces(
            textposition="outside",
            textfont=dict(color="#e6edf3", size=10),
        )
        fig_prod.update_layout(
            **CHART_LAYOUT,
            xaxis=dict(title="Revenue (₹)", **AXIS_STYLE),
            yaxis=dict(title="", **AXIS_STYLE),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_prod, use_container_width=True)

# -------------------------------------------------
# CITY × WEATHER MATRIX
# -------------------------------------------------
st.subheader("🌍 City × Weather Matrix")

if not df.empty:
    pivot = df.groupby(["city", "weather"])["price"].sum().unstack(fill_value=0)

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=[[0, "#161b22"], [0.3, "#1c4a7a"], [0.7, "#118dff"], [1, "#f2c811"]],
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_traces(textfont=dict(color="#e6edf3", size=11))
    fig_heat.update_layout(
        **CHART_LAYOUT,
        xaxis=dict(title="Weather", **AXIS_STYLE),
        yaxis=dict(title="City", **AXIS_STYLE),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Not enough data yet for the matrix.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center;color:#484f58;font-size:0.72rem;letter-spacing:0.5px;'>"
    "Enterprise Revenue Pulse · Built with Streamlit · "
    f"Refreshes every {refresh_rate}s · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</p>",
    unsafe_allow_html=True
)
