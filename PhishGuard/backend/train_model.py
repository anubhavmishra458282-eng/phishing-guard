import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

np.random.seed(42)

benign = np.array([
    [25, 12, 1, 0, 1, 0, 0, 0, 0, 2.8, 1, 0],
    [32, 14, 2, 1, 2, 0, 0, 0, 1, 3.1, 1, 0],
    [40, 18, 1, 0, 3, 2, 0, 0, 0, 3.0, 1, 0],
    [22, 10, 1, 0, 1, 0, 0, 0, 0, 2.5, 1, 0],
    [45, 15, 2, 0, 4, 1, 0, 0, 1, 3.2, 1, 0],
    [28, 12, 1, 0, 2, 0, 0, 0, 0, 2.7, 1, 0]
])

phishing = np.array([
    [85, 38, 5, 3, 4, 8, 1, 0, 4, 4.3, 0, 1],
    [65, 15, 3, 0, 2, 12, 0, 1, 0, 3.8, 0, 1],
    [92, 45, 6, 4, 5, 6, 0, 0, 5, 4.5, 0, 1],
    [78, 35, 4, 2, 3, 5, 1, 0, 3, 4.1, 0, 1],
    [60, 28, 4, 2, 3, 4, 0, 0, 3, 3.9, 0, 1],
    [105, 50, 7, 5, 6, 14, 1, 1, 5, 4.8, 0, 1]
])

X = np.vstack([benign, phishing])
y = np.array([0] * len(benign) + [1] * len(phishing))

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

os.makedirs("app", exist_ok=True)
joblib.dump(model, "app/phishguard_rf.joblib")
print("Model trained and saved to app/phishguard_rf.joblib successfully!")
