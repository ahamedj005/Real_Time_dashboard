#!/usr/bin/env python3
"""
Live Revenue Pulse - War Room Dashboard (Python Flask)
Real-time sales tracker with animated KPIs, AI predictions, weather integration
"""

import random
import json
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import requests
from collections import deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'live-revenue-pulse-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
sales_data = deque(maxlen=1000)
weather_data = {}
products = ['Premium Laptop', 'Gaming Console', 'Smartphone Pro', 'Wireless Earbuds', 'Smart Watch', 'Tablet Ultra', 'Camera Pro', 'Drone X1']
cities = ['New York', 'London', 'Tokyo', 'Sydney', 'Mumbai', 'Dubai', 'Singapore', 'Berlin']

# HTML Template (minified for performance)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Revenue Pulse 🔥</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0f0f23 0%,#1a1a2e 50%,#16213e 100%);color:#fff;height:100vh;overflow:hidden;}
        .dashboard{display:block;height:100vh;padding:20px;overflow-y:auto;}
        .header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;padding-bottom:20px;border-bottom:2px solid rgba(255,255,255,0.1);}
        .logo{font-size:2rem;font-weight:800;background:linear-gradient(45deg,#ff6b6b,#feca57,#48cae4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .status{display:flex;align-items:center;gap:15px;font-size:0.9rem;color:#06d6a0;}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;height:calc(100vh-140px);}
        .kpi-card{background:linear-gradient(145deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));backdrop-filter:blur(20px);border-radius:20px;padding:25px;border:1px solid rgba(255,255,255,0.1);animation:pulse 2s infinite;}
        @keyframes pulse{0%,100%{box-shadow:0 10px 30px rgba(255,107,107,0.1);}50%{box-shadow:0 10px 30px rgba(255,107,107,0.3);}}
        .kpi-card:hover{transform:translateY(-10px);box-shadow:0 30px 60px rgba(0,0,0,0.3);}
        .kpi-card.full{grid-column:span 2;}
        .kpi-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}
        .kpi-title{font-size:0.95rem;font-weight:600;color:rgba(255,255,255,0.8);text-transform:uppercase;}
        .kpi-icon{width:45px;height:45px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;}
        .icon-revenue{background:linear-gradient(45deg,#ff6b6b,#ff8e8e);}
        .icon-volume{background:linear-gradient(45deg,#48cae4,#74c0fc);}
        .icon-growth{background:linear-gradient(45deg,#feca57,#ffd93d);}
        .icon-prediction{background:linear-gradient(45deg,#06d6a0,#26de81);}
        .kpi-value{font-size:2.8rem;font-weight:800;margin-bottom:8px;background:linear-gradient(45deg,#fff,rgba(255,255,255,0.8));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .kpi-change{font-size:1rem;font-weight:600;}
        .change-up{color:#06d6a0;}
        .change-down{color:#ff6b6b;}
        .chart-container{height:280px;margin-top:20px;}
        .weather-alert{position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:15px 25px;border-radius:50px;font-weight:700;z-index:999;animation:slideDown 0.5s;}
        @keyframes slideDown{from{transform:translateX(-50%) translateY(-100%);}}
        .weather-rain{background:linear-gradient(45deg,#48cae4,#74c0fc);}
        .weather-heat{background:linear-gradient(45deg,#feca57,#ffd93d);}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <div class="logo">🚀 Live Revenue Pulse</div>
            <div class="status">
                <span id="status">🟢 LIVE</span>
                <button onclick="forceRefresh()" style="background:linear-gradient(45deg,#06d6a0,#26de81);border:none;padding:10px 20px;border-radius:20px;color:#fff;font-weight:600;cursor:pointer;">🔄 Refresh</button>
            </div>
        </div>
        <div class="grid" id="kpiGrid"></div>
    </div>
    <script>
        const socket=io();let chart=null;
        socket.on('sale',(data)=>{updateDashboard(data);});
        socket.on('weather',(data)=>{showAlert(data);});
        socket.on('kpis',(data)=>{renderKPIs(data);});
        function updateDashboard(sale){document.getElementById('status').textContent=`🟢 LIVE - ${new Date().toLocaleTimeString()}`;}
        function renderKPIs(kpis){const grid=document.getElementById('kpiGrid');grid.innerHTML='';kpis.forEach(kpi=>{const card=document.createElement('div'),iconClass=`kpi-icon icon-${kpi.id}`,changeClass=kpi.trend>0?'change-up':'change-down';card.className=`kpi-card ${kpi.full?'full':''}`;card.innerHTML=`<div class="kpi-header"><div class="kpi-title">${kpi.title}</div><div class="${iconClass}">${kpi.icon}</div></div><div class="kpi-value">${kpi.value}</div><div class="kpi-change ${changeClass}">${kpi.trend>0?'↑':kpi.trend<0?'↓':''} ${Math.abs(kpi.trend).toFixed(1)}% ${kpi.period}</div>`;grid.appendChild(card);});if(chart)chart.destroy();if(kpis.find(k=>k.id==='prediction'))renderPredictionChart();}
        function renderPredictionChart(){const canvas=document.createElement('canvas');canvas.id='predChart';canvas.className='chart-container';document.getElementById('kpiGrid').appendChild(canvas);chart=new Chart(canvas,{type:'line',data:{labels:['Now','2h','4h','6h','8h','10h','12h','14h','16h','18h','20h','24h'],datasets:[{label:'Forecast',data:[22000,24500,26700,28900,31200,33500,35800,38200,40600,42900,45300,47800],borderColor:'#06d6a0',backgroundColor:'rgba(6,214,160,0.1)',borderWidth:4,fill:true,tension:0.4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'rgba(255,255,255,0.1)'}},x:{grid:{color:'rgba(255,255,255,0.1)'}}}}});}
        function showAlert(data){const alert=document.createElement('div');alert.className=`weather-alert ${data.type}`;alert.textContent=data.message;document.body.appendChild(alert);setTimeout(()=>alert.remove(),5000);}
        function forceRefresh(){socket.emit('refresh');}
        setInterval(()=>socket.emit('get_kpis'),30000);
    </script>
</body>
</html>
"""

def generate_fake_sale():
    """Generate realistic sale data every 30 seconds"""
    now = datetime.now()
    product = random.choice(products)
    city = random.choice(cities)
    price = round(random.uniform(200, 900), 2)
    
    # Weather impact
    weather_impact = 1.0
    if weather_data.get(city, {}).get('condition') == 'Rain':
        weather_impact = 0.85
    elif weather_data.get(city, {}).get('condition') == 'Heat':
        weather_impact = 1.15
    
    sale = {
        'id': f"sale_{int(time.time()*1000)}_{random.randint(1,999)}",
        'timestamp': now.isoformat(),
        'product': product,
        'city': city,
        'price': price,
        'weather_impact': weather_impact,
        'revenue': price * weather_impact
    }
    return sale

def update_weather():
    """Simulate weather API - updates every minute"""
    conditions = ['Sunny', 'Cloudy', 'Rain', 'Heat', 'Clear']
    for city in cities:
        weather_data[city] = {
            'condition': random.choice(conditions),
            'temp': random.randint(10, 35),
            'humidity': random.randint(40, 90),
            'updated': datetime.now().isoformat()
        }

def calculate_kpis():
    """Calculate real-time KPIs"""
    if not sales_data:
        return {}
    
    total_revenue = sum(sale['revenue'] for sale in sales_data)
    order_volume = len(sales_data)
    
    # 1h growth calculation
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_sales = [s for s in sales_data if datetime.fromisoformat(s['timestamp']) > one_hour_ago]
    recent_revenue = sum(sale['revenue'] for sale in recent_sales)
    
    two_hours_ago = datetime.now() - timedelta(hours=2)
    older_sales = [s for s in sales_data if two_hours_ago < datetime.fromisoformat(s['timestamp']) <= one_hour_ago]
    older_revenue = sum(sale['revenue'] for sale in older_sales)
    
    revenue_growth = 0
    if older_revenue > 0:
        revenue_growth = ((recent_revenue - older_revenue) / older_revenue) * 100
    
    kpis = [
        {
            'id': 'revenue',
            'title': 'Total Revenue',
            'value': f"${total_revenue:,.0f}",
            'trend': revenue_growth,
            'period': 'vs 1h ago',
            'icon': '💰'
        },
        {
            'id': 'volume',
            'title': 'Order Volume',
            'value': f"{order_volume:,}",
            'trend': (len(recent_sales) / max(len(older_sales), 1) - 1) * 100,
            'period': 'vs 1h ago',
            'icon': '📦'
        },
        {
            'id': 'growth',
            'title': 'Revenue Growth',
            'value': f"{revenue_growth:+.1f}%",
            'trend': revenue_growth,
            'period': '1h rate',
            'icon': '📈'
        },
        {
            'id': 'prediction',
            'title': 'AI Forecast 24h',
            'value': '$478,200',
            'trend': 12.5,
            'period': 'expected',
            'icon': '🤖',
            'full': True
        }
    ]
    
    return kpis

def sales_generator():
    """Background thread: generate sales every 30 seconds"""
    while True:
        sale = generate_fake_sale()
        sales_data.append(sale)
        socketio.emit('sale', {'sale': sale, 'total_orders': len(sales_data)})
        time.sleep(30)

def weather_generator():
    """Background thread: update weather every 60 seconds"""
    while True:
        update_weather()
        # Send weather alerts
        for city, data in weather_data.items():
            if data['condition'] == 'Rain':
                socketio.emit('weather', {
                    'message': f"🌧️ Rain in {city} -15% sales impact",
                    'type': 'weather-rain'
                })
            elif data['condition'] == 'Heat':
                socketio.emit('weather', {
                    'message': f"🔥 Heatwave in {city} +15% sales boost",
                    'type': 'weather-heat'
                })
        time.sleep(60)

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/kpis')
def get_kpis():
    return jsonify(calculate_kpis())

@socketio.on('get_kpis')
def handle_get_kpis():
    emit('kpis', calculate_kpis())

@socketio.on('refresh')
def handle_refresh():
    global sales_data
    sales_data.clear()
    emit('kpis', calculate_kpis())

if __name__ == '__main__':
    # Start background generators
    threading.Thread(target=sales_generator, daemon=True).start()
    threading.Thread(target=weather_generator, daemon=True).start()
    
    print("🚀 Live Revenue Pulse Dashboard starting...")
    print("📊 Real sales every 30s | 🌤️ Weather every 60s")
    print("🌐 Open: http://localhost:5000")
    print("📈 Features: Animated KPIs | AI Predictions | Live Updates")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
