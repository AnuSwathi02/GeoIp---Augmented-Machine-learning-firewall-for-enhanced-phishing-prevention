from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
from urllib.parse import urlparse
import subprocess
import socket
import sqlite3
import datetime
import os

# Optional GeoIP import
try:
    import geoip2.database
    geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
except:
    geoip_reader = None  # GeoIP not available

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS

# Load the phishing detection model
model = joblib.load('phishing_model.pkl')

# Initialize database
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

# Initialize database on startup
init_database()

# UFW Firewall Functions
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

def unblock_ip_with_ufw(ip_address):
    """Unblock IP using UFW firewall (Linux) or Windows Firewall (Windows)"""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "linux":
            # Linux UFW commands
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("UFW not available, simulating unblock")
                return True
            
            # Unblock the IP
            subprocess.run(['sudo', 'ufw', 'delete', 'deny', 'from', ip_address], 
                          check=True, capture_output=True)
        elif system == "windows":
            # Windows Firewall commands
            try:
                # Use netsh to remove firewall rule
                subprocess.run([
                    'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                    f'name=Block_IP_{ip_address}'
                ], check=True, capture_output=True)
                print(f"Successfully unblocked IP {ip_address} using Windows Firewall")
            except subprocess.CalledProcessError:
                print(f"Windows Firewall unblock failed, simulating unblock for IP {ip_address}")
        else:
            print(f"Unsupported OS: {system}, simulating unblock for IP {ip_address}")
        
        # Update database (always do this regardless of OS)
        conn = sqlite3.connect('firewall_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE blocked_ips 
            SET unblocked_at = CURRENT_TIMESTAMP 
            WHERE ip_address = ? AND unblocked_at IS NULL
        ''', (ip_address,))
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error unblocking IP {ip_address}: {e}")
        # Still update database even if firewall command fails
        try:
            conn = sqlite3.connect('firewall_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE blocked_ips 
                SET unblocked_at = CURRENT_TIMESTAMP 
                WHERE ip_address = ? AND unblocked_at IS NULL
            ''', (ip_address,))
            conn.commit()
            conn.close()
        except:
            pass
        return False

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

# Extract 11 advanced features from a given URL
def extract_features(url):
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

# Add this helper function BELOW extract_features (paste here)
def is_phishing_keyword_present(url):
    phishing_keywords = ['login', 'secure', 'account', 'verify', 'update', 'password', 'bank', 'confirm']
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in phishing_keywords)

# Get country code from IP address (optional)
def get_geo_location(ip_address):
    if geoip_reader is None:
        return None
    try:
        response = geoip_reader.city(ip_address)
        return response.country.iso_code
    except Exception:
        return None

# Serve frontend
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint for checking URL
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

# Admin interface routes
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/blocked_ips')
def get_blocked_ips():
    conn = sqlite3.connect('firewall_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ip_address, url, country, blocked_at, unblocked_at 
        FROM blocked_ips 
        ORDER BY blocked_at DESC
    ''')
    ips = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'ip_address': ip[0],
        'url': ip[1],
        'country': ip[2],
        'blocked_at': ip[3],
        'unblocked_at': ip[4]
    } for ip in ips])

@app.route('/api/unblock_ip', methods=['POST'])
def unblock_ip():
    data = request.json
    ip_address = data.get('ip_address')
    
    if not ip_address:
        return jsonify({'success': False, 'error': 'IP address required'})
    
    success = unblock_ip_with_ufw(ip_address)
    return jsonify({'success': success})

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('firewall_logs.db')
    cursor = conn.cursor()
    
    # Get total blocked IPs
    cursor.execute('SELECT COUNT(*) FROM blocked_ips')
    total_blocked = cursor.fetchone()[0]
    
    # Get currently blocked IPs
    cursor.execute('SELECT COUNT(*) FROM blocked_ips WHERE unblocked_at IS NULL')
    currently_blocked = cursor.fetchone()[0]
    
    # Get blocked by country
    cursor.execute('''
        SELECT country, COUNT(*) 
        FROM blocked_ips 
        WHERE unblocked_at IS NULL 
        GROUP BY country 
        ORDER BY COUNT(*) DESC
    ''')
    country_stats = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'total_blocked': total_blocked,
        'currently_blocked': currently_blocked,
        'country_stats': [{'country': c[0], 'count': c[1]} for c in country_stats]
    })

# Run the server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
