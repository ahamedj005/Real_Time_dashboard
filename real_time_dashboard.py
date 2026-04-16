import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Enterprise Command Center PRO",
    layout="wide",
    page_icon="📈"
)

# =========================================================
# PROFESSIONAL UI - NO PURPLE
# =========================================================
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f8;
    font-family: Arial, sans-serif;
}

h1, h2, h3 {
    color: #111111 !important;
    font-weight: 800 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1f2937 !important;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    padding: 18px !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    border: 0 !important;
}

/* Revenue */
div[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #ff6b6b, #ee5253) !important;
}
/* Orders */
div[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #1dd1a1, #10ac84) !important;
}
/* Avg */
div[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #feca57, #ff9f43) !important;
}
/* Prediction */
div[data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
    background: linear-gradient(135deg, #54a0ff, #2e86de) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #111111 !important;
    font-weight: 800 !important;
}

[data-testid="stMetricValue"] {
    font-size: 30px !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #0f172a !important;
    color: white !important;
}

/* Inputs */
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    padding: 4px !important;
}

/* Pulse card */
.pulse-box {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border-left: 8px solid #ff6b6b;
    padding: 16px 18px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    animation: pulse 1.8s infinite;
    margin-bottom: 10px;
}
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255,107,107,0.35); }
    70% { transform: scale(1.01); box-shadow: 0 0 0 14px rgba(255,107,107,0); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255,107,107,0); }
}
.pulse-title {
    font-size: 15px;
    font-weight: 800;
    color: #111111;
}
.pulse-value {
    font-size: 24px;
    font-weight: 900;
    color: #111111;
}
.pulse-sub {
    font-size: 13px;
    color: #374151;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("enterprise_pro.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    product TEXT,
    price INTEGER,
    city TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stocks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER
)
""")
conn.commit()

# =========================================================
# DEFAULT USERS
# =========================================================
def seed_users():
    existing = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        users = [
            ("admin", "admin123", "Admin"),
            ("manager", "manager123", "Manager")
        ]
        cursor.executemany("INSERT INTO users(username,password,role) VALUES(?,?,?)", users)
        conn.commit()

seed_users()

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "last_revenue": 0,
    "last_orders": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# LOGIN
# =========================================================
if not st.session_state.logged_in:
    st.title("🔐 Enterprise Command Center PRO Login")
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("### Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            user = cursor.execute(
                "SELECT username, password, role FROM users WHERE username=?",
                (username,)
            ).fetchone()

            if user and password == user[1]:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[2]
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Control Panel")
st.sidebar.success(f"User: {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role}")

page_options = ["Revenue Dashboard", "Stock Dashboard"]
if st.session_state.role == "Admin":
    page_options.append("Admin Panel")

page = st.sidebar.selectbox("Select Dashboard", page_options)
refresh = st.sidebar.slider("Auto Refresh (sec)", 5, 60, 10)
st_autorefresh(interval=refresh * 1000, key="refresh_key")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# =========================================================
# DATA GENERATORS
# =========================================================
products = ["Laptop", "Mobile", "Tablet", "Camera", "Headphones", "Watch", "Monitor"]
cities = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]

def insert_sale():
    row = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000, 50000),
        random.choice(cities)
    )
    cursor.execute("INSERT INTO sales(time, product, price, city) VALUES(?,?,?,?)", row)
    conn.commit()

def insert_stock():
    last_close_row = cursor.execute("SELECT close FROM stocks ORDER BY id DESC LIMIT 1").fetchone()
    base = last_close_row[0] if last_close_row else 1000.0

    open_p = round(base + random.uniform(-15, 15), 2)
    high_p = round(open_p + random.uniform(5, 25), 2)
    low_p = round(open_p - random.uniform(5, 25), 2)
    close_p = round(random.uniform(low_p, high_p), 2)
    volume = random.randint(1000, 8000)

    row = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        open_p, high_p, low_p, close_p, volume
    )
    cursor.execute(
        "INSERT INTO stocks(time, open, high, low, close, volume) VALUES(?,?,?,?,?,?)",
        row
    )
    conn.commit()

insert_sale()
insert_stock()

sales_df = pd.read_sql("SELECT * FROM sales ORDER BY id ASC", conn)
stock_df = pd.read_sql("SELECT * FROM stocks ORDER BY id ASC", conn)

sales_df["time"] = pd.to_datetime(sales_df["time"])
stock_df["time"] = pd.to_datetime(stock_df["time"])

# =========================================================
# SIMPLE AI PREDICTION
# =========================================================
def predict_next_revenue(df):
    if len(df) < 3:
        return 0

    temp = df.copy()
    temp["minute"] = temp["time"].dt.floor("min")
    minute_rev = temp.groupby("minute")["price"].sum().reset_index()

    if len(minute_rev) < 2:
        return int(temp["price"].tail(5).mean())

    y = minute_rev["price"].values.astype(float)
    x = np.arange(len(y))
    coef = np.polyfit(x, y, 1)
    next_x = len(y)
    prediction = coef[0] * next_x + coef[1]
    return max(0, int(prediction))

# =========================================================
# REVENUE DASHBOARD
# =========================================================
if page == "Revenue Dashboard":
    st.title("🔥 Enterprise Revenue Dashboard")

    total_revenue = int(sales_df["price"].sum()) if not sales_df.empty else 0
    total_orders = len(sales_df)
    avg_order = int(sales_df["price"].mean()) if not sales_df.empty else 0
    next_prediction = predict_next_revenue(sales_df)

    revenue_delta = total_revenue - st.session_state.last_revenue
    orders_delta = total_orders - st.session_state.last_orders
    st.session_state.last_revenue = total_revenue
    st.session_state.last_orders = total_orders

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Revenue", f"₹{total_revenue:,}", f"{revenue_delta:+,}")
    c2.metric("📦 Total Orders", f"{total_orders:,}", f"{orders_delta:+}")
    c3.metric("📊 Avg Order Value", f"₹{avg_order:,}")
    c4.metric("🧠 Next Revenue Prediction", f"₹{next_prediction:,}")

    st.markdown(
        f"""
        <div class="pulse-box">
            <div class="pulse-title">Real-Time Pulse Alert</div>
            <div class="pulse-value">₹{revenue_delta:+,}</div>
            <div class="pulse-sub">Latest revenue movement after refresh cycle</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        city_data = sales_df.groupby("city", as_index=False)["price"].sum().sort_values("price", ascending=False)
        fig_bar = px.bar(
            city_data,
            x="city",
            y="price",
            color="city",
            color_discrete_sequence=["#ff6b6b", "#1dd1a1", "#feca57", "#54a0ff", "#ff9f43"]
        )
        fig_bar.update_layout(
            title="Revenue by City",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        product_data = sales_df.groupby("product", as_index=False)["price"].sum()
        fig_pie = px.pie(
            product_data,
            names="product",
            values="price",
            hole=0.45,
            color_discrete_sequence=["#ff6b6b", "#1dd1a1", "#feca57", "#54a0ff", "#ff9f43", "#48dbfb", "#10ac84"]
        )
        fig_pie.update_layout(
            title="Product Revenue Share",
            paper_bgcolor="white",
            font=dict(color="black")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📈 Revenue Trend")
    trend_df = sales_df.copy()
    trend_df["minute"] = trend_df["time"].dt.floor("min")
    trend = trend_df.groupby("minute", as_index=False)["price"].sum()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=trend["minute"],
        y=trend["price"],
        mode="lines+markers",
        line=dict(color="#ee5253", width=3),
        marker=dict(size=8, color="#feca57")
    ))
    fig_line.update_layout(
        title="Revenue Over Time",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        xaxis_title="Time",
        yaxis_title="Revenue"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("🟢 Live Transactions")
    st.dataframe(
        sales_df.sort_values("id", ascending=False).head(15),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Revenue Data",
        data=sales_df.to_csv(index=False),
        file_name="revenue_data.csv",
        mime="text/csv"
    )

# =========================================================
# STOCK DASHBOARD
# =========================================================
elif page == "Stock Dashboard":
    st.title("📊 Candlestick Stock Dashboard")

    latest_close = float(stock_df["close"].iloc[-1]) if not stock_df.empty else 0
    latest_open = float(stock_df["open"].iloc[-1]) if not stock_df.empty else 0
    latest_high = float(stock_df["high"].max()) if not stock_df.empty else 0
    latest_volume = int(stock_df["volume"].sum()) if not stock_df.empty else 0

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("💹 Last Close", f"₹{latest_close:,.2f}")
    s2.metric("🔔 Last Open", f"₹{latest_open:,.2f}")
    s3.metric("📈 Session High", f"₹{latest_high:,.2f}")
    s4.metric("📦 Total Volume", f"{latest_volume:,}")

    fig_candle = go.Figure(data=[go.Candlestick(
        x=stock_df["time"],
        open=stock_df["open"],
        high=stock_df["high"],
        low=stock_df["low"],
        close=stock_df["close"],
        increasing_line_color="#10ac84",
        decreasing_line_color="#ee5253"
    )])

    fig_candle.update_layout(
        title="Live Candlestick Chart",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=500
    )
    st.plotly_chart(fig_candle, use_container_width=True)

    vol_fig = px.bar(
        stock_df.tail(20),
        x="time",
        y="volume",
        color_discrete_sequence=["#54a0ff"]
    )
    vol_fig.update_layout(
        title="Recent Volume",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        showlegend=False
    )
    st.plotly_chart(vol_fig, use_container_width=True)

    st.subheader("Recent Stock Data")
    st.dataframe(stock_df.sort_values("id", ascending=False).head(15), use_container_width=True, hide_index=True)

# =========================================================
# ADMIN PANEL
# =========================================================
elif page == "Admin Panel" and st.session_state.role == "Admin":
    st.title("👥 Admin User Management")

    st.subheader("Create New User")
    a1, a2, a3 = st.columns(3)
    new_user = a1.text_input("New Username")
    new_pass = a2.text_input("New Password")
    new_role = a3.selectbox("Role", ["Admin", "Manager"])

    if st.button("Add User"):
        if new_user.strip() and new_pass.strip():
            exists = cursor.execute("SELECT username FROM users WHERE username=?", (new_user.strip(),)).fetchone()
            if exists:
                st.warning("Username already exists")
            else:
                cursor.execute(
                    "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (new_user.strip(), new_pass.strip(), new_role)
                )
                conn.commit()
                st.success("User added successfully")
                st.rerun()
        else:
            st.error("Please enter username and password")

    st.subheader("Current Users")
    users_df = pd.read_sql("SELECT username, role FROM users", conn)
    st.dataframe(users_df, use_container_width=True, hide_index=True)
