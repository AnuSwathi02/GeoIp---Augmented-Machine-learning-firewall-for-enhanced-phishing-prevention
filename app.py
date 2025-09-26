from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
from urllib.parse import urlparse

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

# Extract features from a given URL
def extract_features(url):
    parsed = urlparse(url)
    return [
        len(url),                     # Full URL length
        len(parsed.netloc),            # Domain length
        url.count('.'),                # Dot count
        int(url.startswith('https'))  # HTTPS flag
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

    # GeoIP Check
    country_code = get_geo_location(ip)
    risky_countries = ['RU', 'CN', 'IR', 'KP']
    geo_flagged = country_code in risky_countries if country_code else False

    # HERE is the key change: check keywords FIRST
    if is_phishing_keyword_present(url):
        result = 'phishing'
    else:
        # If no phishing keywords found, use the ML model prediction
        features = extract_features(url)
        prediction = model.predict([features])[0]
        result = 'phishing' if prediction == 1 else 'safe'

    return jsonify({
        'url': url,
        'country': country_code,
        'geoFlagged': geo_flagged,
        'mlResult': result
    })

# Run the server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
