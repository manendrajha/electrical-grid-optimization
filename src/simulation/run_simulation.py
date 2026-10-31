
import pandas as pd

from src.simulation.energy_simulator import (
    conventional_grid_step,
    optimized_grid_step,
    INITIAL_BATTERY_LEVEL_MWH
)


def run_simulation(data, forecast_results):
    """
    Compare conventional and forecast-guided energy management.

    Both strategies receive identical actual demand and renewable
    generation. The optimized strategy additionally uses the
    one-hour-ahead demand forecast.
    """

    # Match forecasts to the timestamps they predict
    data = data.copy()
    forecasts = forecast_results[
        ["Timestamp", "Forecast_Demand"]
    ].copy()

    data["Timestamp"] = pd.to_datetime(data["Timestamp"])
    forecasts["Timestamp"] = pd.to_datetime(forecasts["Timestamp"])

    simulation_data = data.merge(
        forecasts,
        on="Timestamp",
        how="inner"
    )

    simulation_data = simulation_data.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    results = []

    battery_level = INITIAL_BATTERY_LEVEL_MWH

    for _, row in simulation_data.iterrows():

        demand = float(row["Demand (MW)"])
        wind = float(row["Wind (MW)"])
        solar = float(row["Solar (MW)"])
        forecast_demand = float(row["Forecast_Demand"])

        # Strategy 1: Conventional grid
        conventional = conventional_grid_step(
            demand=demand,
            wind=wind,
            solar=solar
        )

        # Strategy 2: Forecast-guided battery dispatch
        optimized = optimized_grid_step(
            demand=demand,
            wind=wind,
            solar=solar,
            battery_level=battery_level,
            forecast_demand=forecast_demand
        )

        # Carry battery state into the next hour
        battery_level = optimized["battery_level"]

        result = {
            "Timestamp": row["Timestamp"],
            "forecast_demand": forecast_demand
        }

        for key, value in conventional.items():
            result[f"conventional_{key}"] = value

        for key, value in optimized.items():
            result[f"optimized_{key}"] = value

        results.append(result)

    return pd.DataFrame(results)
