# 🏗️ System Architecture & Data Flow

## 📊 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CYBER SECURITY FIREWALL SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Streamlit UI   │    │ Monitoring Dash │    │   Admin Panel   │
│   (index.html)  │    │ (streamlit_app) │    │(monitoring_dash)│    │  (admin.html)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │                      │
          │ HTTP Requests        │ HTTP Requests        │ HTTP Requests        │ HTTP Requests
          │                      │                      │                      │
          └──────────────────────┼──────────────────────┼──────────────────────┘
                                 │                      │
                    ┌─────────────▼─────────────┐      │
                    │      Flask API Server     │      │
                    │        (app.py)           │      │
                    │      Port: 5000           │      │
                    └─────────────┬─────────────┘      │
                                  │                    │
          ┌───────────────────────┼─────────────────────┼───────────────────────┐
          │                       │                     │                       │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│  ML Classifier  │    │   GeoIP Engine  │    │  Firewall Mgmt  │    │  SQLite DB      │
│ (11 Features)   │    │  (Country Risk) │    │ (UFW/Windows)   │    │(firewall_logs)  │
│                 │    │                 │    │                 │    │                 │
│ • URL Length    │    │ • MaxMind DB    │    │ • Linux: UFW    │    │ • blocked_ips   │
│ • Domain Length │    │ • Country Codes │    │ • Windows: netsh│    │ • Timestamps    │
│ • Dot Count     │    │ • Risk Flags    │    │ • Auto Block    │    │ • Admin Logs    │
│ • HTTPS Flag    │    │ • RU,CN,IR,KP   │    │ • Unblock       │    │ • Statistics    │
│ • Hyphen Count  │    │                 │    │                 │    │                 │
│ • Underscore    │    │                 │    │                 │    │                 │
│ • Slash Count   │    │                 │    │                 │    │                 │
│ • Path Length   │    │                 │    │                 │    │                 │
│ • Has @ Symbol  │    │                 │    │                 │    │                 │
│ • Has Query     │    │                 │    │                 │    │                 │
│ • Has Fragment  │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                     │                       │
          └───────────────────────┼─────────────────────┼───────────────────────┘
                                  │                     │
                    ┌─────────────▼─────────────┐      │
                    │    Two-Tier Defense      │      │
                    │                         │      │
                    │ 1. Keyword Pre-filter   │      │
                    │ 2. ML Classification    │      │
                    └─────────────────────────┘      │
                                                     │
                    ┌─────────────────────────────────▼─────────────────────────────────┐
                    │                    External Systems                               │
                    │                                                                  │
                    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
                    │  │   UFW       │  │  Windows    │  │   GeoIP     │              │
                    │  │ Firewall    │  │ Firewall    │  │ Database    │              │
                    │  │ (Linux)     │  │ (Windows)   │  │ (MaxMind)   │              │
                    │  └─────────────┘  └─────────────┘  └─────────────┘              │
                    └──────────────────────────────────────────────────────────────────┘
```

## 🔄 Detailed Data Flow

### **1. URL Scanning Process**

```
User Input URL
    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Interface                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Browser   │  │ Streamlit   │  │ Monitoring  │            │
│  │ (index.html)│  │ Dashboard   │  │ Dashboard   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP POST /check_url
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Flask API Server (app.py)                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              check_url() Function                       │   │
│  │                                                         │   │
│  │  1. Parse JSON request                                  │   │
│  │  2. Extract URL from request                            │   │
│  │  3. Get client IP address                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Two-Tier Defense System                    │   │
│  │                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────────────┐    │   │
│  │  │ Keyword Check   │    │ ML Classification       │    │   │
│  │  │                 │    │                         │    │   │
│  │  │ • login         │    │ • Extract 11 features   │    │   │
│  │  │ • secure        │    │ • Load ML model         │    │   │
│  │  │ • account       │    │ • Predict phishing      │    │   │
│  │  │ • verify        │    │ • Return result         │    │   │
│  │  │ • update        │    │                         │    │   │
│  │  │ • password      │    │                         │    │   │
│  │  │ • bank          │    │                         │    │   │
│  │  │ • confirm       │    │                         │    │   │
│  │  └─────────────────┘    └─────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              IP Resolution & GeoIP                      │   │
│  │                                                         │   │
│  │  • get_ip_from_url() - Resolve hostname to IP          │   │
│  │  • get_geo_location() - Get country from IP            │   │
│  │  • Check against flagged countries (RU,CN,IR,KP)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Firewall Blocking                          │   │
│  │                                                         │   │
│  │  if (result == 'phishing'):                            │   │
│  │    block_ip_with_ufw(ip_address)                       │   │
│  │    • Linux: sudo ufw deny from IP                      │   │
│  │    • Windows: netsh advfirewall add rule               │   │
│  │    • Log to database                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Database Logging                           │   │
│  │                                                         │   │
│  │  INSERT INTO blocked_ips (ip_address, url, country,    │   │
│  │                         blocked_at) VALUES (...)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Response Generation                        │   │
│  │                                                         │   │
│  │  return jsonify({                                       │   │
│  │    'url': url,                                          │   │
│  │    'url_ip': url_ip,                                    │   │
│  │    'country': country_code,                             │   │
│  │    'geoFlagged': geo_flagged,                           │   │
│  │    'mlResult': result,                                  │   │
│  │    'blocked': blocked                                   │   │
│  │  })                                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ JSON Response
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Display                             │
│                                                                 │
│  • Show phishing/safe result                                   │
│  • Display IP address and country                              │
│  • Show blocking status                                        │
│  • Update UI with appropriate styling                          │
└─────────────────────────────────────────────────────────────────┘
```

### **2. Admin Management Process**

```
Admin Panel Access
    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Admin Interface                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Browser   │  │ Streamlit   │  │ Monitoring  │            │
