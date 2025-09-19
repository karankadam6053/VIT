import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import cv2
from datetime import datetime, timedelta
import random
import time

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="FireWatch AI - Flame & Smoke Detection",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# CUSTOM CSS
# =====================
st.markdown("""
<style>
    /* Main styling */
    .main { background-color: #0e1117; color: #fafafa; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1d29 100%); }
    
    /* Sidebar styling */
    .css-1d391kg { background-color: #131721; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #131721 0%, #1a1f2e 100%);
        border-right: 1px solid #2a2f3c;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #ff4b4b, #ff7b25);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 800;
        text-shadow: 0px 2px 10px rgba(255, 75, 75, 0.3);
    }
    .sub-header {
        font-size: 1.6rem;
        color: #ffa64b;
        margin-bottom: 1.2rem;
        font-weight: 700;
        border-left: 4px solid #ff4b4b;
        padding-left: 12px;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(145deg, #1a1f2e, #21283b);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border: 1px solid #2a2f3c;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.3);
    }
    
    .status-card {
        background: rgba(26, 31, 46, 0.7);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #ff4b4b;
        backdrop-filter: blur(5px);
    }
    
    /* Risk indicators */
    .risk-critical { color: #ff4b4b; font-weight: bold; }
    .risk-high { color: #ff8c42; font-weight: bold; }
    .risk-medium { color: #ffdd4b; font-weight: bold; }
    .risk-low { color: #4bff4b; font-weight: bold; }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        background: linear-gradient(45deg, #ff4b4b, #ff7b25);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
    }
    
    /* Sidebar elements */
    .sidebar-title {
        font-size: 1.8rem;
        background: linear-gradient(45deg, #ff4b4b, #ff7b25);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 2rem;
        text-align: center;
    }
    .sidebar-section {
        background: rgba(26, 31, 46, 0.5);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #2a2f3c;
    }
    
    /* Progress bars */
    .progress-container {
        background-color: #1a1f2e;
        border-radius: 10px;
        height: 8px;
        margin: 10px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(45deg, #ff4b4b, #ff7b25);
    }
    
    /* Camera feed */
    .camera-feed {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        border: 2px solid #2a2f3c;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# SESSION STATE
# =====================
if 'detections' not in st.session_state:
    st.session_state.detections = []

if 'alerts' not in st.session_state:
    st.session_state.alerts = [
        {'id':1,'type':'FIRE','location':'Warehouse A','confidence':91,'timestamp':datetime.now()-timedelta(minutes=20),'critical':True},
        {'id':2,'type':'FIRE','location':'Server Room','confidence':89,'timestamp':datetime.now()-timedelta(minutes=15),'critical':False},
        {'id':3,'type':'SMOKE','location':'Lab Area','confidence':78,'timestamp':datetime.now()-timedelta(minutes=5),'critical':True}
    ]

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

if 'camera' not in st.session_state:
    st.session_state.camera = None

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown('<p class="sidebar-title">🔥 FireWatch AI</p>', unsafe_allow_html=True)
    
    # System Status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("System Status")
    
    # Status indicators
    col1, col2 = st.columns(2)
    with col1:
        st.success("AI Engine ✅")
        st.success("Cameras ✅")
    with col2:
        st.error("Alert System ❌")
        st.warning("Storage 78%")
    
    # Uptime
    st.markdown("**Uptime:** 14 days, 6 hrs")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("Navigation")
    nav_options = ["Dashboard", "Camera Feeds", "Analytics", "Alerts", "System Settings"]
    selected_nav = st.radio("Go to", nav_options, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Alert Preferences
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("Alert Preferences")
    sms_alerts = st.checkbox("SMS Notifications", value=True)
    email_alerts = st.checkbox("Email Alerts", value=True)
    audio_warnings = st.checkbox("Audio Warnings", value=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("Quick Actions")
    if st.button("🚨 Emergency Alert", use_container_width=True):
        st.session_state.alerts.append({
            'id': len(st.session_state.alerts) + 1,
            'type': 'EMERGENCY',
            'location': 'Manual Trigger',
            'confidence': 100,
            'timestamp': datetime.now(),
            'critical': True
        })
        st.success("Emergency alert triggered!")
    
    if st.button("🔄 Refresh System", use_container_width=True):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem;'>FireWatch AI v2.1<br>© 2024 FireSafe Technologies</p>", unsafe_allow_html=True)

# =====================
# DASHBOARD
# =====================
if selected_nav == "Dashboard":
    st.markdown('<h1 class="main-header">AI Flame & Smoke Detection</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#aaa; margin-bottom: 2rem;">Real-time fire & smoke monitoring system</p>', unsafe_allow_html=True)
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Overall Risk", "CRITICAL", delta=None, delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Detections", len(st.session_state.alerts), delta="+2", delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Response Time", "2.3s", delta="-0.4s", delta_color="normal")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Accuracy", "99.2%", delta="+0.2%", delta_color="normal")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main Content Area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Risk Analysis
        st.markdown('<h2 class="sub-header">AI Analysis</h2>', unsafe_allow_html=True)
        
        # Predictive Risk Model
        st.markdown("##### Predictive Risk Model")
        risk_factors = {
            'Factor': ['Smoke Density', 'Spread Velocity', 'Wind Factor', 'Heat Signature'],
            'Level': [95, 85, 60, 92],
            'Status': ['Critical', 'High', 'Moderate', 'Critical']
        }
        
        for i, factor in enumerate(risk_factors['Factor']):
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([2, 1, 2])
            with col_a:
                st.write(f"**{factor}**")
            with col_b:
                status_class = f"risk-{risk_factors['Status'][i].lower()}"
                st.markdown(f'<span class="{status_class}">{risk_factors["Status"][i]}</span>', unsafe_allow_html=True)
            with col_c:
                st.markdown(f'<div class="progress-container"><div class="progress-fill" style="width: {risk_factors["Level"][i]}%;"></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Alerts
        st.markdown("##### Recent Alerts")
        for alert in st.session_state.alerts[::-1]:
            card_color = "#ff4b4b20" if alert['critical'] else "#44444420"
            st.markdown(f'<div class="status-card" style="background-color:{card_color};">', unsafe_allow_html=True)
            st.write(f"**{alert['type']} detected at {alert['location']}**")
            st.write(f"Confidence: {alert['confidence']}% | Time: {alert['timestamp'].strftime('%H:%M:%S')}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Environmental Data
        st.markdown('<h2 class="sub-header">Environmental Data</h2>', unsafe_allow_html=True)
        
        # Environment metrics
        env_metrics = {
            'Temperature': {'value': '32°C', 'status': 'High'},
            'Humidity': {'value': '45%', 'status': 'Normal'},
            'Air Quality': {'value': 'Moderate', 'status': 'Moderate'},
            'Lighting': {'value': 'Optimal', 'status': 'Optimal'}
        }
        
        for metric, data in env_metrics.items():
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**{metric}**")
            with col_b:
                status_class = f"risk-{data['status'].lower()}"
                st.markdown(f'<span class="{status_class}">{data["value"]}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Confidence Gauge
        st.markdown("##### AI Confidence Level")
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 99.8,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Confidence Score"},
            delta = {'reference': 98.5},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#ff4b4b"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 90], 'color': "gray"},
                    {'range': [90, 100], 'color': "#ff4b4b"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 99.8
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# =====================
# CAMERA FEEDS
# =====================
elif selected_nav == "Camera Feeds":
    st.markdown('<h1 class="main-header">Live Camera Feeds</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📱 Mobile Camera Stream")
        mobile_url = st.text_input("Enter Mobile Stream URL", "http://192.168.1.5:8080/video")
        start_mobile = st.checkbox("Start Mobile Camera", value=False)
        mobile_placeholder = st.empty()
        
        if start_mobile:
            cap_mobile = cv2.VideoCapture(mobile_url)
            if not cap_mobile.isOpened(): 
                st.error("Cannot access mobile stream")
            else:
                while start_mobile:
                    ret, frame = cap_mobile.read()
                    if not ret: break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mobile_placeholder.image(frame, channels="RGB", use_column_width=True)
    
    with col2:
        st.markdown("#### 💻 Laptop Camera")
        run_webcam = st.checkbox("Start Laptop Camera", value=st.session_state.camera_active)
        frame_placeholder = st.empty()
        
        if run_webcam:
            st.session_state.camera_active = True
            if st.session_state.camera is None:
                st.session_state.camera = cv2.VideoCapture(0)
            
            if not st.session_state.camera.isOpened(): 
                st.error("Cannot access laptop camera")
            else:
                while run_webcam and st.session_state.camera_active:
                    ret, frame = st.session_state.camera.read()
                    if not ret: break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Simulate detection overlay
                    if random.random() > 0.8:  # Randomly add detection markers
                        h, w, _ = frame.shape
                        cv2.rectangle(frame, (w//4, h//4), (w//4+100, h//4+100), (255, 0, 0), 3)
                        cv2.putText(frame, "FIRE DETECTED", (w//4, h//4-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    
                    frame_placeholder.image(frame, channels="RGB", use_column_width=True)
                    time.sleep(0.1)  # Control frame rate
        else:
            st.session_state.camera_active = False
            if st.session_state.camera:
                st.session_state.camera.release()
                st.session_state.camera = None

# =====================
# ANALYTICS
# =====================
elif selected_nav == "Analytics":
    st.markdown('<h1 class="main-header">Detection Analytics</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Real-time Detection Confidence")
        data = []
        for i in range(30):
            new_point = {"time": (datetime.now() - timedelta(seconds=30-i)).strftime("%H:%M:%S"), 
                         "confidence": random.randint(70, 99)}
            data.append(new_point)
        
        df = pd.DataFrame(data)
        fig = px.line(df, x="time", y="confidence", title="Live Detection Confidence", 
                      range_y=[0, 100], line_shape="spline")
        fig.update_traces(line=dict(color='#ff4b4b', width=3))
        fig.add_hrect(y0=85, y1=100, line_width=0, fillcolor="red", opacity=0.2)
        fig.add_hrect(y0=70, y1=85, line_width=0, fillcolor="orange", opacity=0.2)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Detection Type Distribution")
        detection_types = ['Fire', 'Smoke', 'Heat', 'Motion']
        counts = [45, 32, 15, 8]
        fig = px.pie(values=counts, names=detection_types, title="Detection Types",
                     color_discrete_sequence=['#ff4b4b', '#ff8c42', '#ffdd4b', '#4bff4b'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical data
    st.markdown("#### Historical Detection Trends")
    dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
    values = np.random.randint(0, 20, size=len(dates)) + np.sin(np.arange(len(dates)) * 0.1) * 5 + 10
    df_hist = pd.DataFrame({'Date': dates, 'Detections': values})
    fig = px.area(df_hist, x='Date', y='Detections', title="Daily Detections Over Time")
    st.plotly_chart(fig, use_container_width=True)

# =====================
# ALERTS
# =====================
elif selected_nav == "Alerts":
    st.markdown('<h1 class="main-header">Active Alerts</h1>', unsafe_allow_html=True)
    
    for alert in st.session_state.alerts[::-1]:
        if alert['critical']:
            st.markdown('<div style="background-color: #ff4b4b20; padding: 1.5rem; border-radius: 12px; border-left: 6px solid #ff4b4b; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('**🚨 CRITICAL ALERT**')
        else:
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if alert['type'] == 'FIRE':
                st.markdown(f"**🔥 {alert['type']} DETECTED**")
            else:
                st.markdown(f"**💨 {alert['type']} DETECTED**")
            
            st.write(f"Location: **{alert['location']}**")
            st.write(f"Time: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.markdown(f"**{alert['confidence']}%**")
            if st.button("Acknowledge", key=f"alert_{alert['id']}"):
                st.session_state.alerts = [a for a in st.session_state.alerts if a['id'] != alert['id']]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# =====================
# SYSTEM SETTINGS
# =====================
elif selected_nav == "System Settings":
    st.markdown('<h1 class="main-header">System Settings</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Detection Sensitivity")
        sensitivity = st.slider("AI Detection Sensitivity", 1, 100, 85)
        
        st.markdown("#### Alert Thresholds")
        fire_threshold = st.slider("Fire Confidence Threshold (%)", 70, 99, 85)
        smoke_threshold = st.slider("Smoke Confidence Threshold (%)", 60, 95, 75)
    
    with col2:
        st.markdown("#### Notification Channels")
        notif_col1, notif_col2 = st.columns(2)
        with notif_col1:
            st.checkbox("Email Notifications", value=True)
            st.checkbox("SMS Alerts", value=True)
        with notif_col2:
            st.checkbox("Browser Notifications", value=True)
            st.checkbox("Audio Alarms", value=True)
        
        st.markdown("#### System Maintenance")
        if st.button("Run System Diagnostics", use_container_width=True):
            st.success("System diagnostics completed successfully!")
        
        if st.button("Reset System", type="secondary", use_container_width=True):
            st.warning("Are you sure you want to reset the system?")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>FireWatch AI Detection System | Real-time Monitoring</p>", unsafe_allow_html=True)