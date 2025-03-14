import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Load the dataset
csv_file_path = "sales_data.csv"  # Ensure the CSV file is in the same directory as this script
df = pd.read_csv(csv_file_path)

# Selecting features and target variable
X = df[['stock', 'supplier_price', 'demand', 'season', 'reviews', 'competitor_price']]
y = df['price']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model
with open("market_price_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model training complete. Saved as 'market_price_model.pkl'")
