
from pathlib import Path
from collections import Counter
import csv

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DATASET = next((ROOT / "datasets").glob("*/data.yaml")).parent
WEIGHTS = ROOT / "runs/detect/results/pcb_detector/weights/best.pt"
OUTPUT = ROOT / "results/component_inventory.csv"

model = YOLO(str(WEIGHTS))
images = DATASET / "test/images"

rows = []

for result in model.predict(
    source=str(images),
    conf=0.25,
    imgsz=640,
    device="mps",
    stream=True,
    verbose=False,
):
    image_name = Path(result.path).name

    for box in result.boxes:
        class_id = int(box.cls.item())
        confidence = float(box.conf.item())

        rows.append({
            "image": image_name,
            "component": model.names[class_id],
            "confidence": round(confidence, 4),
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["image", "component", "confidence"]
    )
    writer.writeheader()
    writer.writerows(rows)

counts = Counter(row["component"] for row in rows)

print("\nCOMPONENT INVENTORY")
for component, count in sorted(counts.items()):
    print(f"{component}: {count}")

print(f"\nTotal detections: {len(rows)}")
print(f"Images processed: {len(set(row['image'] for row in rows))}")
print(f"Saved to: {OUTPUT}")
 