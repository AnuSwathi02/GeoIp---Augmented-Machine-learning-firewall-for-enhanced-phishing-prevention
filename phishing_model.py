from sklearn.ensemble import RandomForestClassifier
import joblib

# Sample training data: [URL length, domain length, dot count, is_https]
X = [
    [100, 15, 3, 1],
    [40, 10, 1, 0],
    [120, 20, 4, 1],
    [50, 12, 2, 0],
    [60, 8, 1, 1]
]
y = [1, 0, 1, 0, 0]  # Labels: 1 = phishing, 0 = safe

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save the model to a file
joblib.dump(model, 'phishing_model.pkl')
print("✅ phishing_model.pkl saved")
