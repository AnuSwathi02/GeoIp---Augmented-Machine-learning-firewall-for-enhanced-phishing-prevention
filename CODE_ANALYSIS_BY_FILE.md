# 📋 Complete Code Analysis by File

## 🎯 Overview
This document provides a line-by-line analysis of every file in the project, explaining how each line of code impacts the overall system.

---

## 📁 **app.py** - Main Flask API Server (325 lines)

### **Lines 1-9: Import Statements**
```python
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
from urllib.parse import urlparse
import subprocess
import socket
import sqlite3
import datetime
import os
```

**Impact Analysis:**
- **Line 1**: `Flask` - Core web framework for API server
- **Line 1**: `request` - Handles HTTP requests from frontend
- **Line 1**: `jsonify` - Converts Python objects to JSON responses
- **Line 1**: `render_template` - Serves HTML templates
- **Line 2**: `CORS` - Enables cross-origin requests (essential for frontend-backend communication)
- **Line 3**: `joblib` - Loads the trained ML model from pickle file
- **Line 4**: `urlparse` - Parses URLs for feature extraction
- **Line 5**: `subprocess` - Executes system commands (firewall operations)
- **Line 6**: `socket` - Resolves hostnames to IP addresses
- **Line 7**: `sqlite3` - Database operations for logging
- **Line 8**: `datetime` - Timestamp handling
- **Line 9**: `os` - Operating system interface

### **Lines 11-15: GeoIP Integration**
```python
try:
    import geoip2.database
    geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
except:
    geoip_reader = None  # GeoIP not available
```

**Impact Analysis:**
- **Line 12**: Imports GeoIP2 library for geographic analysis
- **Line 13**: Loads MaxMind GeoLite2 database for country lookup
- **Line 14-15**: Graceful fallback if GeoIP database is missing
- **System Impact**: Enables country-based risk assessment, critical for geographic threat analysis

### **Lines 17-20: Flask App Initialization**
```python
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS
model = joblib.load('phishing_model.pkl')
```

**Impact Analysis:**
- **Line 18**: Creates Flask application instance with template folder
- **Line 19**: Enables CORS for frontend communication
- **Line 20**: Loads the trained ML model (critical for phishing detection)
- **System Impact**: Core application setup, enables all API functionality

### **Lines 25-43: Database Initialization**
```python
def init_database():
    conn = sqlite3.connect('firewall_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE,
            url TEXT,
            country TEXT,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unblocked_at TIMESTAMP NULL
        )
    ''')
    conn.commit()
    conn.close()

init_database()
```

