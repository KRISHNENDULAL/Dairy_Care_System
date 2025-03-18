import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Load dataset
file_path = "sales_data.csv"  # Update this path if necessary
df = pd.read_csv(file_path)

# Features and target variable
X = df[['stock', 'supplier_price', 'demand', 'season', 'reviews', 'competitor_price']]
y = df['price']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Save trained model
with open('market_pricing_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model training complete. Model saved as 'market_pricing_model.pkl'.")
