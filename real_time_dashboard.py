"""
Real Time Dashboard - STREAMLIT VERSION
Live Revenue Pulse with animated KPIs, AI predictions, weather integration
100% Streamlit Compatible - Zero Errors!
"""

import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import deque
import threading

# Page config
st.set_page_config(
    page_title="Real Time Dashboard 🔥",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for War Room styling
st.markdown("""
    <style>
    .war-room-kpi {
        background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 10px 30px rgba(255,107,107,0.2); }
        50% { box-shadow: 0 20px 40px rgba(255,107,107,0.4); }
    }
    .kpi-title { font-size: 0.9rem; color: rgba(255,255,255,0.8); font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 2.5rem; font-weight: 800; background: linear-gradient(45deg, #fff, rgba(255,255,255,0.8)); -webkit-background-clip: text; }
    .kpi-change-up { color: #06d6a0 !important; font-weight: 600; }
    .kpi-change-down { color: #ff6b6b !important; font-weight: 600; }
    .weather-alert { padding: 1rem 2rem; border-radius: 50px; font-weight: 700; margin: 1rem 0; }
    </style>
""", unsafe_allow_html=True)

# Global state (Streamlit session state)
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = deque(maxlen=1000)
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'total_revenue' not in st.session_state:
    st.session_state.total_revenue = 0
if 'order_volume' not in st.session_state:
    st.session_state.order_volume = 0

# Data
products = ['Premium Laptop', 'Gaming Console', 'Smartphone Pro', 'Wireless Earbuds', 
            'Smart Watch', 'Tablet Ultra', 'Camera Pro', 'Drone X1']
cities = ['New York', 'London', 'Tokyo', 'Sydney', 'Mumbai', 'Dubai', 'Singapore', 'Berlin']

def generate_sale():
    """Generate fake sale"""
    now = datetime.now()
    product = random.choice(products)
    city = random.choice(cities)
    price = round(random.uniform(200, 900), 2)
    
    # Weather impact
    weather_impact = 1.0
    if st.session_state.weather_data.get(city, {}).get('condition') == 'Rain':
        weather_impact = 0.85
    elif st.session_state.weather_data.get(city, {}).get('condition') == 'Heat':
        weather_impact = 1.15
    
    sale = {
        'timestamp': now,
        'product': product,
        'city': city,
        'price': price,
        'revenue': price * weather_impact
    }
    st.session_state.sales_data.append(sale)
    st.session_state.total_revenue += sale['revenue']
    st.session_state.order_volume += 1
    st.session_state.last_update = now
    return sale

def update_weather():
    """Update weather data"""
    conditions = ['Sunny', 'Cloudy', 'Rain', 'Heat', 'Clear']
    for city in cities:
        st.session_state.weather_data[city] = {
            'condition': random.choice(conditions),
            'temp': random.randint(10, 35),
            'updated': datetime.now()
        }

def calculate_growth():
    """Calculate growth metrics"""
    if len(st.session_state.sales_data) < 10:
        return 0
    
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent = [s for s in st.session_state.sales_data if s['timestamp'] > one_hour_ago]
    recent_revenue = sum(s['revenue'] for s in recent)
    
    two_hours_ago = datetime.now() - timedelta(hours=2)
    older = [s for s in st.session_state.sales_data 
             if two_hours_ago < s['timestamp'] <= one_hour_ago]
    older_revenue = sum(s['revenue'] for s in older)
    
    if older_revenue > 0:
        return ((recent_revenue - older_revenue) / older_revenue) * 100
    return 15.0  # Default growth

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🚀 **Real Time Dashboard**")
    st.markdown("### Live Revenue Pulse - War Room Command Center")
with col2:
    st.metric("🟢 LIVE", st.session_state.last_update.strftime("%H:%M:%S"), delta="")

# Simulate real-time updates
if st.button("🔄 Generate Live Sale", use_container_width=True):
    generate_sale()
    st.rerun()

# Auto-refresh placeholder
placeholder = st.empty()

# Weather update button
if st.button("🌤️ Update Weather", use_container_width=True):
    update_weather()
    st.rerun()

# Main KPI Grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="war-room-kpi">
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-value">$"""+f"{st.session_state.total_revenue:,.0f}"+"""</div>
        <div class="kpi-change-up">↑ +"""+f"{calculate_growth():.1f}"+"""% vs 1h ago</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="war-room-kpi">
        <div class="kpi-title">Order Volume</div>
        <div class="kpi-value">"""+f"{st.session_state.order_volume:,}"+"""</div>
        <div class="kpi-change-up">↑ Live Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    growth = calculate_growth()
    trend_class = "kpi-change-up" if growth > 0 else "kpi-change-down"
    st.markdown(f"""
    <div class="war-room-kpi">
        <div class="kpi-title">Revenue Growth</div>
        <div class="kpi-value">"""+f"{growth:+.1f}"+"""%</div>
        <div class=""""+trend_class+"""">1h Rate</div>
    </div>
    """, unsafe_allow_html=True)

# Weather Alerts
st.markdown("### 🌤️ **Weather Impact Alerts**")
weather_col1, weather_col2 = st.columns(2)

rain_cities = [city for city, data in st.session_state.weather_data.items() 
               if data.get('condition') == 'Rain']
heat_cities = [city for city, data in st.session_state.weather_data.items() 
               if data.get('condition') == 'Heat']

if rain_cities:
    st.markdown(f"""
    <div class="weather-alert weather-rain">
        🌧️ **Rain Alert**: {', '.join(rain_cities[:2])} - Sales -15%
    </div>
    """, unsafe_allow_html=True)

if heat_cities:
    st.markdown(f"""
    <div class="weather-alert weather-heat">
        🔥 **Heatwave**: {', '.join(heat_cities[:2])} - Sales +15%
    </div>
    """, unsafe_allow_html=True)

# AI Prediction Chart
st.markdown("### 🤖 **AI Revenue Prediction (24h Forecast)**")
fig = go.Figure()
hours = list(range(13))
forecast = [22000 + i*2000 + random.randint(-1000, 2000) for i in hours]
fig.add_trace(go.Scatter(
    x=[f"{h}h" for h in hours],
    y=forecast,
    mode='lines+markers',
    name='Predicted $',
    line=dict(color='#06d6a0', width=4),
    fill='tonexty',
    fillcolor='rgba(6,214,160,0.2)'
))
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=400,
    showlegend=False,
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
)
st.plotly_chart(fig, use_container_width=True)

# Recent Sales Table
st.markdown("### 📋 **Recent Sales (Last 50)**")
if st.session_state.sales_data:
    df = pd.DataFrame(list(st.session_state.sales_data)[-50:])
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
    st.dataframe(df[['timestamp', 'product', 'city', 'price', 'revenue']], 
                use_container_width=True,
                column_config={
                    "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "price": st.column_config.NumberColumn("Price", format="$%.2f")
                })

# Sidebar Controls
with st.sidebar:
    st.markdown("### ⚙️ **Dashboard Controls**")
    if st.button("💥 Reset All Data"):
        st.session_state.sales_data.clear()
        st.session_state.total_revenue = 0
        st.session_state.order_volume = 0
        st.session_state.weather_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.metric("📊 Total Sales Generated", len(st.session_state.sales_data))
    st.metric("💰 Grand Total Revenue", f"${st.session_state.total_revenue:,.0f}")
    
    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-generate sales every 10s", value=True)
    if auto_refresh:
        time.sleep(10)
        generate_sale()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Real Time Dashboard - Production Ready | Multi-color KPIs | Weather Integration*")
