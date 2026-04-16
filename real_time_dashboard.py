import streamlit as st
import pandas as pd
import random
import plotly.express as px
from datetime import datetime
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

# Soft, professional background + matching colors
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #1e293b;
    }
    .stApp header {
        background: transparent !important;
    }

    /* Professional blue primary button */
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

    /* Slightly card‑like dividers */
    .stDivider {
        border-color: #cbd5e1;
    }

    /* Table background */
    .stDataframe {
        border-radius: 8px;
        overflow: hidden;
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
products = ["Laptop","Mobile","Tablet","Camera","Headphones","Watch"]

# More cities
cities = [
    "Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad",
    "Kolkata", "Pune", "Jaipur", "Lucknow", "Indore", "Surat",
    "Visakhapatnam", "Coimbatore", "Madurai", "Trichy"
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
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("📊 Control Panel")

# Filters
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

refresh = st.sidebar.slider("Refresh (sec)", 5, 60, 10)
st_autorefresh(interval=refresh * 1000, key="auto")

# -----------------------------
# SAFE DB READ
# -----------------------------
def load_data():
    return pd.read_sql("SELECT * FROM sales", conn)

# -----------------------------
# REVENUE
# -----------------------------
st.title("📊 Revenue Dashboard PRO")

# Insert one dummy sale every refresh
cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?)", sale())
conn.commit()

df = load_data()

if not df.empty:
    # Apply filters
    if selected_cities:
        df = df[df["city"].isin(selected_cities)]
    if selected_weather:
        df = df[df["weather"].isin(selected_weather)]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"₹{df['price'].sum():,}")
    col2.metric("Orders", len(df))
    col3.metric("Avg", f"₹{int(df['price'].mean())}")
    col4.metric("Cities", df['city'].nunique())

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        fig1 = px.bar(
            df,
            x="city",
            y="price",
            color="city",
            title="Sales by City"
        )
        fig1.update_layout(
            font=dict(family="Arial", size=12),
            title=dict(font=dict(size=16)),
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.pie(
            df,
            names="product",
            title="Sales by Product"
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(
            font=dict(family="Arial", size=12),
            title=dict(font=dict(size=16))
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Live Data")
    st.dataframe(df.tail(10), use_container_width=True)

else:
    st.warning("No sales data yet")

# -----------------------------
# EXPORT
# -----------------------------
st.sidebar.divider()

if st.sidebar.button("Export Sales"):
    load_data().to_csv("sales.csv", index=False)
    st.sidebar.success("Exported")
