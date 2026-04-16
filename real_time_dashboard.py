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
# PROFESSIONAL MULTI-COLOR THEME CSS
# -------------------------------------------------
st.markdown("""
<style>
/* ─── Google Fonts ───────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');

/* ─── Color Palette ──────────────────────────── */
:root {
    --bg-primary:    linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    --bg-card:       rgba(255,255,255,0.03);
    --bg-card-glow:  rgba(255,255,255,0.08);
    --border:        rgba(255,255,255,0.12);
    --text-primary:  #ffffff;
    --text-secondary: #e2e8f0;
    --text-muted:    #94a3b8;
    
    /* Vibrant Multi-Color Palette */
    --primary-gold:    #FFD700;
    --primary-emerald: #10B981;
    --primary-crimson: #EF4444;
    --primary-violet:  #8B5CF6;
    --primary-cyan:    #06B6D4;
    --primary-amber:   #F59E0B;
    --primary-rose:    #EC4899;
    
    /* Gradients */
    --gradient-gold:    linear-gradient(135deg, #FFB800 0%, #FFD700 50%, #FFA500 100%);
    --gradient-emerald: linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%);
    --gradient-crimson: linear-gradient(135deg, #DC2626 0%, #EF4444 50%, #F87171 100%);
    --gradient-violet:  linear-gradient(135deg, #7C3AED 0%, #8B5CF6 50%, #A78BFA 100%);
    --gradient-cyan:    linear-gradient(135deg, #0891B2 0%, #06B6D4 50%, #22D3EE 100%);
}

/* ─── Global Styles ──────────────────────────── */
.stApp {
    background: var(--bg-primary);
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

#MainMenu, footer, header { visibility: hidden; }
.main .block-container { padding: 2rem 3rem; max-width: 1800px; }

/* ─── Typography ─────────────────────────────── */
h1 {
    font-family: 'Poppins', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #FFD700 0%, #10B981 50%, #EF4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.8px;
    margin-bottom: 1rem !important;
}

h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
    letter-spacing: 0.2px;
}

/* ─── Sidebar ────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,15,35,0.95) 0%, rgba(26,26,46,0.95) 100%);
    border-right: 1px solid var(--border);
    backdrop-filter: blur(20px);
}

[data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* ─── ENHANCED KPI CARDS ─────────────────────── */
.metric-container {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 2rem 1.5rem !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
    transition: all 0.3s ease !important;
    backdrop-filter: blur(15px);
}

.metric-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 25px 50px rgba(0,0,0,0.4);
}

.metric-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    z-index: 2;
}

/* Revenue Card - Gold */
.metric-container:nth-child(1) { 
    background: linear-gradient(145deg, rgba(255,215,0,0.15) 0%, rgba(255,165,0,0.1) 100%);
    border-color: var(--primary-gold);
}
.metric-container:nth-child(1)::before { background: var(--gradient-gold); }

/* Orders Card - Emerald */
.metric-container:nth-child(2) { 
    background: linear-gradient(145deg, rgba(16,185,129,0.15) 0%, rgba(52,211,153,0.1) 100%);
    border-color: var(--primary-emerald);
}
.metric-container:nth-child(2)::before { background: var(--gradient-emerald); }

/* Average Card - Crimson */
.metric-container:nth-child(3) { 
    background: linear-gradient(145deg, rgba(239,68,68,0.15) 0%, rgba(248,113,113,0.1) 100%);
    border-color: var(--primary-crimson);
}
.metric-container:nth-child(3)::before { background: var(--gradient-crimson); }

.metric-container label {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem !important;
}

.metric-container [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    line-height: 1;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.metric-container [data-testid="stMetricDelta"] {
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    margin-top: 0.5rem;
}

/* ─── Enhanced Tables ────────────────────────── */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: blur(10px);
}

[data-testid="stDataFrame"] thead tr th {
    background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 2px solid var(--border) !important;
}

[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: rgba(255,255,255,0.02) !important;
}

[data-testid="stDataFrame"] tbody tr:hover td {
    background: linear-gradient(90deg, rgba(255,215,0,0.1), rgba(16,185,129,0.1)) !important;
}

/* ─── Enhanced Charts ────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 20px !important;
    border: 1px solid var(--border) !important;
    padding: 1.5rem !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    backdrop-filter: blur(15px);
}

/* ─── Download Button ───────────────────────── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--primary-gold), var(--primary-emerald)) !important;
    border: none !important;
    color: #000 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 10px 25px rgba(255,215,0,0.3);
}

[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(255,215,0,0.4);
}

/* ─── Scrollbar ─────────────────────────────── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
::-webkit-scrollbar-thumb { 
    background: linear-gradient(135deg, var(--primary-gold), var(--primary-emerald));
    border-radius: 10px; 
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# ENHANCED PLOTLY TEMPLATE
# -------------------------------------------------
PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13, weight=500),
        title=dict(
            font=dict(color="#ffffff", size=16, family="Poppins", weight=700),
            x=0.05, xanchor="left"
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.15)",
            tickcolor="rgba(255,255,255,0.2)",
            tickfont=dict(color="#e2e8f0", size=12, weight=600),
            title=dict(font=dict(color="#ffffff", weight=600)),
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.15)",
            tickcolor="rgba(255,255,255,0.2)",
            tickfont=dict(color="#e2e8f0", size=12, weight=600),
            title=dict(font=dict(color="#ffffff", weight=600)),
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.08)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            font=dict(color="#e2e8f0", weight=500),
            orientation="h",
            yanchor="bottom",
            y=-0.2
        ),
        colorway=[
            "#FFD700", "#10B981", "#EF4444", "#8B5CF6", 
            "#06B6D4", "#F59E0B", "#EC4899", "#3B82F6"
        ],
        margin=dict(l=50, r=20, t=50, b=50),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="rgba(255,255,255,0.2)",
            font=dict(color="#0f0f23", family="Inter", weight=600),
        ),
    )
)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("🚀 Enterprise Live Revenue Pulse")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = True
if "last_revenue" not in st.session_state:
    st.session_state.last_revenue = 0

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown("""
<div style="
    font-family: 'Poppins', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FFD700 0%, #10B981 50%, #EF4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 1rem 0;
    border-bottom: 2px solid rgba(255,255,255,0.2);
    margin-bottom: 1.5rem;
">⚙️ Control Panel</div>
""", unsafe_allow_html=True)

st.session_state.running = st.sidebar.toggle("▶️ Live Simulation", value=True)
refresh_rate = st.sidebar.slider("⏱️ Refresh Rate (sec)", 3, 30, 10)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
city_filter = st.sidebar.multiselect(
    "🏙️ Cities",
    ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"],
    default=[]
)
weather_filter = st.sidebar.multiselect(
    "🌤️ Weather",
    ["Rain 🌧️", "Cloudy ☁️", "Sunny ☀️", "Clear 🌤️", "Unknown ❓"],
    default=[]
)

if st.session_state.running:
    st_autorefresh(interval=refresh_rate * 1000)

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

# -------------------------------------------------
# DATA
# -------------------------------------------------
products = ["Laptop", "iPhone", "Headphones", "Keyboard", "Monitor", "Mouse", "iPad", "Smart Watch"]
cities = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"]
prices = [45000, 75000, 3500, 2500, 22000, 1200, 55000, 18000]

@st.cache_data(ttl=300)
def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=2)
        data = r.json()
        condition = data["current_condition"][0]["weatherDesc"][0]["value"].lower()
        if "rain" in condition: return "Rain 🌧️"
        if "cloud" in condition: return "Cloudy ☁️"
        if "sun" in condition: return "Sunny ☀️"
        return "Clear 🌤️"
    except:
        return "Unknown ❓"

def generate_sale():
    product = random.choice(products)
    price = random.choice(prices) * random.uniform(0.85, 1.15)
    city = random.choice(cities)
    weather = get_weather(city)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales(time,product,price,city,weather) VALUES(?,?,?,?,?)",
        (time_now, product, price, city, weather)
    )
    conn.commit()

if st.session_state.running:
    generate_sale()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC LIMIT 10000", conn)
df["time"] = pd.to_datetime(df["time"], errors="coerce")

if city_filter:
    df = df[df["city"].isin(city_filter)]
if weather_filter:
    df = df[df["weather"].isin(weather_filter)]

# -------------------------------------------------
# ENHANCED KPI METRICS
# -------------------------------------------------
total_revenue = df["price"].sum()
total_orders = len(df)
avg_order = df["price"].mean() if total_orders > 0 else 0

delta = total_revenue - st.session_state.last_revenue
st.session_state.last_revenue = total_revenue

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
cols = st.columns(3, gap="large")
with cols[0]:
    st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>💰</div>
        <h3 style='margin: 0 0 1rem 0; color: #FFD700;'>Total Revenue</h3>
    </div>
    """, unsafe_allow_html=True)
    st.metric("", f"₹{int(total_revenue):,}", f"₹{int(delta):,}", delta_color="normal")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
