
from pathlib import Path
from collections import Counter
import csv

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results/component_inventory.csv"
OUTPUT = ROOT / "results/monte_carlo_results.csv"

N_SIMULATIONS = 10000
rng = np.random.default_rng(42)

# Illustrative material masses in mg per component.
# These are hypothetical ranges, NOT measured compositions.
# Each tuple is (minimum, maximum).
MATERIAL_RANGES = {
    "IC": {
        "gold": (0.01, 0.03),
        "palladium": (0.0025, 0.0075),
    },
    "LED": {
        "gallium": (0.005, 0.015),
        "indium": (0.0025, 0.0075),
    },
    "capacitor": {
        "tantalum": (0.25, 0.75),
        "palladium": (0.005, 0.015),
    },
    "connector": {
        "gold": (0.005, 0.015),
        "palladium": (0.0025, 0.0075),
    },
}

# Illustrative ranges of recovery efficiency.
RECOVERY_RANGES = {
    "gallium": (0.35, 0.65),
    "tantalum": (0.50, 0.90),
    "palladium": (0.60, 0.90),
    "gold": (0.65, 0.95),
    "indium": (0.35, 0.65),
}

# Illustrative probability that a detected component
# actually contains the mapped material.
PRESENCE_PROBABILITIES = {
    "IC": {"gold": 0.70, "palladium": 0.30},
    "LED": {"gallium": 0.80, "indium": 0.50},
    "capacitor": {"tantalum": 0.25, "palladium": 0.20},
    "connector": {"gold": 0.60, "palladium": 0.30},
}

with INPUT.open(newline="") as file:
    rows = list(csv.DictReader(file))

counts = Counter(row["component"].strip() for row in rows)
results = {}

for material, (low_eff, high_eff) in RECOVERY_RANGES.items():
    simulated_mass = np.zeros(N_SIMULATIONS)

    for component, material_map in MATERIAL_RANGES.items():
        if material not in material_map:
            continue

        count = counts[component]
        if count == 0:
            continue

        low_mass, high_mass = material_map[material]
        presence = PRESENCE_PROBABILITIES[component][material]

        # Number of components containing the material
        present_counts = rng.binomial(
            count, presence, size=N_SIMULATIONS
        )

        # Simulate total material content across components
        # Conditional on presence, each component has a
        # uniformly distributed mass within the given range.
        masses = rng.uniform(
            low_mass,
            high_mass,
            size=(N_SIMULATIONS, count),
        )
        present = rng.random(
            size=(N_SIMULATIONS, count)
        ) < presence

        total_content = (masses * present).sum(axis=1)

        # Simulate recovery efficiency
        efficiency = rng.uniform(
            low_eff, high_eff, size=N_SIMULATIONS
        )

        simulated_mass += total_content * efficiency

    results[material] = simulated_mass

summary = []

for material, samples in results.items():
    summary.append({
        "material": material,
        "mean_mg": np.mean(samples),
        "p5_mg": np.percentile(samples, 5),
        "median_mg": np.median(samples),
        "p95_mg": np.percentile(samples, 95),
    })

df = pd.DataFrame(summary)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

print("\nMONTE CARLO RESULTS (10,000 SIMULATIONS)")
print(df.round(4).to_string(index=False))
print(f"\nSaved to: {OUTPUT}")
print("NOTE: All model inputs are illustrative assumptions.")