**Impact Analysis:**
- **Line 26**: Connects to SQLite database (creates if doesn't exist)
- **Line 30**: Creates unique identifier for each record
- **Line 31**: Stores blocked IP address (unique constraint prevents duplicates)
- **Line 32**: Stores original URL that triggered the block
- **Line 33**: Stores country code from GeoIP analysis
- **Line 34**: Automatic timestamp when IP is blocked
- **Line 35**: Timestamp when IP is unblocked (NULL = still blocked)
- **Line 43**: Calls function on startup to ensure database exists
- **System Impact**: Enables persistent storage, admin functionality, and audit trails

### **Lines 45-104: UFW Firewall Blocking Function**
```python
def block_ip_with_ufw(ip_address):
    """Block IP using UFW firewall (Linux) or Windows Firewall (Windows)"""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "linux":
            # Linux UFW commands
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("UFW not available, simulating block")
                return True
            
            # Block the IP
            subprocess.run(['sudo', 'ufw', 'insert', '1', 'deny', 'from', ip_address], 
                          check=True, capture_output=True)
        elif system == "windows":
            # Windows Firewall commands
            try:
                # Use netsh to block IP in Windows Firewall
                subprocess.run([
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=Block_IP_{ip_address}',
                    'dir=in',
                    'action=block',
                    f'remoteip={ip_address}'
                ], check=True, capture_output=True)
                print(f"Successfully blocked IP {ip_address} using Windows Firewall")
            except subprocess.CalledProcessError:
                print(f"Windows Firewall block failed, simulating block for IP {ip_address}")
        else:
            print(f"Unsupported OS: {system}, simulating block for IP {ip_address}")
        
        # Log to database (always do this regardless of OS)
        conn = sqlite3.connect('firewall_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO blocked_ips (ip_address, blocked_at)
            VALUES (?, CURRENT_TIMESTAMP)
        ''', (ip_address,))
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error blocking IP {ip_address}: {e}")
        # Still log to database even if firewall command fails
        try:
            conn = sqlite3.connect('firewall_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO blocked_ips (ip_address, blocked_at)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (ip_address,))
            conn.commit()
            conn.close()
        except:
            pass
        return False
```

**Impact Analysis:**
- **Line 49**: Detects operating system for appropriate firewall commands
- **Line 52-58**: Linux UFW firewall integration
- **Line 59-75**: Windows Firewall integration using netsh
- **Line 76-77**: Fallback for unsupported operating systems
- **Line 80-87**: Database logging (always executed regardless of OS)
- **Line 89-104**: Error handling with database fallback
- **System Impact**: Core security feature - automatically blocks malicious IPs

### **Lines 106-163: UFW Firewall Unblocking Function**
```python
def unblock_ip_with_ufw(ip_address):
    """Unblock IP using UFW firewall (Linux) or Windows Firewall (Windows)"""
    # Similar structure to block_ip_with_ufw but for unblocking
```

**Impact Analysis:**
- **Lines 109-121**: Linux UFW unblock commands
- **Lines 122-131**: Windows Firewall unblock commands
- **Lines 137-145**: Database update to mark IP as unblocked
- **System Impact**: Enables admin functionality to remove IP blocks

### **Lines 165-175: IP Resolution Function**
```python
def get_ip_from_url(url):
    """Extract IP address from URL"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname:
            ip = socket.gethostbyname(hostname)
            return ip
    except:
        pass
    return None
```

**Impact Analysis:**
- **Line 168**: Parses URL to extract hostname
- **Line 170**: Performs DNS lookup to get IP address
- **Line 172-174**: Error handling for failed DNS resolution
- **System Impact**: Essential for firewall operations - converts URLs to blockable IPs

### **Lines 177-191: Enhanced Feature Extraction**
```python
def extract_features(url):
    """Extract 11 advanced features from a given URL"""
    parsed = urlparse(url)
    return [
        len(url),                           # 1. Full URL length
        len(parsed.netloc),                 # 2. Domain length
        url.count('.'),                     # 3. Dot count
        int(url.startswith('https')),       # 4. HTTPS flag
        url.count('-'),                     # 5. Hyphen count
        url.count('_'),                     # 6. Underscore count
        url.count('/'),                     # 7. Slash count
        len(parsed.path),                   # 8. Path length
        int('@' in url),                    # 9. Contains @ symbol
        int('?' in url),                    # 10. Contains query parameters
        int('#' in url)                     # 11. Contains fragment
    ]
```

**Impact Analysis:**
- **Line 179**: Parses URL for feature extraction
- **Line 180**: URL length (phishing URLs often longer)
- **Line 181**: Domain length (suspicious domains often longer)
- **Line 182**: Dot count (phishing URLs often have many dots)
- **Line 183**: HTTPS flag (legitimate sites more likely to use HTTPS)
- **Line 184**: Hyphen count (phishing domains often use hyphens)
- **Line 185**: Underscore count (suspicious character)
- **Line 186**: Slash count (complex paths may indicate phishing)
- **Line 187**: Path length (long paths may be suspicious)
- **Line 188**: @ symbol (often used in phishing URLs)
- **Line 189**: Query parameters (phishing URLs often have parameters)
- **Line 190**: Fragment (URL fragments can be suspicious)
- **System Impact**: Core ML feature extraction - enables accurate phishing detection

### **Lines 193-199: Keyword Detection Function**
```python
def is_phishing_keyword_present(url):
    phishing_keywords = ['login', 'secure', 'account', 'verify', 'update', 'password', 'bank', 'confirm']
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in phishing_keywords)
```

**Impact Analysis:**
- **Line 194**: Common phishing keywords list
- **Line 195**: Convert URL to lowercase for case-insensitive matching
- **Line 196**: Check if any keyword exists in URL
- **System Impact**: Fast pre-filtering before expensive ML analysis

### **Lines 201-210: GeoIP Location Function**
```python
def get_geo_location(ip_address):
    if geoip_reader is None:
        return None
    try:
        response = geoip_reader.city(ip_address)
        return response.country.iso_code
    except Exception:
        return None
```

**Impact Analysis:**
- **Line 202**: Check if GeoIP database is available
- **Line 204**: Query GeoIP database for country information
- **Line 205**: Extract country code from response
- **Line 206-207**: Error handling for failed GeoIP lookup
- **System Impact**: Enables geographic risk assessment

### **Lines 212-216: Home Route**
```python
@app.route('/')
def home():
    return render_template('index.html')
```

**Impact Analysis:**
- **Line 213**: Defines route for main page
- **Line 214**: Serves the main web interface
- **System Impact**: Entry point for web interface

### **Lines 218-250: Main URL Check API**
```python
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url')
    ip = request.remote_addr

    # Get IP from URL
    url_ip = get_ip_from_url(url)
    
    # GeoIP Check
    country_code = get_geo_location(ip)
    risky_countries = ['RU', 'CN', 'IR', 'KP']
    geo_flagged = country_code in risky_countries if country_code else False

    # HERE is the key change: check keywords FIRST
    if is_phishing_keyword_present(url):
        result = 'phishing'
        # Block IP if phishing detected
        if url_ip:
            block_ip_with_ufw(url_ip)
    else:
        # If no phishing keywords found, use the ML model prediction
        features = extract_features(url)
        prediction = model.predict([features])[0]
        result = 'phishing' if prediction == 1 else 'safe'
        
        # Block IP if phishing detected by ML
        if result == 'phishing' and url_ip:
            block_ip_with_ufw(url_ip)

    return jsonify({
        'url': url,
        'url_ip': url_ip,
        'country': country_code,
        'geoFlagged': geo_flagged,
        'mlResult': result,
        'blocked': result == 'phishing' and url_ip is not None
    })
```

**Impact Analysis:**
- **Line 220**: Extract URL from JSON request
- **Line 221**: Get client IP address
- **Line 224**: Resolve URL hostname to IP
- **Line 227**: Get country from client IP
- **Line 228**: Define risky countries list
- **Line 229**: Check if country is flagged
- **Line 232-236**: Two-tier defense - keyword check first
- **Line 237-243**: ML model analysis if no keywords found
- **Line 245-250**: Comprehensive response with all analysis results
- **System Impact**: Core phishing detection endpoint - ties all components together

### **Lines 252-325: Admin API Endpoints**
```python
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/blocked_ips')
def get_blocked_ips():
    # Database query implementation

@app.route('/api/unblock_ip', methods=['POST'])
def unblock_ip():
    # Unblock functionality implementation

@app.route('/api/stats')
def get_stats():
    # Statistics generation implementation
```

**Impact Analysis:**
- **Line 253**: Serves admin interface
- **Line 256**: API endpoint for blocked IPs list
- **Line 259**: API endpoint for unblocking IPs
- **Line 262**: API endpoint for system statistics
- **System Impact**: Enables admin functionality and monitoring

---

## 📁 **enhanced_training_data.py** - ML Model Training (179 lines)

### **Lines 1-4: Imports**
```python
from sklearn.ensemble import RandomForestClassifier
import joblib
import random
```

**Impact Analysis:**
- **Line 1**: Random Forest algorithm for ML classification
- **Line 2**: Model serialization library
- **Line 3**: Random number generation for data shuffling
- **System Impact**: Enables ML model creation

### **Lines 6-179: Training Data Creation**
```python
# Enhanced training data with 11 features
# Format: [url_len, domain_len, dots, https, hyphens, underscores, slashes, path_len, has_at, has_query, has_fragment]

# Safe URLs (label = 0)
safe_urls = [
    [45, 12, 2, 1, 0, 0, 2, 5, 0, 0, 0],   # https://google.com/search
    # ... 32 safe URL samples
]

# Phishing URLs (label = 1)
phishing_urls = [
    [78, 15, 3, 0, 2, 1, 3, 8, 0, 1, 0],   # http://fake-bank-site.com/login?redirect=steal
    # ... 45 phishing URL samples
]
```

**Impact Analysis:**
- **Lines 7-32**: Safe URL samples with realistic feature values
- **Lines 34-77**: Phishing URL samples with suspicious characteristics
- **Each line**: Represents one training sample with 11 features
- **System Impact**: Creates comprehensive training dataset for accurate ML model

### **Lines 180-200: Model Training and Saving**
```python
# Combine all data
X = safe_urls + phishing_urls
y = [0] * len(safe_urls) + [1] * len(phishing_urls)

# Shuffle the data
combined = list(zip(X, y))
random.shuffle(combined)
X, y = zip(*combined)
X = list(X)
y = list(y)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'phishing_model.pkl')
```

**Impact Analysis:**
- **Line 181**: Combines safe and phishing samples
- **Line 182**: Creates labels (0=safe, 1=phishing)
- **Line 185-189**: Shuffles data to prevent bias
- **Line 192**: Creates Random Forest with 100 trees
- **Line 193**: Trains the model on the data
- **Line 196**: Saves model to pickle file
- **System Impact**: Creates the ML model used by app.py for phishing detection

---

## 📁 **templates/index.html** - Main Web Interface (241 lines)

### **Lines 1-163: HTML Structure and CSS**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Phishing URL Detector</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
  <style>
    /* CSS styles for modern UI */
  </style>
</head>
```

**Impact Analysis:**
- **Line 2**: HTML5 document type
- **Line 3**: Language specification
- **Line 5**: Page title for browser tab
- **Line 6**: Google Fonts for professional appearance
- **Lines 7-163**: CSS styles for modern, responsive design
- **System Impact**: Creates professional user interface

### **Lines 165-178: HTML Body Structure**
```html
<body>
  <div class="glow-banner">
    <span>🚨 Stay Vigilant! Paste a URL below to detect phishing threats in real-time! 🚨</span>
  </div>

  <div class="container">
    <h2>🔐 Real-Time Phishing URL Scanner</h2>
    <input type="text" id="urlInput" placeholder="Paste a URL to scan (e.g. https://suspicious-site.com)" />
    <button onclick="checkURL()">🔎 Check Now</button>
    <div style="margin-top: 15px;">
      <a href="/admin" style="color: #007bff; text-decoration: none; font-weight: 600;">🛡️ Admin Panel</a>
    </div>
```

**Impact Analysis:**
- **Line 167**: Animated warning banner
- **Line 171**: Main heading
- **Line 172**: URL input field
- **Line 173**: Check button that triggers analysis
- **Line 175**: Link to admin panel
- **System Impact**: User interface elements for URL scanning

### **Lines 180-232: JavaScript Functionality**
```javascript
function checkURL() {
  const url = document.getElementById("urlInput").value.trim();
  const resultBox = document.getElementById("resultBox");
  const loading = document.getElementById("loading");
  const geoFlag = document.getElementById("geoFlag");

  resultBox.style.display = "none";
  geoFlag.textContent = "";
  loading.style.display = "block";

  if (!url) {
    alert("Please enter a URL.");
    loading.style.display = "none";
    return;
  }

  fetch("http://127.0.0.1:5000/check_url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: url }),
  })
  .then((res) => {
    if (!res.ok) {
      throw new Error('Server error. Please try again.');
    }
    return res.json();
  })
  .then((data) => {
    loading.style.display = "none";
    resultBox.style.display = "block";
    resultBox.className = "result " + (data.mlResult === "phishing" ? "phishing" : "safe");

    const icon = data.mlResult === "phishing" ? "🚨" : "✅";
    resultBox.innerHTML = `
      <strong>${icon} ${data.mlResult.toUpperCase()}</strong><br><br>
      <strong>URL:</strong> <a href="${data.url}" target="_blank" rel="noopener noreferrer">${data.url}</a><br>
      <strong>IP Address:</strong> ${data.url_ip || "Unknown"}<br>
      <strong>Country:</strong> ${data.country || "Unknown"}<br>
      ${data.blocked ? '<br><strong>🛡️ IP Address has been automatically blocked!</strong>' : ''}
    `;

    geoFlag.textContent = data.geoFlagged
      ? "⚠️ Alert: The URL originates from a flagged country."
      : "🟢 Country origin appears safe.";
  })
  .catch((error) => {
    loading.style.display = "none";
    resultBox.style.display = "block";
    resultBox.className = "result phishing";
    resultBox.textContent = `❌ Error: ${error.message}`;
  });
}
```

**Impact Analysis:**
- **Line 181**: Get URL from input field
- **Line 182-184**: Get DOM elements for display
- **Line 186-188**: Hide previous results, show loading
- **Line 190-194**: Validate URL input
- **Line 196-202**: Send POST request to Flask API
- **Line 203-208**: Handle API response
- **Line 209-220**: Display results with appropriate styling
- **Line 222-225**: Show geographic warnings
- **Line 226-231**: Error handling
- **System Impact**: Frontend-backend communication, user experience

---

## 📁 **templates/admin.html** - Admin Panel (418 lines)

### **Lines 1-163: HTML Structure and CSS**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Phishing Firewall</title>
    <style>
        /* Admin-specific CSS styles */
    </style>
</head>
```

