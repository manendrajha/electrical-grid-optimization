
# Simulation parameters
BATTERY_CAPACITY_MWH = 25000

MAX_CHARGE_POWER_MW = 5000
MAX_DISCHARGE_POWER_MW = 5000

CHARGING_EFFICIENCY = 0.95
DISCHARGING_EFFICIENCY = 0.95

INITIAL_BATTERY_LEVEL_MWH = 2500

GRID_IMPORT_LIMIT_MW = 220000

PEAK_THRESHOLD_MW = 198293.31


def conventional_grid_step(demand, wind, solar):
    """
    Conventional strategy:
    Renewable generation is used first.
    Remaining demand is supplied by the grid.
    """

    renewable_available = wind + solar
    renewable_used = min(demand, renewable_available)

    net_demand = demand - renewable_used

    grid_import = min(net_demand, GRID_IMPORT_LIMIT_MW)
    unmet_demand = max(0, net_demand - grid_import)

    renewable_curtailed = renewable_available - renewable_used

    return {
        "demand": demand,
        "renewable_available": renewable_available,
        "renewable_used": renewable_used,
        "grid_import": grid_import,
        "unmet_demand": unmet_demand,
        "renewable_curtailed": renewable_curtailed
    }


def optimized_grid_step(
    demand,
    wind,
    solar,
    battery_level,
    forecast_demand
):
    """
    Forecast-guided battery dispatch.

    The forecast determines whether to charge or discharge.
    Actual demand determines the energy balance.
    Grid electricity used for charging is included in grid imports.
    """

    renewable_available = wind + solar
    renewable_used = min(demand, renewable_available)

    actual_net_demand = demand - renewable_used

    forecast_net_demand = max(
        0,
        forecast_demand - wind - solar
    )

    battery_charged = 0
    battery_discharged = 0

    # Forecast indicates an upcoming peak: discharge
    if forecast_net_demand > PEAK_THRESHOLD_MW:

        required_discharge = (
            forecast_net_demand - PEAK_THRESHOLD_MW
        )

        available_energy = (
            battery_level * DISCHARGING_EFFICIENCY
        )

        battery_discharged = min(
            required_discharge,
            MAX_DISCHARGE_POWER_MW,
            available_energy,
            actual_net_demand
        )

        battery_level -= (
            battery_discharged / DISCHARGING_EFFICIENCY
        )

    # Forecast indicates lower demand: charge
    else:

        available_capacity = (
            BATTERY_CAPACITY_MWH - battery_level
        )

        forecast_headroom = (
            PEAK_THRESHOLD_MW - forecast_net_demand
        )

        actual_grid_headroom = max(
            0,
            GRID_IMPORT_LIMIT_MW - actual_net_demand
        )

        battery_charged = min(
            forecast_headroom,
            actual_grid_headroom,
            MAX_CHARGE_POWER_MW,
            available_capacity / CHARGING_EFFICIENCY
        )

        battery_level += (
            battery_charged * CHARGING_EFFICIENCY
        )

    # Calculate actual grid requirement.
    # Charging consumes grid electricity.
    # Discharging supplies part of the actual demand.
    required_grid_import = (
        actual_net_demand
        - battery_discharged
        + battery_charged
    )

    grid_import = min(
        required_grid_import,
        GRID_IMPORT_LIMIT_MW
    )

    unmet_demand = max(
        0,
        required_grid_import - grid_import
    )

    return {
        "demand": demand,
        "renewable_available": renewable_available,
        "renewable_used": renewable_used,
        "forecast_net_demand": forecast_net_demand,
        "battery_charged": battery_charged,
        "battery_discharged": battery_discharged,
        "battery_level": battery_level,
        "grid_import": grid_import,
        "unmet_demand": unmet_demand,
        "renewable_curtailed": renewable_available - renewable_used
    }