with cols[1]:
    st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📦</div>
        <h3 style='margin: 0 0 1rem 0; color: #10B981;'>Total Orders</h3>
    </div>
    """, unsafe_allow_html=True)
    st.metric("", f"{total_orders:,}", "+{total_orders//10}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
with cols[2]:
    st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📊</div>
        <h3 style='margin: 0 0 1rem 0; color: #EF4444;'>Avg Order Value</h3>
    </div>
    """, unsafe_allow_html=True)
    st.metric("", f"₹{int(avg_order):,}")
st.markdown('</div></div>', unsafe_allow_html=True)

st.divider()

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
col1, col2 = st.columns([1, 4])
with col1:
    st.download_button(
        "⬇️ Export CSV",
        data=df.to_csv(index=False),
        file_name=f"sales_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# -------------------------------------------------
# LIVE FEED
# -------------------------------------------------
st.markdown("### 🟢 Live Transaction Feed")
st.dataframe(
    df.head(20),
    use_container_width=True,
    hide_index=True,
    column_config={
        "price": st.column_config.NumberColumn("Price", format="₹%.0f"),
        "time": st.column_config.TimeColumn("Time")
    }
)

# -------------------------------------------------
# CHARTS ROW 1
# -------------------------------------------------
st.markdown("### 📊 Revenue Analytics")
col1, col2 = st.columns(2, gap="large")

with col1:
    city_data = df.groupby("city")["price"].sum().reset_index().sort_values("price", ascending=False)
    fig1 = px.bar(
        city_data, x="city", y="price",
        text=[f"₹{int(x):,}" for x in city_data["price"]],
        color="price",
        color_continuous_scale=["#8B5CF6","#06B6D4","#F59E0B","#EC4899","#10B981"],
        template=PLOTLY_TEMPLATE,
    )
    fig1.update_traces(textposition="outside", textfont=dict(size=14, weight=700, color="#ffffff"))
    fig1.update_layout(height=400, showlegend=False, title="Revenue by City")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    weather_data = df.groupby("weather")["price"].sum().reset_index()
    fig2 = px.pie(
        weather_data, names="weather", values="price",
        hole=0.4,
        color_discrete_sequence=["#FFD700","#10B981","#EF4444","#8B5CF6","#06B6D4","#F59E0B","#EC4899"],
        template=PLOTLY_TEMPLATE,
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=13, weight=600))
    fig2.update_layout(height=400, title="Weather Revenue Share")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# TREND CHART
# -------------------------------------------------
st.markdown("### 📈 Revenue Trend (Live)")
if not df.empty and df["time"].notna().any():
    trend_data = df.set_index("time").resample("1min").sum()["price"].tail(60).reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=trend_data["time"], y=trend_data["price"],
        mode="lines+markers",
        line=dict(color="#FFD700", width=4),
        marker=dict(size=8, color="#10B981"),
        name="Live Revenue",
        hovertemplate="<b>%{x|%H:%M:%S}</b><br>₹%{y:,.0f}<extra></extra>"
    ))
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        height=450,
        title="60-Minute Revenue Trend",
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# MATRIX
# -------------------------------------------------
st.markdown("### 🌍 City × Weather Matrix")
matrix = df.groupby(["city", "weather"]).agg({
    "price": "sum",
    "id": "count"
}).round(0).reset_index()
matrix.columns = ["City", "Weather", "Revenue", "Orders"]
st.dataframe(matrix, use_container_width=True, hide_index=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(f"🕐 Updated: {datetime.now().strftime('%d %B %Y | %H:%M:%S IST')} | 🎨 Professional Multi-Color Dashboard")