**Impact Analysis:**
- **Line 4**: Responsive viewport meta tag
- **Line 5**: Admin-specific page title
- **Lines 6-163**: CSS for professional admin interface
- **System Impact**: Creates admin interface styling

### **Lines 200-418: JavaScript Admin Functions**
```javascript
async function loadData() {
    try {
        // Load statistics
        const statsResponse = await fetch('/api/stats');
        stats = await statsResponse.json();
        updateStats();

        // Load blocked IPs
        const ipsResponse = await fetch('/api/blocked_ips');
        blockedIps = await ipsResponse.json();
        updateBlockedIpsTable();
        updateCountryStatsTable();

    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load data. Please try again.');
    }
}

async function unblockIp(ipAddress) {
    if (!confirm(`Are you sure you want to unblock IP address ${ipAddress}?`)) {
        return;
    }

    try {
        const response = await fetch('/api/unblock_ip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ip_address: ipAddress })
        });

        const result = await response.json();

        if (result.success) {
            showSuccess(`IP address ${ipAddress} has been unblocked successfully.`);
            loadData(); // Refresh data
        } else {
            showError(`Failed to unblock IP address ${ipAddress}.`);
        }
    } catch (error) {
        console.error('Error unblocking IP:', error);
        showError('Failed to unblock IP address. Please try again.');
    }
}
```

