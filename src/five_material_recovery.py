
from pathlib import Path
from collections import defaultdict
import csv

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results/component_inventory.csv"
OUTPUT = ROOT / "results/five_material_recovery.csv"

# Illustrative mg of material per detected component.
# NOT measured or literature-validated composition data.
MATERIAL_MG = {
    "IC": {"gold": 0.02, "palladium": 0.005},
    "LED": {"gallium": 0.01, "indium": 0.005},
    "capacitor": {"tantalum": 0.5, "palladium": 0.01},
    "connector": {"gold": 0.01, "palladium": 0.005},
}

# Illustrative recovery efficiencies.
RECOVERY_RATE = {
    "gallium": 0.50,
    "tantalum": 0.70,
    "palladium": 0.75,
    "gold": 0.80,
    "indium": 0.50,
}

totals = defaultdict(float)
images = set()

with INPUT.open(newline="") as file:
    for row in csv.DictReader(file):
        images.add(row["image"])
        component = row["component"].strip()

        for material, mass in MATERIAL_MG.get(component, {}).items():
            totals[material] += mass * RECOVERY_RATE[material]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["material", "estimated_recovered_mg"])

    for material in RECOVERY_RATE:
        writer.writerow([material, round(totals[material], 6)])

print("\nILLUSTRATIVE FIVE-MATERIAL RECOVERY ESTIMATES")

for material in RECOVERY_RATE:
    print(f"{material}: {totals[material]:.4f} mg")

print(f"\nImages analyzed: {len(images)}")
print(f"Saved to: {OUTPUT}")
print("NOTE: Results are hypothetical estimates, not measured recovery.")