│  │ (admin.html)│  │ Dashboard   │  │ Dashboard   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP GET /api/blocked_ips
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Flask API Server                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              get_blocked_ips() Function                 │   │
│  │                                                         │   │
│  │  1. Connect to SQLite database                          │   │
│  │  2. Query blocked_ips table                             │   │
│  │  3. Return JSON array of blocked IPs                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Database Query                             │   │
│  │                                                         │   │
│  │  SELECT ip_address, url, country, blocked_at,          │   │
│  │         unblocked_at                                    │   │
│  │  FROM blocked_ips                                       │   │
│  │  ORDER BY blocked_at DESC                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ JSON Response
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Admin Display                                │
│                                                                 │
│  • Show table of blocked IPs                                   │
│  • Display status (blocked/unblocked)                          │
│  • Provide unblock buttons                                     │
│  • Show country statistics                                     │
└─────────────────────────────────────────────────────────────────┘

Unblock IP Action
    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Unblock Process                             │
│                                                                 │
│  HTTP POST /api/unblock_ip                                     │
│  { "ip_address": "192.168.1.1" }                              │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              unblock_ip() Function                      │   │
│  │                                                         │   │
│  │  1. Validate IP address                                 │   │
│  │  2. Call unblock_ip_with_ufw()                          │   │
│  │  3. Update database                                     │   │
│  │  4. Return success/failure                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Firewall Unblocking                        │   │
│  │                                                         │   │
│  │  • Linux: sudo ufw delete deny from IP                 │   │
│  │  • Windows: netsh advfirewall delete rule              │   │
│  │  • Update unblocked_at timestamp in database           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### **3. Real-time Monitoring Process**

```
Monitoring Dashboard
    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Auto-refresh Loop (30s)                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              System Status Check                        │   │
│  │                                                         │   │
│  │  • Check Flask API health                              │   │
│  │  • Get current statistics                              │   │
│  │  • Calculate threat level                              │   │
│  │  • Update dashboard                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Statistics Collection                      │   │
│  │                                                         │   │
│  │  HTTP GET /api/stats                                    │   │
│  │  • Total blocked IPs                                    │   │
│  │  • Currently blocked IPs                                │   │
│  │  • Country distribution                                 │   │
│  │  • System performance metrics                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Threat Level Assessment                    │   │
│  │                                                         │   │
│  │  if (currently_blocked > 10):                          │   │
│  │    threat_level = "HIGH"                               │   │
│  │  elif (currently_blocked > 5):                         │   │
│  │    threat_level = "MEDIUM"                             │   │
│  │  else:                                                 │   │
│  │    threat_level = "LOW"                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              ↓                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Dashboard Updates                          │   │
│  │                                                         │   │
│  │  • Update threat level indicator                        │   │
│  │  • Refresh statistics cards                             │   │
│  │  • Update geographic charts                             │   │
│  │  • Show recent activity feed                            │   │
│  │  • Display system performance                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 File Interconnection Matrix

| File | Depends On | Used By | Purpose |
|------|------------|---------|---------|
| **app.py** | phishing_model.pkl, firewall_logs.db | streamlit_app.py, monitoring_dashboard.py, index.html, admin.html | Main API server |
| **phishing_model.pkl** | enhanced_training_data.py | app.py | Trained ML model |
| **enhanced_training_data.py** | sklearn, joblib | Creates phishing_model.pkl | Model training |
| **streamlit_app.py** | app.py (API calls) | User interface | Streamlit dashboard |
| **monitoring_dashboard.py** | app.py (API calls) | User interface | Real-time monitoring |
| **index.html** | app.py (API calls) | User interface | Main web interface |
| **admin.html** | app.py (API calls) | User interface | Admin panel |
| **firewall_logs.db** | app.py (creates) | app.py, admin.html, monitoring_dashboard.py | Data storage |

## 📊 Data Flow Summary

### **Input Sources**
1. **User URLs** → Frontend interfaces
2. **Admin Commands** → Admin panel
3. **System Monitoring** → Monitoring dashboard

### **Processing Pipeline**
1. **URL Analysis** → Two-tier defense system
2. **IP Resolution** → DNS lookup
3. **GeoIP Analysis** → Country risk assessment
4. **Firewall Actions** → IP blocking/unblocking
5. **Database Logging** → Persistent storage

### **Output Destinations**
1. **User Interfaces** → Results display
2. **Firewall Rules** → System security
3. **Database** → Audit trail
4. **Admin Tools** → Management interface

This architecture ensures that every component is interconnected and serves a specific purpose in the overall cybersecurity workflow, creating a comprehensive and robust phishing detection and prevention system.
