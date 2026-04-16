import streamlit as st
import pandas as pd
import random
import plotly.express as px
from datetime import datetime
import sqlite3
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Revenue Command Center PRO",
    layout="wide",
    page_icon="📊"
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
# SIDEBAR
# -----------------------------
st.sidebar.title("📊 Control Panel")

refresh = st.sidebar.slider("Refresh (sec)", 5, 60, 10)

st_autorefresh(interval=refresh * 1000, key="auto")

# -----------------------------
# SAFE DB READ
# -----------------------------
def load_data():
    return pd.read_sql("SELECT * FROM sales", conn)

# -----------------------------
# DATA
# -----------------------------
products = ["Laptop","Mobile","Tablet","Camera","Headphones","Watch"]
cities = ["Chennai","Mumbai","Delhi","Bangalore","Hyderabad"]

def weather():
    return random.choice(["Clear","Rain","Clouds","Heat"])

def sale():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000,50000),
        random.choice(cities),
        weather()
    )

# -----------------------------
# REVENUE
# -----------------------------
st.title("📊 Revenue Dashboard PRO")

# Add one dummy sale every refresh
cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?)", sale())
conn.commit()

df = load_data()

if not df.empty:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"₹{df['price'].sum():,}")
    col2.metric("Orders", len(df))
    col3.metric("Avg", f"₹{int(df['price'].mean())}")
    col4.metric("Cities", df['city'].nunique())

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(px.bar(df, x="city", y="price", color="city"), use_container_width=True)

    with c2:
        st.plotly_chart(px.pie(df, names="product"), use_container_width=True)

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