**Impact Analysis:**
- **Lines 201-203**: Fetch system statistics from API
- **Lines 205-207**: Fetch blocked IPs list from API
- **Lines 209-212**: Error handling for API failures
- **Lines 215-217**: Confirmation dialog for unblocking
- **Lines 219-225**: Send unblock request to API
- **Lines 227-233**: Handle unblock response
- **Lines 234-238**: Error handling for unblock failures
- **System Impact**: Enables admin functionality and IP management

---

## 📁 **streamlit_app.py** - Streamlit Dashboard (377 lines)

### **Lines 1-10: Imports and Configuration**
```python
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
```

**Impact Analysis:**
- **Line 1**: Streamlit web app framework
- **Line 2**: HTTP client for API communication
- **Line 3**: Data manipulation library
- **Line 4-5**: Interactive charting libraries
- **Line 6**: Date/time handling
- **Line 7**: Time operations
- **Lines 9-15**: Streamlit page configuration
- **System Impact**: Creates modern dashboard interface

### **Lines 12-50: Custom CSS and Helper Functions**
```python
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
    /* More CSS styles */
</style>
""", unsafe_allow_html=True)

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
```

**Impact Analysis:**
- **Lines 13-30**: Custom CSS for professional appearance
- **Lines 32-42**: API communication function
- **Line 34**: Send POST request to Flask API
- **Line 35**: Check response status
- **Line 36**: Return JSON data if successful
- **Line 38**: Return error if API request fails
- **Lines 39-41**: Handle connection errors
- **Lines 42-43**: Handle other exceptions
- **System Impact**: Enables communication between Streamlit and Flask API

