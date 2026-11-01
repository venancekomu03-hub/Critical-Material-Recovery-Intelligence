
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results/component_inventory.csv"
OUTPUT = ROOT / "results/critical_material_screening.csv"

# Potential associations, NOT confirmed material composition.
ASSOCIATIONS = {
    "IC": ["gold", "palladium", "gallium"],
    "LED": ["gallium", "indium", "gold"],
    "capacitor": ["tantalum", "palladium"],
    "connector": ["gold", "palladium"],
    "diode": ["gallium"],
    "transistor": ["gallium"],
    "resistor": [],
    "potentiometer": [],
}

detections = pd.read_csv(INPUT)
detections["component"] = detections["component"].str.strip()

# Include every image represented in the inventory.
images = sorted(detections["image"].unique())
materials = ["gallium", "tantalum", "palladium", "gold", "indium"]

rows = []

for image in images:
    board = detections[detections["image"] == image]

    for material in materials:
        associated = board[
            board["component"].apply(
                lambda component: material in ASSOCIATIONS.get(component, [])
            )
        ]

        rows.append({
            "image": image,
            "material": material,
            "potential_source_detections": len(associated),
            "status": (
                "Potential source detected"
                if len(associated) > 0
                else "No mapped source detected"
            ),
        })

result = pd.DataFrame(rows)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUTPUT, index=False)

print("\nCRITICAL MATERIAL SCREENING")
print(result.groupby("material")["potential_source_detections"].sum())
print(f"\nBoards screened: {len(images)}")
print(f"Saved to: {OUTPUT}")
print("\nNOTE: Associations indicate possible sources, not confirmed metal content.")
