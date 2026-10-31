import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from src.forecasting.feature_engineering import create_features


# Project paths
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "processed" / "energy_data.csv"
MODEL_PATH = ROOT_DIR / "models" / "trained" / "random_forest.joblib"


def train():

    # Load processed dataset
    data = pd.read_csv(DATA_PATH)

    # Generate features and target
    X, y = create_features(data)

    # Chronological 80/20 split
    split_index = int(len(X) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    # Initialize and train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Evaluate
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model training completed!")
    print(f"MAE:  {mae:,.2f} MW")
    print(f"RMSE: {rmse:,.2f} MW")
    print(f"R²:   {r2:.4f}")
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    train()