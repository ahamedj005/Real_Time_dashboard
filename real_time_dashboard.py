import streamlit as st
import pandas as pd
import random
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG + CUSTOM THEME
# -----------------------------
st.set_page_config(
    page_title="Revenue Command Center PRO",
    layout="wide",
    page_icon="📊"
)

# Full‑page soft blue‑gray background + matching sidebar + cleaner chart spacing
st.markdown(
    """
    <style>
    /* Main page background */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #1e293b;
    }

    /* Header background transparency */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* Sidebar background to match main page */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-right: 1px solid #cbd5e1;
    }

    /* Sidebar text color */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stButton {
        color: #1e293b;
    }

    /* Buttons & metrics */
    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }
    .stButton button:hover {
        background-color: #1d4ed8;
    }

    .stMetricLabel {
        color: #475569;
        font-size: 1rem;
    }

    .stMetricValue {
        color: #0f172a;
        font-weight: 500;
    }

    .stDivider {
        border-color: #cbd5e1;
    }

    .stDataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    /* More generous spacing around charts */
    .stPlotlyChart {
        margin-top: 0.5rem;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# DB
# -----------------------------
conn = sqlite3.connect("command_center.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS sales(
        time TEXT,
        product TEXT,
        price INTEGER,
        city TEXT,
        weather TEXT
    )""")

    conn.commit()

init_db()

# -----------------------------
# DATA
# -----------------------------
# Many more products with variants
products = [
    "Laptop (15\")", "Laptop (13\")", "Gaming Laptop", "Ultrabook",
    "Mobile - Budget", "Mobile - Mid", "Mobile - Flagship",
    "Tablet 8\"", "Tablet 10\"",
    "DSLR Camera", "Mirrorless Camera", "Action Camera",
    "Wireless Headphones", "Wired Headphones", "Earbuds",
    "Smart Watch", "Fitness Watch",
    "Desktop PC", "All‑in‑One PC",
    "Monitor 24\"", "Monitor 27\"",
    "Mechanical Keyboard", "Membrane Keyboard",
    "Gaming Mouse", "Office Mouse",
    "Inkjet Printer", "Laser Printer",
    "Wi‑Fi Router", "Mesh Router",
    "External HDD 1TB", "External HDD 2TB",
    "SSD 500GB", "SSD 1TB",
    "Power Bank 10000mAh", "Power Bank 20000mAh",
    "Smart Speaker", "Home Speaker",
    "DJI Drone", "Camera Drone"
]

# Many more cities
cities = [
    "Chennai", "Madurai", "Trichy", "Coimbatore", "Salem",
    "Mumbai", "Thane", "Pune", "Nashik", "Nagpur",
    "Delhi", "Noida", "Gurgaon", "Faridabad",
    "Bangalore", "Mysore", "Hubli", "Mangalore",
    "Hyderabad", "Warangal", "Vijayawada", "Visakhapatnam",
    "Kolkata", "Siliguri", "Durgapur",
    "Jaipur", "Udaipur", "Jodhpur",
    "Lucknow", "Kanpur", "Prayagraj",
    "Indore", "Bhopal", "Ujjain",
    "Surat", "Vadodara", "Rajkot",
    "Patna", "Bhubaneswar", "Guwahati"
]

weather_types = ["Clear", "Rain", "Clouds", "Heat", "Storm"]

def weather():
    return random.choice(weather_types)

def sale():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000, 50000),
        random.choice(cities),
        weather()
    )

# -----------------------------
# SIDEBAR FILTERS: PRODUCTS, DATE, TIME, CITY, WEATHER
# -----------------------------
st.sidebar.title("🚀 Revenue War Room")

now = datetime.now()
today = now.date()

# Default date range: last 7 days → today
min_date = today - timedelta(days=7)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, today)
    # no min_value / max_value → user can pick any date
)

time_start = st.sidebar.time_input("From Time", value=datetime.now().replace(hour=0, minute=0).time())
time_end = st.sidebar.time_input("To Time", value=datetime.now().time())

# Filters
selected_products = st.sidebar.multiselect(
    "Filter by Product",
    options=products,
    default=products
)

selected_cities = st.sidebar.multiselect(
    "Filter by City",
    options=cities,
    default=cities
)

selected_weather = st.sidebar.multiselect(
    "Filter by Weather",
    options=weather_types,
    default=weather_types
)

refresh = st.sidebar.slider("Refresh (sec)", 5, 60, 30)
st_autorefresh(interval=refresh * 1000, key="auto")

# -----------------------------
# SAFE DB READ
# -----------------------------
def load_data():
    df = pd.read_sql("SELECT * FROM sales", conn)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])
    return df

