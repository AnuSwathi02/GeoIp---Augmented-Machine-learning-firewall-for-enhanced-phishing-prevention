# 🔐 GeoIP-Augmented ML Firewall for Phishing Prevention

A comprehensive cybersecurity solution that combines machine learning, GeoIP analysis, and UFW firewall integration to detect and block phishing threats in real-time.

## 🚀 Features

### ✅ Implemented Features

- **🤖 Machine Learning Classification**: Random Forest classifier with 11 URL-based features
- **🌍 GeoIP Integration**: Country-based risk assessment with flagged regions (RU, CN, IR, KP)
- **🛡️ Two-Tier Defense System**: Keyword-based pre-filtering + ML model classification
- **🔥 UFW Firewall Integration**: Automatic IP blocking for detected threats
- **💾 SQLite Database**: Persistent storage for blocked IPs and system logs
- **👨‍💼 Admin Interface**: Web-based admin panel for IP management
- **📊 Real-time Monitoring**: Live dashboard with threat statistics
- **🎨 Multiple Interfaces**: Flask web app, Streamlit dashboard, and monitoring tools

### 🎯 Key Capabilities

- **Real-time URL Scanning**: Instant phishing detection
- **Automatic IP Blocking**: UFW firewall integration for immediate threat mitigation
- **Geographic Analysis**: Country-based threat assessment
- **Admin Controls**: Unblock IPs and manage firewall rules
- **Live Monitoring**: Real-time threat statistics and system performance
- **Enhanced ML Model**: 11-feature URL analysis with 100% training accuracy

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Streamlit UI   │    │ Monitoring Dash │
│    (Flask)      │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Flask API Server     │
                    │    (Port 5000)           │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│  ML Classifier  │    │   GeoIP Engine  │    │  UFW Firewall   │
│ (11 Features)   │    │  (Country Risk) │    │   (Auto Block)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    SQLite Database       │
                    │  (Blocked IPs & Logs)   │
                    └───────────────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- UFW firewall (Linux/Ubuntu)
- GeoLite2 database (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cyber-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download GeoLite2 database** (optional)
   ```bash
   # Download from MaxMind and place as 'GeoLite2-City.mmdb'
   ```

5. **Train the ML model**
   ```bash
   python enhanced_training_data.py
   ```

## 🚀 Usage

### 1. Flask Web Application

Start the main Flask server:
```bash
python app.py
```

Access the web interface at: `http://localhost:5000`

### 2. Streamlit Dashboard

Launch the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

Access at: `http://localhost:8501`

### 3. Real-time Monitoring

Start the monitoring dashboard:
```bash
streamlit run monitoring_dashboard.py
```

Access at: `http://localhost:8502`

### 4. Admin Panel

Access the admin interface at: `http://localhost:5000/admin`

## 📊 ML Model Details

### Features (11 total)
1. **URL Length**: Total character count
2. **Domain Length**: Domain name character count
3. **Dot Count**: Number of dots in URL
4. **HTTPS Flag**: Whether URL uses HTTPS
5. **Hyphen Count**: Number of hyphens
6. **Underscore Count**: Number of underscores
7. **Slash Count**: Number of forward slashes
8. **Path Length**: URL path character count
9. **Has @ Symbol**: Presence of @ character
10. **Has Query Params**: Presence of query parameters
11. **Has Fragment**: Presence of URL fragment

### Training Data
- **77 total samples**: 32 safe URLs, 45 phishing URLs
- **100% training accuracy** with Random Forest classifier
- **Feature importance**: URL Length (22.6%), Hyphen Count (16.4%), Path Length (15.6%)

## 🛡️ Security Features

### UFW Firewall Integration
- Automatic IP blocking for detected threats
- Database logging of all blocked IPs
- Admin interface for IP unblocking
- Cross-platform compatibility (simulates on Windows)

### GeoIP Analysis
- Country-based risk assessment
- Flagged countries: Russia (RU), China (CN), Iran (IR), North Korea (KP)
- Real-time geographic threat analysis

### Two-Tier Defense
1. **Keyword Filtering**: Pre-screening for common phishing terms
2. **ML Classification**: Advanced pattern recognition

## 📈 Monitoring & Analytics

### Real-time Metrics
- Total blocked IPs
- Currently active blocks
- Geographic threat distribution
- System performance metrics

### Admin Controls
- View all blocked IPs
- Unblock specific addresses
- Country-based statistics
- System health monitoring

## 🔧 Configuration

### Environment Variables
```bash
# Optional: GeoIP database path
GEOIP_DB_PATH=GeoLite2-City.mmdb

# Optional: Flask debug mode
FLASK_DEBUG=True
```

### UFW Configuration
```bash
# Enable UFW (Linux only)
sudo ufw enable

# Check status
sudo ufw status
```

## 🧪 Testing

### Test URLs
- **Safe**: `https://google.com`, `https://github.com`
- **Phishing**: `http://fake-bank-site.com/login?redirect=steal`

### API Endpoints
- `POST /check_url`: Check URL for phishing
- `GET /api/stats`: Get system statistics
- `GET /api/blocked_ips`: List blocked IPs
- `POST /api/unblock_ip`: Unblock specific IP

## 🚨 Troubleshooting

### Common Issues

1. **Flask API not responding**
   - Ensure port 5000 is available
   - Check firewall settings
   - Verify Python dependencies

2. **UFW commands failing**
   - Run with sudo privileges
   - Check UFW installation
   - Verify firewall rules

3. **GeoIP not working**
   - Download GeoLite2 database
   - Check file permissions
   - Verify database path

## 📝 API Documentation

### Check URL
```bash
curl -X POST http://localhost:5000/check_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Get Statistics
```bash
curl http://localhost:5000/api/stats
```

### Unblock IP
```bash
curl -X POST http://localhost:5000/api/unblock_ip \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.1.1"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- Scikit-learn for machine learning capabilities
- Flask for web framework
- Streamlit for dashboard interface
- MaxMind for GeoIP database
- UFW for firewall integration

---

**⚠️ Security Notice**: This tool is for educational and research purposes. Always verify results and use additional security measures in production environments.
