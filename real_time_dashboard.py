import streamlit as st
import pandas as pd
import random
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise Command Center PRO", layout="wide")

# -----------------------------
# SOLID PROFESSIONAL UI (NO TRANSPARENCY)
# -----------------------------
st.markdown("""
<style>

/* Global */
.stApp {
    background-color: #f5f7fa;
    font-family: Arial;
}

/* Title */
h1 {
    color: #000000 !important;
    font-weight: 900 !important;
}

/* KPI Cards */
[data-testid="stMetric"] {
    padding: 18px !important;
    border-radius: 14px !important;
    font-weight: bold !important;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* KPI COLORS */
[data-testid="stMetric"]:nth-child(1) {
    background: linear-gradient(135deg, #ff6b6b, #ff4757);
    color: white !important;
}
[data-testid="stMetric"]:nth-child(2) {
    background: linear-gradient(135deg, #1dd1a1, #10ac84);
}
[data-testid="stMetric"]:nth-child(3) {
    background: linear-gradient(135deg, #feca57, #ff9f43);
}
[data-testid="stMetric"]:nth-child(4) {
    background: linear-gradient(135deg, #5f27cd, #341f97);
    color: white !important;
}

/* Metric text */
[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 900 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #2f3640 !important;
    color: white !important;
}

/* Table */
[data-testid="stDataFrame"] {
    background: white !important;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("enterprise.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    time TEXT,
    product TEXT,
    price INTEGER,
    city TEXT
)
""")
conn.commit()

# -----------------------------
# DATA GENERATION
# -----------------------------
products = ["Laptop","Mobile","Tablet","Camera","Headphones","Watch"]
cities = ["Chennai","Mumbai","Delhi","Bangalore","Hyderabad"]

def generate_sale():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000,50000),
        random.choice(cities)
    )

# Insert live data
cursor.execute("INSERT INTO sales VALUES (?,?,?,?)", generate_sale())
conn.commit()

df = pd.read_sql("SELECT * FROM sales", conn)
df["time"] = pd.to_datetime(df["time"])

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Control Panel")

refresh = st.sidebar.slider("Refresh Speed (sec)", 5, 60, 10)
st_autorefresh(interval=refresh * 1000)

city_filter = st.sidebar.multiselect("Filter City", df["city"].unique())
if city_filter:
    df = df[df["city"].isin(city_filter)]

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 Enterprise Command Center PRO")

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_revenue = df["price"].sum()
orders = len(df)
avg = int(df["price"].mean())
cities_count = df["city"].nunique()

# Delta logic
if "last_rev" not in st.session_state:
    st.session_state.last_rev = 0

delta = total_revenue - st.session_state.last_rev
st.session_state.last_rev = total_revenue

# -----------------------------
# KPI DISPLAY
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Revenue", f"₹{total_revenue:,}", f"{delta:+}")
c2.metric("📦 Orders", orders)
c3.metric("📊 Avg Value", f"₹{avg}")
c4.metric("🌍 Cities", cities_count)

st.divider()

# -----------------------------
# CHARTS
# -----------------------------
col1, col2 = st.columns(2)

# Bar Chart
with col1:
    city_data = df.groupby("city")["price"].sum().reset_index()
    fig = px.bar(
        city_data,
        x="city",
        y="price",
        color="city",
        color_discrete_sequence=["#ff6b6b","#1dd1a1","#feca57","#5f27cd","#54a0ff"]
    )
    fig.update_layout(title="Revenue by City")
    st.plotly_chart(fig, use_container_width=True)

# Pie Chart
with col2:
    fig2 = px.pie(
        df,
        names="product",
        color_discrete_sequence=["#ff6b6b","#1dd1a1","#feca57","#5f27cd","#54a0ff"]
    )
    fig2.update_layout(title="Product Distribution")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TREND CHART (NEW)
# -----------------------------
st.subheader("📈 Revenue Trend")

trend = df.set_index("time").resample("1min")["price"].sum().reset_index()

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=trend["time"],
    y=trend["price"],
    mode='lines+markers',
    line=dict(width=3),
))

fig3.update_layout(title="Revenue Over Time")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🟢 Live Transactions")
st.dataframe(df.tail(10), use_container_width=True)

# -----------------------------
# EXPORT
# -----------------------------
st.download_button(
    "⬇️ Download Data",
    data=df.to_csv(index=False),
    file_name="sales_data.csv"
)
