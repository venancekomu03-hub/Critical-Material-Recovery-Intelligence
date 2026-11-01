from pathlib import Path
import argparse
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 PCB component detector"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to YOLO dataset data.yaml"
    )
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()

    data_path = Path(args.data).expanduser().resolve()

    if not data_path.is_file():
        parser.error(f"Dataset config not found: {data_path}")

    model = YOLO("yolov8n.pt")

    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(ROOT / "runs" / "detect" / "results"),
        name="pcb_detector",
        exist_ok=True,
        seed=42,
        plots=True,
    )

    print("\nTraining completed.")
    print(
        "Model saved under: "
        "runs/detect/results/pcb_detector/weights/"
    )

if __name__ == "__main__":
    main()
