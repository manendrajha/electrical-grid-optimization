# Electrical Grid Optimization

A data-driven smart energy management system for analyzing electricity demand, forecasting short-term consumption, and evaluating battery-assisted grid optimization strategies.

The project combines machine learning, battery energy storage simulation, and linear programming to investigate how intelligent energy management can reduce peak grid demand.

## Overview

Electricity demand fluctuates throughout the day, creating periods of high grid loading. Integrating renewable energy and battery energy storage can help manage these fluctuations and improve grid utilization.

This project uses historical Indian national-grid data to simulate and compare three grid-management strategies:

1. **Conventional Grid:** Renewable generation is utilized first, with the remaining demand supplied by the grid.
2. **Forecast Heuristic:** A Random Forest demand forecasting model informs battery charging and discharging decisions.
3. **Linear Optimization:** A linear programming model optimizes battery dispatch to minimize peak grid import using actual demand over the evaluation horizon.

An interactive Streamlit dashboard provides visualizations and allows users to explore the simulation results.

## Key Features

- Historical electricity demand and renewable generation analysis.
- One-hour-ahead electricity demand forecasting using Random Forest.
- Forecast-guided battery charging and discharging.
- Linear programming-based battery dispatch optimization.
- Comparison of conventional, heuristic, and optimized grid operation.
- Battery state-of-charge and energy-flow visualization.
- Interactive grid simulation.
- Performance analytics and CSV data export.

## System Architecture

```text
Historical Grid Dataset
         |
         v
 Data Preprocessing
         |
         +----------------------+
         |                      |
         v                      v
 Demand Forecasting       Energy Data
 (Random Forest)           Analysis
         |
         v
 Forecast-Guided
 Battery Controller
         |
         v
 Heuristic Simulation

Historical Demand
         |
         v
Linear Programming
  Optimization
         |
         v
Optimized Dispatch

         |
         v
 Strategy Comparison
         |
         v
 Streamlit Dashboard
```

## Methodology

### 1. Data Processing

Historical hourly electricity data is processed to prepare demand, wind generation, and solar generation measurements for analysis and simulation.

The dataset contains:

- Timestamp
- Demand (MW)
- Wind Generation (MW)
- Solar Generation (MW)
- Total Generation (MW)

### 2. Demand Forecasting

A Random Forest Regressor is used to predict electricity demand one hour ahead.

The model uses temporal features, previous demand observations, and current renewable generation measurements.

**Model configuration:**
- Algorithm: Random Forest Regressor
- Number of estimators: 100
- Maximum depth: 15
- Train-test split: Chronological 80:20

**Held-out test performance:**

| Metric | Result |
|---|---:|
| MAE | 2,451.51 MW |
| RMSE | 3,820.39 MW |
| R² | 0.9244 |

### 3. Forecast-Guided Battery Management

A heuristic battery controller uses predicted demand to determine when the battery should charge or discharge.

The simulation considers battery capacity, maximum charging and discharging power, efficiency, and grid operating constraints.

### 4. Linear Programming Optimization

A linear programming model is implemented using SciPy to optimize battery dispatch and minimize maximum grid import over the evaluation horizon.

The optimization considers:

- Battery state-of-charge constraints.
- Charging and discharging power limits.
- Battery energy balance.
- Initial and final state-of-charge constraints.
- Grid import peak minimization.

The linear optimizer uses actual demand over the complete evaluation horizon. It therefore serves as an offline perfect-information benchmark rather than a real-time controller.

## Experimental Results

The following results were obtained over the chronological held-out evaluation period.

| Performance Metric | Conventional | Forecast Heuristic | Linear Optimizer |
|---|---:|---:|---:|
| Peak Grid Import (MW) | 218,515.53 | 214,950.07 | 213,515.53 |
| Peak Reduction | — | 1.63% | 2.29% |

### Forecasting Performance

| Metric | Value |
|---|---:|
| MAE | 2,451.51 MW |
| RMSE | 3,820.39 MW |
| R² | 0.9244 |

The results demonstrate the potential of battery-assisted energy management to reduce peak grid import. The linear programming approach provides an offline benchmark for evaluating the heuristic controller.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Optimization | SciPy |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Data Visualization | Matplotlib, Seaborn |
| Model Persistence | Joblib |

## Project Structure

```text
electrical-grid-optimization/
│
├── assets/
│   └── smart_city.png
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── energy_data.csv
│       ├── optimized_dispatch_results.csv
│       └── heuristic_simulation_results.csv
│
├── models/
│   └── trained/
│       └── random_forest.joblib
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   ├── forecasting/
│   ├── simulation/
│   ├── optimization/
│   └── dashboard/
│
├── app.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.11
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/manendrajha/electrical-grid-optimization.git

cd electrical-grid-optimization
```

### 2. Create a Virtual Environment

```bash
python3.11 -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Project Data

Place the required processed datasets and trained model in their respective directories, following the project structure above.

The historical source dataset should be placed in the appropriate raw-data directory if preprocessing needs to be repeated.

### 5. Run the Dashboard

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Dashboard Modules

The application contains six primary sections:

- **Overview:** System performance KPIs and strategy comparison.
- **Demand Analytics:** Demand trends, renewable generation, and forecast evaluation.
- **Energy Management:** Comparison of grid-management strategies.
- **Battery Operations:** Battery state-of-charge and charging/discharging analysis.
- **Grid Simulator:** Interactive visualization of hourly energy flows.
- **Data Explorer:** Dataset inspection, filtering, and CSV export.

## Limitations

- The project uses historical grid observations rather than live grid telemetry.
- The heuristic controller uses forecast-based decisions, with actual target-hour renewable generation used as a simulation proxy.
- The linear programming optimizer uses future actual demand and is an offline benchmark, not a real-time deployable controller.
- Battery operation is evaluated using simplified simulation assumptions and does not represent a complete physical battery model.

## Future Improvements

- Integrate short-term renewable generation forecasting.
- Develop more advanced predictive battery control strategies.
- Evaluate optimization under forecast uncertainty.
- Incorporate real-time grid data and streaming infrastructure.
- Extend the simulation to multiple distributed energy storage systems.

## Disclaimer

This project is an academic simulation and research-oriented prototype. It is not intended for direct control of real-world electrical grid infrastructure.