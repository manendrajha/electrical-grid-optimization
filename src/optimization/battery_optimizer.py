import numpy as np
from scipy.optimize import linprog


def optimize_battery_dispatch(
    net_demand,
    capacity=25000,
    max_charge=5000,
    max_discharge=5000,
    initial_soc=2500,
    charge_efficiency=0.95,
    discharge_efficiency=0.95
):
    """
    Optimize battery dispatch to minimize peak grid imports.

    Uses linear programming with a cyclic battery constraint.
    All time intervals are assumed to be one hour.
    """

    demand = np.asarray(net_demand, dtype=float)
    n = len(demand)

    # Variables:
    # charge[0:n], discharge[0:n], soc[0:n], peak

    total_variables = 3 * n + 1

    charge_idx = np.arange(n)
    discharge_idx = np.arange(n, 2 * n)
    soc_idx = np.arange(2 * n, 3 * n)
    peak_idx = 3 * n

    # Objective: minimize peak grid import
    objective = np.zeros(total_variables)
    objective[peak_idx] = 1

    # Battery energy balance constraints
    A_eq = []
    b_eq = []

    for t in range(n):
        row = np.zeros(total_variables)

        row[soc_idx[t]] = 1
        row[charge_idx[t]] = -charge_efficiency
        row[discharge_idx[t]] = 1 / discharge_efficiency

        if t > 0:
            row[soc_idx[t - 1]] = -1
            rhs = 0
        else:
            rhs = initial_soc

        A_eq.append(row)
        b_eq.append(rhs)

    # Cyclic battery constraint
    terminal_row = np.zeros(total_variables)
    terminal_row[soc_idx[-1]] = 1

    A_eq.append(terminal_row)
    b_eq.append(initial_soc)

    # Grid import must not exceed optimized peak
    A_ub = []
    b_ub = []

    for t in range(n):
        row = np.zeros(total_variables)

        row[charge_idx[t]] = 1
        row[discharge_idx[t]] = -1
        row[peak_idx] = -1

        A_ub.append(row)
        b_ub.append(-demand[t])

    bounds = (
        [(0, max_charge)] * n +
        [(0, max_discharge)] * n +
        [(0, capacity)] * n +
        [(0, None)]
    )

    result = linprog(
        objective,
        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),
        A_eq=np.array(A_eq),
        b_eq=np.array(b_eq),
        bounds=bounds,
        method="highs"
    )

    if not result.success:
        raise RuntimeError(result.message)

    charge = result.x[charge_idx]
    discharge = result.x[discharge_idx]
    soc = result.x[soc_idx]

    grid_import = demand + charge - discharge

    return {
        "battery_charged": charge,
        "battery_discharged": discharge,
        "battery_level": soc,
        "grid_import": grid_import,
        "optimized_peak": result.x[peak_idx],
        "optimization_status": result.message
    }