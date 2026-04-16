import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import random
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise AI Dashboard", layout="wide")

# -----------------------------
# CSS (NO PURPLE + KPI ANIMATION)
# -----------------------------
st.markdown("""
<style>
.stApp { background-color: #f4f6f9; }

/* KPI animation */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.04); }
  100% { transform: scale(1); }
}

[data-testid="stMetric"] {
    animation: pulse 2s infinite;
    border-radius: 12px;
    padding: 15px;
    font-weight: bold;
}

/* KPI colors */
[data-testid="stMetric"]:nth-child(1) { background: #ff6b6b; color: white; }
[data-testid="stMetric"]:nth-child(2) { background: #1dd1a1; }
[data-testid="stMetric"]:nth-child(3) { background: #feca57; }
[data-testid="stMetric"]:nth-child(4) { background: #54a0ff; color: white; }

h1 { color: black; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("enterprise_ai.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    time TEXT,
    price INTEGER,
    city TEXT
)
""")
conn.commit()

# -----------------------------
# DEFAULT USERS
# -----------------------------
if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
    users = [
        ("admin","admin123","Admin"),
        ("manager","manager123","Manager")
    ]
    cursor.executemany("INSERT INTO users VALUES (?,?,?)", users)
    conn.commit()

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        user = cursor.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
        if user and p == user[1]:
            st.session_state.login = True
            st.session_state.role = user[2]
            st.rerun()
        else:
            st.error("Invalid")

    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.success(f"Role: {st.session_state.role}")
refresh = st.sidebar.slider("Refresh",5,60,10)
st_autorefresh(interval=refresh*1000)

# -----------------------------
# DATA GENERATION
# -----------------------------
cities = ["Chennai","Mumbai","Delhi","Bangalore"]

def generate():
    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.randint(2000,50000),
        random.choice(cities)
    )

cursor.execute("INSERT INTO sales VALUES (?,?,?)", generate())
conn.commit()

df = pd.read_sql("SELECT * FROM sales", conn)
df["time"] = pd.to_datetime(df["time"])

# -----------------------------
# KPI
# -----------------------------
total = df["price"].sum()
orders = len(df)
avg = int(df["price"].mean())
cities_count = df["city"].nunique()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Revenue", f"₹{total:,}")
c2.metric("Orders", orders)
c3.metric("Avg", f"₹{avg}")
c4.metric("Cities", cities_count)

st.divider()

# -----------------------------
# CHARTS
# -----------------------------
col1,col2 = st.columns(2)

with col1:
    fig = px.bar(df, x="city", y="price",
                 color="city",
                 color_discrete_sequence=["#ff6b6b","#1dd1a1","#feca57","#54a0ff"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.line(df, x="time", y="price")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# AI PREDICTION (ML)
# -----------------------------
st.subheader("🧠 AI Revenue Prediction")

if len(df) > 5:
    df["t"] = np.arange(len(df))
    model = LinearRegression()
    model.fit(df[["t"]], df["price"])

    future = np.array([[len(df)+i] for i in range(5)])
    pred = model.predict(future)

    st.write("Next 5 predictions:", [int(x) for x in pred])

# -----------------------------
# ROLE BASED VIEW
# -----------------------------
if st.session_state.role == "Admin":
    st.success("Admin Panel Access")
    st.dataframe(df)

elif st.session_state.role == "Manager":
    st.info("Manager View (limited)")
    st.dataframe(df.tail(5))
