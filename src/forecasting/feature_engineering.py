import pandas as pd


def create_features(data):
    """
    Prepare features for one-hour-ahead electricity demand forecasting.
    """

    df = data.copy()

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp").reset_index(drop=True)

    # Time-based features for the hour we want to predict
    future_time = df["Timestamp"] + pd.Timedelta(hours=1)

    df["Hour"] = future_time.dt.hour
    df["DayOfWeek"] = future_time.dt.dayofweek
    df["Month"] = future_time.dt.month

    # Historical demand features
    df["Demand_Lag_1"] = df["Demand (MW)"]
    df["Demand_Lag_24"] = df["Demand (MW)"].shift(23)

    # Current observed renewable generation
    df["Wind_Current"] = df["Wind (MW)"]
    df["Solar_Current"] = df["Solar (MW)"]

    # Target: demand one hour into the future
    df["Target"] = df["Demand (MW)"].shift(-1)

    # Select model inputs
    feature_columns = [
        "Hour",
        "DayOfWeek",
        "Month",
        "Demand_Lag_1",
        "Demand_Lag_24",
        "Wind_Current",
        "Solar_Current"
    ]

    # Remove rows without sufficient historical data or target
    df = df.dropna().reset_index(drop=True)

    X = df[feature_columns]
    y = df["Target"]

    return X, y