### **Lines 52-200: Main Dashboard Pages**
```python
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
                    # Display results with appropriate styling
```

**Impact Analysis:**
- **Line 54**: Page header
- **Line 56**: Create two-column layout
- **Lines 58-63**: URL input field with help text
- **Line 65**: Scan button
- **Line 67**: Check if URL is provided
- **Line 68**: Show loading spinner
- **Line 69**: Call API function
- **Line 71**: Check for errors
- **Line 72**: Display error message
- **Line 74**: Display results
- **System Impact**: Interactive URL scanning interface

---

## 📁 **monitoring_dashboard.py** - Real-time Monitoring (300+ lines)

### **Lines 1-50: Setup and Configuration**
```python
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
```

**Impact Analysis:**
- **Lines 1-10**: Import libraries for real-time monitoring
- **Line 8**: SQLite for direct database access
- **Line 9**: Threading for concurrent operations
- **Line 10**: Queue for thread communication
- **Lines 12-18**: Streamlit configuration for monitoring dashboard
- **System Impact**: Enables real-time system monitoring

### **Lines 100-200: Real-time Functions**
```python
def get_system_status():
    """Check if Flask API is online"""
    try:
        response = requests.get(f"{API_BASE}/api/stats", timeout=5)
        return "online" if response.status_code == 200 else "offline"
    except:
        return "offline"

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
```

