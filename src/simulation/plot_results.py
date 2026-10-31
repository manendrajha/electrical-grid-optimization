import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_results(results, optimal_dispatch):

    output_dir = Path("reports/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamps = results["Timestamp"]

    baseline = results["conventional_grid_import"]

    heuristic = results["optimized_grid_import"]

    optimizer = optimal_dispatch["grid_import"]

    # 1. Grid import comparison
    plt.figure(figsize=(15, 6))

    plt.plot(
        timestamps, baseline,
        label="Conventional Grid",
        alpha=0.8
    )

    plt.plot(
        timestamps, heuristic,
        label="Forecast-guided Heuristic",
        alpha=0.8
    )

    plt.plot(
        timestamps, optimizer,
        label="Linear Programming Optimizer",
        alpha=0.8
    )

    plt.title("Grid Import Comparison")
    plt.xlabel("Timestamp")
    plt.ylabel("Grid Import (MW)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_dir / "grid_import_comparison.png", dpi=300)
    plt.show()

    # 2. Battery state of charge
    plt.figure(figsize=(15, 5))

    plt.plot(
        timestamps,
        optimal_dispatch["battery_level"],
        label="Optimized Battery SOC"
    )

    plt.axhline(
        25000,
        linestyle="--",
        label="Maximum Capacity"
    )

    plt.axhline(
        2500,
        linestyle=":",
        label="Initial / Final SOC"
    )

    plt.title("Optimized Battery State of Charge")
    plt.xlabel("Timestamp")
    plt.ylabel("Stored Energy (MWh)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_dir / "battery_state_of_charge.png", dpi=300)
    plt.show()

    # 3. Peak grid import comparison
    peak_values = [
        baseline.max(),
        heuristic.max(),
        optimizer.max()
    ]

    labels = [
        "Conventional",
        "Heuristic",
        "Linear Optimizer"
    ]

    plt.figure(figsize=(10, 6))

    bars = plt.bar(labels, peak_values)

    plt.title("Peak Grid Import Comparison")
    plt.ylabel("Peak Grid Import (MW)")
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, peak_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,.0f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(output_dir / "peak_import_comparison.png", dpi=300)
    plt.show()

    print("All visualizations saved to:", output_dir)


if __name__ == "__main__":
    print("Import this module from your notebook to generate plots.")