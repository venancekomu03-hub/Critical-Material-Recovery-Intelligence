
from pathlib import Path
from collections import Counter
import csv

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results/component_inventory.csv"
OUTPUT = ROOT / "results"

# Illustrative baseline assumptions for each material.
# Component counts come from actual model detections.
PARAMETERS = {
    "gallium": {
        "component": "LED",
        "presence": 0.80,
        "mass_mg": 0.01,
        "recovery": 0.50,
    },
    "tantalum": {
        "component": "capacitor",
        "presence": 0.25,
        "mass_mg": 0.50,
        "recovery": 0.70,
    },
    "palladium": {
        "component": "capacitor",
        "presence": 0.20,
        "mass_mg": 0.01,
        "recovery": 0.75,
    },
    "gold": {
        "component": "IC",
        "presence": 0.70,
        "mass_mg": 0.02,
        "recovery": 0.80,
    },
    "indium": {
        "component": "LED",
        "presence": 0.50,
        "mass_mg": 0.005,
        "recovery": 0.50,
    },
}

with INPUT.open(newline="") as file:
    counts = Counter(
        row["component"].strip()
        for row in csv.DictReader(file)
    )

def estimate(count, presence, mass_mg, recovery):
    return count * presence * mass_mg * recovery

rows = []

for material, params in PARAMETERS.items():
    count = counts[params["component"]]

    baseline = estimate(
        count,
        params["presence"],
        params["mass_mg"],
        params["recovery"],
    )

    for parameter in ["presence", "mass_mg", "recovery"]:
        for change in [-0.20, 0.20]:
            modified = params.copy()
            modified[parameter] *= (1 + change)

            # Probabilities and efficiencies cannot exceed 1.
            if parameter in ["presence", "recovery"]:
                modified[parameter] = min(
                    1.0, modified[parameter]
                )

            result = estimate(
                count,
                modified["presence"],
                modified["mass_mg"],
                modified["recovery"],
            )

            percent_change = (
                100 * (result - baseline) / baseline
                if baseline != 0 else 0
            )

            rows.append({
                "material": material,
                "parameter": parameter,
                "input_change_pct": change * 100,
                "baseline_mg": baseline,
                "scenario_mg": result,
                "output_change_pct": percent_change,
            })

df = pd.DataFrame(rows)
OUTPUT.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT / "sensitivity_results.csv", index=False)

# Visualize tantalum scenarios.
subset = df[df["material"] == "tantalum"]

fig, ax = plt.subplots(figsize=(9, 5))

for parameter in ["presence", "mass_mg", "recovery"]:
    data = subset[subset["parameter"] == parameter]
    ax.plot(
        data["input_change_pct"],
        data["output_change_pct"],
        marker="o",
        label=parameter,
    )

ax.axhline(0, color="gray", linewidth=0.8)
ax.axvline(0, color="gray", linewidth=0.8)
ax.set_xlabel("Change in input parameter (%)")
ax.set_ylabel("Change in estimated recovered mass (%)")
ax.set_title("Tantalum Recovery: Local Sensitivity Analysis")
ax.legend()
ax.grid(alpha=0.2)

plt.tight_layout()
plt.savefig(
    OUTPUT / "sensitivity_analysis.png",
    dpi=300,
)
plt.show()

print("\nSENSITIVITY ANALYSIS COMPLETED")
print(df.round(4).to_string(index=False))
print("\nSaved sensitivity_results.csv")
print("Saved sensitivity_analysis.png")
print("NOTE: Model assumptions are illustrative.")
