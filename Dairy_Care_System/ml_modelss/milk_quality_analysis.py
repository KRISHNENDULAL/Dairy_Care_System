import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("milk_quality.csv")

# Separate features and target
X = df.drop(columns=["Quality"])
y = df["Quality"].map({"Good": 1, "Poor": 0})  # Convert to binary labels

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test data
y_pred = model.predict(X_test)

# Evaluate model accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(model, "milk_quality_model.pkl")

# Function for predicting milk quality based on user input
def predict_quality(ph, fat, density, temp):
    input_data = np.array([[ph, fat, density, temp]])
    prediction = model.predict(input_data)
    return "Good" if prediction[0] == 1 else "Poor"

# Example prediction
if __name__ == "__main__":
    sample_prediction = predict_quality(6.8, 4.5, 1030, 8)
    print(f"Predicted Milk Quality: {sample_prediction}")
