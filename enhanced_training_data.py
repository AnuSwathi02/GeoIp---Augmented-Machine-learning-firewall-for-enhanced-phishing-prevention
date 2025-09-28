from sklearn.ensemble import RandomForestClassifier
import joblib
import random

# Enhanced training data with 11 features
# Format: [url_len, domain_len, dots, https, hyphens, underscores, slashes, path_len, has_at, has_query, has_fragment]

# Safe URLs (label = 0)
safe_urls = [
    # Google services
    [45, 12, 2, 1, 0, 0, 2, 5, 0, 0, 0],   # https://google.com/search
    [52, 12, 2, 1, 0, 0, 2, 8, 0, 0, 0],   # https://google.com/maps
    [48, 12, 2, 1, 0, 0, 2, 6, 0, 0, 0],   # https://google.com/gmail
    [50, 12, 2, 1, 0, 0, 2, 7, 0, 0, 0],   # https://google.com/drive
    
    # Social media
    [35, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://facebook.com
    [33, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://twitter.com
    [34, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://linkedin.com
    [32, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://instagram.com
    
    # News and information
    [38, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://wikipedia.org
    [36, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://reddit.com
    [40, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://stackoverflow.com
    
    # E-commerce
    [35, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://amazon.com
    [37, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://ebay.com
    [39, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://shopify.com
    
    # Banking and finance
    [42, 12, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://paypal.com
    [40, 12, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://stripe.com
    [38, 12, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://visa.com
    
    # Technology
    [36, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://github.com
    [38, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://microsoft.com
    [35, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://apple.com
    
    # Educational
    [40, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://coursera.org
    [38, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://edx.org
    [42, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://khanacademy.org
    
    # Government
    [35, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://irs.gov
    [37, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://ssa.gov
    [39, 11, 2, 1, 0, 0, 1, 0, 0, 0, 0],   # https://usps.com
    
    # Short URLs
    [25, 8, 1, 1, 0, 0, 1, 0, 0, 0, 0],    # https://bit.ly
    [27, 8, 1, 1, 0, 0, 1, 0, 0, 0, 0],    # https://tinyurl.com
    [26, 8, 1, 1, 0, 0, 1, 0, 0, 0, 0],    # https://goo.gl
    
    # HTTP (non-secure but legitimate)
    [33, 11, 2, 0, 0, 0, 1, 0, 0, 0, 0],   # http://example.com
    [35, 11, 2, 0, 0, 0, 1, 0, 0, 0, 0],   # http://test.com
    [37, 11, 2, 0, 0, 0, 1, 0, 0, 0, 0],   # http://demo.com
]

# Phishing URLs (label = 1)
phishing_urls = [
    # Fake banking sites
    [78, 15, 3, 0, 2, 1, 3, 8, 0, 1, 0],   # http://fake-bank-site.com/login?redirect=steal
    [85, 18, 4, 1, 3, 2, 4, 10, 0, 1, 0],  # https://suspicious-bank-verification.com/account/verify?token=steal
    [92, 20, 4, 0, 4, 1, 3, 12, 0, 1, 0],  # http://very-long-fake-bank-name.com/secure/login?phish=yes
    
    # Fake social media
    [88, 16, 3, 1, 2, 2, 3, 9, 0, 1, 0],   # https://fake-facebook-login.com/account/verify?steal=data
    [95, 19, 4, 0, 3, 1, 4, 11, 0, 1, 0],  # http://suspicious-twitter-clone.com/login/secure?phish=yes
    [82, 17, 3, 1, 2, 2, 3, 8, 0, 1, 0],   # https://fake-instagram-verification.com/account/update?steal=info
    
    # Fake payment sites
    [90, 18, 4, 1, 3, 1, 4, 10, 0, 1, 0],  # https://fake-paypal-verification.com/account/secure?phish=yes
    [87, 16, 3, 0, 2, 2, 3, 9, 0, 1, 0],   # http://suspicious-stripe-clone.com/login/verify?steal=data
    [93, 20, 4, 1, 4, 1, 4, 11, 0, 1, 0],  # https://very-long-fake-payment-site.com/account/secure?phish=yes
    
    # Fake government sites
    [89, 17, 3, 1, 2, 2, 3, 10, 0, 1, 0],  # https://fake-irs-verification.com/account/update?steal=info
    [91, 19, 4, 0, 3, 1, 4, 11, 0, 1, 0],  # http://suspicious-ssa-clone.com/login/secure?phish=yes
    [86, 16, 3, 1, 2, 2, 3, 9, 0, 1, 0],   # https://fake-usps-verification.com/account/verify?steal=data
    
    # URLs with suspicious characters
    [95, 22, 5, 1, 5, 3, 5, 12, 1, 1, 1],  # https://very-suspicious-site-name.com/verify/account#steal?phish=yes@fake
    [88, 18, 4, 0, 4, 2, 4, 10, 1, 1, 0],  # http://fake-site-with-many-dashes.com/login/secure@phish?steal=yes
    [92, 20, 4, 1, 3, 3, 4, 11, 0, 1, 1],  # https://suspicious-site-with-underscores.com/account/verify?phish=yes#steal
    
    # Very long suspicious URLs
    [120, 25, 6, 1, 6, 4, 6, 15, 1, 1, 1], # https://extremely-long-suspicious-site-name.com/very/long/path/verify?phish=yes#steal@fake
    [115, 23, 5, 0, 5, 3, 5, 14, 1, 1, 0], # http://very-long-fake-site-name.com/long/path/login?steal=yes@phish
    [125, 26, 6, 1, 7, 4, 6, 16, 0, 1, 1], # https://extremely-suspicious-very-long-site.com/account/verify/secure?phish=yes#steal
    
    # URLs with many query parameters
    [98, 19, 4, 1, 3, 2, 4, 12, 0, 1, 0],  # https://fake-site.com/account/verify?param1=steal&param2=phish&param3=yes
    [105, 21, 5, 0, 4, 2, 5, 13, 0, 1, 0], # http://suspicious-site.com/login/secure?steal=data&phish=yes&fake=info
    [102, 20, 4, 1, 3, 3, 4, 12, 0, 1, 0], # https://fake-verification-site.com/account/update?steal=info&phish=yes&fake=data
    
    # URLs with fragments
    [89, 17, 3, 1, 2, 2, 3, 10, 0, 0, 1],  # https://fake-site.com/account/verify#steal
    [94, 19, 4, 0, 3, 2, 4, 11, 0, 0, 1],  # http://suspicious-site.com/login/secure#phish
    [91, 18, 3, 1, 2, 2, 3, 10, 0, 0, 1],  # https://fake-verification.com/account/update#steal
    
    # Mixed suspicious patterns
    [96, 20, 4, 1, 4, 2, 4, 11, 1, 1, 1],  # https://fake-site-with-many-features.com/verify/account@phish?steal=yes#fake
    [87, 16, 3, 0, 3, 1, 3, 9, 1, 1, 0],   # http://suspicious-site.com/login@fake?phish=yes
    [93, 19, 4, 1, 3, 3, 4, 10, 0, 1, 1],  # https://fake-verification-site.com/account/secure?steal=yes#phish
    
    # Short but suspicious
    [65, 12, 2, 0, 2, 1, 2, 8, 0, 1, 0],   # http://fake-bank.com/login?phish=yes
    [68, 13, 2, 1, 2, 1, 2, 9, 0, 1, 0],   # https://phish-site.com/verify?steal=yes
    [70, 14, 3, 0, 2, 1, 3, 8, 0, 1, 0],   # http://fake-pay.com/login?phish=yes
    
    # URLs with many dots
    [85, 22, 6, 1, 2, 1, 3, 9, 0, 1, 0],   # https://fake.site.with.many.dots.com/login?phish=yes
    [88, 24, 7, 0, 2, 1, 3, 10, 0, 1, 0],  # http://very.suspicious.site.with.many.dots.com/verify?steal=yes
    [82, 20, 5, 1, 2, 1, 3, 8, 0, 1, 0],   # https://fake.site.with.dots.com/account?phish=yes
    
    # URLs with many hyphens
    [90, 18, 3, 1, 6, 1, 3, 9, 0, 1, 0],   # https://fake-site-with-many-hyphens.com/login?phish=yes
    [95, 20, 4, 0, 7, 1, 4, 10, 0, 1, 0],  # http://very-suspicious-site-with-hyphens.com/verify?steal=yes
    [88, 16, 3, 1, 5, 1, 3, 8, 0, 1, 0],   # https://fake-bank-site-with-hyphens.com/account?phish=yes
    
    # URLs with many underscores
    [89, 17, 3, 1, 1, 5, 3, 9, 0, 1, 0],   # https://fake_site_with_many_underscores.com/login?phish=yes
    [92, 19, 4, 0, 1, 6, 4, 10, 0, 1, 0],  # http://suspicious_site_with_underscores.com/verify?steal=yes
    [86, 15, 3, 1, 1, 4, 3, 8, 0, 1, 0],   # https://fake_bank_site_underscores.com/account?phish=yes
    
    # URLs with many slashes
    [94, 16, 3, 1, 2, 1, 6, 12, 0, 1, 0],  # https://fake-site.com/very/long/path/to/login?phish=yes
    [97, 18, 4, 0, 2, 1, 7, 13, 0, 1, 0],  # http://suspicious-site.com/account/verify/secure/login?steal=yes
    [91, 15, 3, 1, 2, 1, 5, 11, 0, 1, 0],  # https://fake-bank.com/account/verify/update?phish=yes
    
    # URLs with @ symbols
    [78, 15, 3, 1, 2, 1, 3, 8, 1, 1, 0],   # https://fake-site.com/login@phish?steal=yes
    [82, 17, 3, 0, 2, 1, 3, 9, 1, 1, 0],   # http://suspicious-site.com/verify@fake?phish=yes
    [85, 18, 4, 1, 2, 1, 4, 9, 1, 1, 0],   # https://fake-bank-site.com/account@steal?phish=yes
]

# Combine all data
X = safe_urls + phishing_urls
y = [0] * len(safe_urls) + [1] * len(phishing_urls)

# Shuffle the data
combined = list(zip(X, y))
random.shuffle(combined)
X, y = zip(*combined)
X = list(X)
y = list(y)

print(f"Training dataset created with {len(X)} samples:")
print(f"- Safe URLs: {len(safe_urls)}")
print(f"- Phishing URLs: {len(phishing_urls)}")
print(f"- Features per sample: {len(X[0])}")

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'phishing_model.pkl')
print("✅ Enhanced phishing_model.pkl saved with realistic dataset")

# Test the model
test_accuracy = model.score(X, y)
print(f"✅ Model accuracy on training data: {test_accuracy:.2%}")

# Show feature importance
feature_names = [
    'URL Length', 'Domain Length', 'Dot Count', 'HTTPS Flag',
    'Hyphen Count', 'Underscore Count', 'Slash Count', 'Path Length',
    'Has @ Symbol', 'Has Query Params', 'Has Fragment'
]

print("\nFeature Importance:")
for name, importance in zip(feature_names, model.feature_importances_):
    print(f"- {name}: {importance:.3f}")