# -----------------------------
# REVENUE (ALL KPIs + VISUALS ON ONE PAGE)
# -----------------------------
st.markdown(
    """
    <h1 style='font-size:1.8rem; margin-bottom:0.2rem;'>
        🚀 Revenue Command Center PRO
    </h1>
    <p style='color:#475569; font-size:0.9rem; margin-top:-0.5rem; margin-bottom:0.8rem;'>
        War‑Room View • For Manager Use Only
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<p style='color:#475569; font-size:0.9rem; margin-top:-0.5rem; margin-bottom:0.5rem;'>"
    f"Today: {now.strftime('%Y-%m-%d')} &nbsp; • &nbsp; "
    f"Live time: {now.strftime('%H:%M:%S')}</p>",
    unsafe_allow_html=True
)

st.markdown("### 🎯 Executive Snapshot")

# Insert one dummy sale every refresh
cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?)", sale())
conn.commit()

df = load_data()

if df.empty:
    st.warning("No sales data yet")
else:
    # Convert selected date range to datetime range
    dt_start = pd.Timestamp.combine(
        date_range[0],
        time_start
    )
    dt_end = pd.Timestamp.combine(
        date_range[1],
        time_end
    )

    # Apply global filters
    df_filtered = df[
        (df["time"] >= dt_start) &
        (df["time"] <= dt_end)
    ]

    if selected_products:
        df_filtered = df_filtered[df_filtered["product"].isin(selected_products)]

    if selected_cities:
        df_filtered = df_filtered[df_filtered["city"].isin(selected_cities)]

    if selected_weather:
        df_filtered = df_filtered[df_filtered["weather"].isin(selected_weather)]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"₹{df_filtered['price'].sum():,}")
    col2.metric("Orders", len(df_filtered))

    # Safe Avg calculation to avoid ValueError on empty data
    avg_price = df_filtered["price"].mean()
    avg_str = f"₹{int(avg_price)}" if pd.notna(avg_price) else "₹—"
    col3.metric("Avg", avg_str)

    col4.metric("Cities", df_filtered['city'].nunique())

    st.markdown("---")

    # 📈 Revenue Trend
    st.subheader("📈 Revenue Trend")
    st.markdown("<p style='color:#475569; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:0.4rem;'>"
                "Revenue trend over time (per minute).",
                unsafe_allow_html=True)

    if not df_filtered.empty:
        df_trend = df_filtered.copy()
        df_trend["minute"] = df_trend["time"].dt.floor("1min")
        trend = df_trend.groupby("minute")["price"].sum().reset_index()

        fig_trend = px.line(
            trend,
            x="minute",
            y="price",
            title=None
        )
        fig_trend.update_layout(
            font=dict(family="Arial", size=12),
            xaxis_title="Time",
            yaxis_title="Revenue (₹)",
            margin=dict(t=10, b=80, l=60, r=30)
        )
        st.plotly_chart(fig_trend, use_container_width=True, height=450)
    else:
        st.info("No data for the selected filters.")
    st.markdown("---")

    # 📍 Revenue by City
    st.subheader("📍 Revenue by City")
    st.markdown("<p style='color:#475569; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:0.4rem;'>"
                "Revenue distribution across cities.",
                unsafe_allow_html=True)

    if not df_filtered.empty:
        fig_city = px.bar(
            df_filtered,
            x="city",
            y="price",
            color="city",
            title=None
        )
        fig_city.update_layout(
            font=dict(family="Arial", size=12),
            showlegend=False,
            xaxis_title="City",
            yaxis_title="Revenue (₹)",
            margin=dict(t=10, b=70, l=60, r=30)
        )
        st.plotly_chart(fig_city, use_container_width=True, height=450)
    else:
        st.info("No data for the selected filters.")
    st.markdown("---")

    # 📦 Product Revenue Breakdown (Pie) — DARKER, CLEARER FONT
    st.subheader("📦 Product Revenue Breakdown")
    st.markdown("<p style='color:#475569; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:0.4rem;'>"
                "Distribution of total revenue across products.",
                unsafe_allow_html=True)

    if not df_filtered.empty:
        fig_product = px.pie(
            df_filtered,
            names="product",
            values="price",
            title=None
        )
        fig_product.update_traces(
            textinfo="label+percent",
            textposition="outside",
            # Make labels dark and bold for better visibility
            textfont=dict(
                color="#1e293b",      # dark text
                size=12,
                family="Arial"
            ),
            pull=[0.05 if i < 5 else 0 for i in range(len(df_filtered["product"].unique()))]
        )
        fig_product.update_layout(
            font=dict(family="Arial", size=10),
            margin=dict(t=40, b=140, l=60, r=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="center",
                x=0.5,
                font=dict(size=9)
            ),
            showlegend=True,
            title_x=0.5,
            title_y=0.95
        )
        st.plotly_chart(fig_product, use_container_width=True, height=550)
    else:
        st.info("No data for the selected filters.")
    st.markdown("---")

    # 🔥 Top 8 Products by Revenue
    st.subheader("🔥 Top 8 Products by Revenue")
    st.markdown("<p style='color:#475569; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:0.4rem;'>"
                "Top‑performing products by revenue contribution.",
                unsafe_allow_html=True)

    if not df_filtered.empty:
        top_products = df_filtered.groupby("product")["price"].sum().reset_index()
        top_products = top_products.sort_values("price", ascending=False).head(8)

        fig_top = px.bar(
            top_products,
            x="product",
            y="price",
            title=None,
            color="product"
        )
        fig_top.update_layout(
            font=dict(family="Arial", size=10),
            xaxis_title="Product",
            yaxis_title="Revenue (₹)",
            xaxis_tickangle=-45,
            showlegend=False,
            margin=dict(t=10, b=90, l=60, r=30)
        )
        st.plotly_chart(fig_top, use_container_width=True, height=450)
    else:
        st.info("No data for the selected filters.")
    st.markdown("---")

    # 📊 Live Data
    st.subheader("📊 Live Data")
    st.markdown("<p style='color:#475569; font-size:0.9rem; margin-top:-0.6rem; margin-bottom:0.4rem;'>"
                "Latest transactions in your dataset.",
                unsafe_allow_html=True)

    st.dataframe(df_filtered.tail(20), use_container_width=True)

# -----------------------------
# EXPORT
# -----------------------------
st.sidebar.divider()

if st.sidebar.button("Export Sales"):
    load_data().to_csv("sales.csv", index=False)
    st.sidebar.success("Exported")