**Impact Analysis:**
- **Lines 102-107**: Check Flask API health
- **Line 104**: Send GET request to stats endpoint
- **Line 105**: Return online/offline status
- **Line 106**: Handle connection errors
- **Lines 109-120**: Calculate threat level based on blocked IPs
- **Line 113**: Get currently blocked IP count
- **Lines 115-119**: Determine threat level thresholds
- **System Impact**: Enables real-time system health monitoring

---

## 🔗 **File Interconnection Summary**

### **Core Dependencies**
1. **app.py** ← **phishing_model.pkl** (loads ML model)
2. **app.py** ← **firewall_logs.db** (database operations)
3. **app.py** → **templates/index.html** (serves main interface)
4. **app.py** → **templates/admin.html** (serves admin interface)

### **API Dependencies**
1. **streamlit_app.py** → **app.py** (HTTP API calls)
2. **monitoring_dashboard.py** → **app.py** (HTTP API calls)
3. **templates/index.html** → **app.py** (JavaScript API calls)
4. **templates/admin.html** → **app.py** (JavaScript API calls)

### **Model Dependencies**
1. **enhanced_training_data.py** → **phishing_model.pkl** (creates model)
2. **app.py** ← **phishing_model.pkl** (loads model)
3. **phishing_model.py** → **phishing_model.pkl** (original model)

### **Data Flow**
1. **Training**: enhanced_training_data.py creates model
2. **Loading**: app.py loads model for predictions
3. **Processing**: URL → features → prediction → action
4. **Storage**: Results stored in SQLite database
5. **Display**: Frontend interfaces show results and statistics

This comprehensive analysis shows how every line of code contributes to the overall cybersecurity system, creating a robust and interconnected phishing detection and prevention solution.
