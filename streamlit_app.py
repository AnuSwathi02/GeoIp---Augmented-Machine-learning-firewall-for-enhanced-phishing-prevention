import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="🔐 GeoIP-Augmented ML Firewall",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .phishing-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .safe-alert {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #00c6ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🔐 GeoIP-Augmented ML Firewall for Phishing Prevention</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛡️ Navigation")
page = st.sidebar.selectbox("Choose a page", ["URL Scanner", "Admin Dashboard", "Statistics"])

# Flask API base URL
API_BASE = "http://127.0.0.1:5000"

def check_url_api(url):
    """Check URL using Flask API"""
    try:
        response = requests.post(f"{API_BASE}/check_url", json={"url": url})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "API request failed"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask API. Please ensure the Flask server is running on port 5000."}
    except Exception as e:
        return {"error": str(e)}

def get_stats_api():
    """Get statistics from Flask API"""
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def get_blocked_ips_api():
    """Get blocked IPs from Flask API"""
    try:
        response = requests.get(f"{API_BASE}/api/blocked_ips")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

def unblock_ip_api(ip_address):
    """Unblock IP using Flask API"""
    try:
        response = requests.post(f"{API_BASE}/api/unblock_ip", json={"ip_address": ip_address})
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": "API request failed"}
    except:
        return {"success": False, "error": "Connection error"}

# URL Scanner Page
if page == "URL Scanner":
    st.header("🔎 Real-Time URL Scanner")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url_input = st.text_input(
            "Enter URL to scan:",
            placeholder="https://example.com",
            help="Enter a URL to check for phishing threats"
        )
        
        if st.button("🔍 Scan URL", type="primary"):
            if url_input:
                with st.spinner("Scanning URL..."):
                    result = check_url_api(url_input)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Display results
                    if result['mlResult'] == 'phishing':
                        st.markdown(f"""
                        <div class="phishing-alert">
                            <h2>🚨 PHISHING DETECTED!</h2>
                            <p><strong>URL:</strong> {result['url']}</p>
                            <p><strong>IP Address:</strong> {result.get('url_ip', 'Unknown')}</p>
                            <p><strong>Country:</strong> {result.get('country', 'Unknown')}</p>
                            {f"<p><strong>🛡️ IP Address has been automatically blocked!</strong></p>" if result.get('blocked') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if result.get('url_ip'):
                            st.warning(f"⚠️ IP Address {result['url_ip']} has been blocked by the firewall!")
                    else:
                        st.markdown(f"""
                        <div class="safe-alert">
                            <h2>✅ URL IS SAFE</h2>
                            <p><strong>URL:</strong> {result['url']}</p>
                            <p><strong>IP Address:</strong> {result.get('url_ip', 'Unknown')}</p>
                            <p><strong>Country:</strong> {result.get('country', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # GeoIP warning
                    if result.get('geoFlagged'):
                        st.warning("⚠️ Alert: The URL originates from a flagged country.")
                    else:
                        st.success("🟢 Country origin appears safe.")
            else:
                st.warning("Please enter a URL to scan.")
    
    with col2:
        st.subheader("📊 Quick Stats")
        stats = get_stats_api()
        if stats:
            st.metric("Total Blocked", stats['total_blocked'])
            st.metric("Currently Blocked", stats['currently_blocked'])
            if stats['country_stats']:
                top_country = stats['country_stats'][0]
                st.metric("Top Threat Country", f"{top_country['country']} ({top_country['count']})")
        else:
            st.info("Stats unavailable - ensure Flask API is running")

# Admin Dashboard Page
elif page == "Admin Dashboard":
    st.header("🛡️ Admin Dashboard")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Get data
    stats = get_stats_api()
    blocked_ips = get_blocked_ips_api()
    
    if stats:
        # Statistics cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['total_blocked']}</h3>
                <p>Total Blocked IPs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['currently_blocked']}</h3>
                <p>Currently Blocked</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if stats['country_stats']:
                top_country = stats['country_stats'][0]
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{top_country['country']}</h3>
                    <p>Top Threat Country ({top_country['count']})</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h3>None</h3>
                    <p>Top Threat Country</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Blocked IPs table
        st.subheader("🚫 Blocked IP Addresses")
        
        if blocked_ips:
            # Create DataFrame
            df = pd.DataFrame(blocked_ips)
            df['blocked_at'] = pd.to_datetime(df['blocked_at'])
            df['status'] = df['unblocked_at'].apply(lambda x: 'Unblocked' if pd.notna(x) else 'Blocked')
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("Filter by status", ["All", "Blocked", "Unblocked"])
            with col2:
                if status_filter != "All":
                    df = df[df['status'] == status_filter]
            
            # Display table
            st.dataframe(
                df[['ip_address', 'url', 'country', 'blocked_at', 'status']],
                use_container_width=True
            )
            
            # Unblock functionality
            st.subheader("🔓 Unblock IP Address")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_ip = st.selectbox(
                    "Select IP to unblock:",
                    options=df[df['status'] == 'Blocked']['ip_address'].tolist() if len(df[df['status'] == 'Blocked']) > 0 else [],
                    help="Only currently blocked IPs are shown"
                )
            
            with col2:
                if st.button("Unblock IP", type="secondary"):
                    if selected_ip:
                        with st.spinner("Unblocking IP..."):
                            result = unblock_ip_api(selected_ip)
                        
                        if result.get('success'):
                            st.success(f"✅ IP {selected_ip} has been unblocked successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to unblock IP: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please select an IP to unblock")
        else:
            st.info("No blocked IPs found")
    else:
        st.error("❌ Cannot connect to Flask API. Please ensure the server is running on port 5000.")

# Statistics Page
elif page == "Statistics":
    st.header("📊 Threat Statistics")
    
    stats = get_stats_api()
    blocked_ips = get_blocked_ips_api()
    
    if stats and blocked_ips:
        # Country distribution chart
        if stats['country_stats']:
            st.subheader("🌍 Threat Distribution by Country")
            
            country_df = pd.DataFrame(stats['country_stats'])
            
            # Pie chart
            fig_pie = px.pie(
                country_df, 
                values='count', 
                names='country',
                title="Blocked IPs by Country",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Bar chart
            fig_bar = px.bar(
                country_df,
                x='country',
                y='count',
                title="Blocked IPs by Country",
                color='count',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Timeline chart
        st.subheader("📈 Blocking Timeline")
        
        if blocked_ips:
            timeline_df = pd.DataFrame(blocked_ips)
            timeline_df['blocked_at'] = pd.to_datetime(timeline_df['blocked_at'])
            timeline_df['date'] = timeline_df['blocked_at'].dt.date
            
            daily_counts = timeline_df.groupby('date').size().reset_index(name='count')
            
            fig_timeline = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Daily Blocking Activity",
                markers=True
            )
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Blocked IPs"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Recent activity
        st.subheader("🕒 Recent Activity")
        recent_ips = pd.DataFrame(blocked_ips).head(10)
        if not recent_ips.empty:
            recent_ips['blocked_at'] = pd.to_datetime(recent_ips['blocked_at'])
            st.dataframe(
                recent_ips[['ip_address', 'country', 'blocked_at']],
                use_container_width=True
            )
        else:
            st.info("No recent activity")
    else:
        st.error("❌ Cannot load statistics. Please ensure the Flask API is running.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔐 GeoIP-Augmented ML Firewall for Phishing Prevention</p>
    <p>Built with Streamlit, Flask, and Machine Learning</p>
</div>
""", unsafe_allow_html=True)
