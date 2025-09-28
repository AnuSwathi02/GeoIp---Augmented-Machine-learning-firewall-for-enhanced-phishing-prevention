import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sqlite3
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="🛡️ Real-time Firewall Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for real-time monitoring
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #51cf66;
        animation: pulse-green 2s infinite;
    }
    
    .status-offline {
        background-color: #ff6b6b;
    }
    
    @keyframes pulse-green {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .alert-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        animation: pulse-red 1s infinite alternate;
    }
    
    @keyframes pulse-red {
        from { box-shadow: 0 0 10px rgba(255, 107, 107, 0.5); }
        to { box-shadow: 0 0 20px rgba(255, 107, 107, 0.9); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .threat-level-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    
    .threat-level-medium {
        background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
    }
    
    .threat-level-low {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
    }
</style>
""", unsafe_allow_html=True)

# Global variables for real-time updates
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'threat_count' not in st.session_state:
    st.session_state.threat_count = 0
if 'system_status' not in st.session_state:
    st.session_state.system_status = "online"

# Flask API base URL
API_BASE = "http://127.0.0.1:5000"

def get_system_status():
    """Check if Flask API is online"""
    try:
        response = requests.get(f"{API_BASE}/api/stats", timeout=5)
        return "online" if response.status_code == 200 else "offline"
    except:
        return "offline"

def get_real_time_stats():
    """Get real-time statistics"""
    try:
        response = requests.get(f"{API_BASE}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_recent_activity():
    """Get recent blocking activity"""
    try:
        response = requests.get(f"{API_BASE}/api/blocked_ips", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def calculate_threat_level(stats):
    """Calculate current threat level"""
    if not stats:
        return "unknown", 0
    
    currently_blocked = stats.get('currently_blocked', 0)
    
    if currently_blocked > 10:
        return "high", currently_blocked
    elif currently_blocked > 5:
        return "medium", currently_blocked
    else:
        return "low", currently_blocked

# Main header
st.markdown('<h1 class="main-header">🛡️ Real-time Firewall Monitoring Dashboard</h1>', unsafe_allow_html=True)

# Auto-refresh toggle
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)

# System status
system_status = get_system_status()
st.session_state.system_status = system_status

status_color = "🟢" if system_status == "online" else "🔴"
st.markdown(f"### {status_color} System Status: {system_status.upper()}")

if system_status == "offline":
    st.markdown("""
    <div class="alert-banner">
        <h3>⚠️ WARNING: Flask API is offline!</h3>
        <p>Please ensure the Flask server is running on port 5000</p>
    </div>
    """, unsafe_allow_html=True)

# Get current statistics
stats = get_real_time_stats()
recent_activity = get_recent_activity()

if stats:
    # Threat level assessment
    threat_level, threat_count = calculate_threat_level(stats)
    st.session_state.threat_count = threat_count
    
    # Threat level indicator
    threat_colors = {
        "high": "🔴",
        "medium": "🟡", 
        "low": "🟢",
        "unknown": "⚪"
    }
    
    st.markdown(f"### {threat_colors.get(threat_level, '⚪')} Current Threat Level: {threat_level.upper()}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total_blocked']}</h2>
            <p>Total Blocked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        threat_class = f"threat-level-{threat_level}"
        st.markdown(f"""
        <div class="metric-card {threat_class}">
            <h2>{stats['currently_blocked']}</h2>
            <p>Currently Blocked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if stats['country_stats']:
            top_country = stats['country_stats'][0]
            st.markdown(f"""
            <div class="metric-card">
                <h2>{top_country['count']}</h2>
                <p>From {top_country['country']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h2>0</h2>
                <p>No Country Data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(recent_activity)}</h2>
            <p>Recent Events</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Geographic Threat Distribution")
        if stats['country_stats']:
            country_df = pd.DataFrame(stats['country_stats'])
            
            fig = px.pie(
                country_df,
                values='count',
                names='country',
                title="Blocked IPs by Country",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic data available")
    
    with col2:
        st.subheader("📈 Threat Level Timeline")
        # Simulate timeline data (in real implementation, this would come from historical data)
        timeline_data = {
            'time': [datetime.now() - timedelta(minutes=i*5) for i in range(12, 0, -1)],
            'threats': [max(0, threat_count + (i % 3) - 1) for i in range(12, 0, -1)]
        }
        
        timeline_df = pd.DataFrame(timeline_data)
        
        fig = px.line(
            timeline_df,
            x='time',
            y='threats',
            title="Threat Level Over Time",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Active Threats"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity feed
    st.subheader("🕒 Real-time Activity Feed")
    
    if recent_activity:
        # Create DataFrame for recent activity
        activity_df = pd.DataFrame(recent_activity)
        activity_df['blocked_at'] = pd.to_datetime(activity_df['blocked_at'])
        activity_df = activity_df.sort_values('blocked_at', ascending=False)
        
        # Show last 10 activities
        recent_df = activity_df.head(10)
        
        for _, row in recent_df.iterrows():
            status_icon = "🚫" if pd.isna(row['unblocked_at']) else "✅"
            time_ago = datetime.now() - row['blocked_at']
            
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"**{row['ip_address']}**")
            with col2:
                st.write(f"{row['country'] or 'Unknown'}")
            with col3:
                st.write(f"{time_ago.total_seconds()/60:.0f} min ago")
            with col4:
                st.write(f"{status_icon}")
            
            st.divider()
    else:
        st.info("No recent activity to display")
    
    # System performance metrics
    st.subheader("⚡ System Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Simulate response time
        response_time = 45 + (threat_count * 2)  # Simulate load-based response time
        st.metric("API Response Time", f"{response_time}ms")
    
    with col2:
        # Simulate CPU usage
        cpu_usage = min(100, 20 + (threat_count * 5))
        st.metric("System Load", f"{cpu_usage}%")
    
    with col3:
        # Database status
        db_status = "🟢 Healthy" if len(recent_activity) < 1000 else "🟡 Warning"
        st.metric("Database Status", db_status)
    
    # Alerts and notifications
    if threat_level == "high":
        st.markdown("""
        <div class="alert-banner">
            <h3>🚨 HIGH THREAT LEVEL DETECTED!</h3>
            <p>Multiple IP addresses are currently blocked. Consider reviewing firewall rules.</p>
        </div>
        """, unsafe_allow_html=True)
    elif threat_level == "medium":
        st.warning("⚠️ Medium threat level detected. Monitor system closely.")
    
    # Last update timestamp
    st.session_state.last_update = datetime.now()
    st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

else:
    st.error("❌ Unable to load monitoring data. Please check the Flask API connection.")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🛡️ Real-time Firewall Monitoring Dashboard</p>
    <p>Live threat detection and system monitoring</p>
</div>
""", unsafe_allow_html=True)
