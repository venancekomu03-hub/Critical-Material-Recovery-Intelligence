
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent

STEPS = [
    ("Component detection and inventory", "component_inventory.py"),
    ("Critical-material screening", "critical_materials.py"),
    ("Five-material recovery estimation", "five_material_recovery.py"),
    ("Monte Carlo uncertainty analysis", "monte_carlo.py"),
    ("Uncertainty visualization", "visualize_results.py"),
    ("Local sensitivity analysis", "sensitivity_analysis.py"),
    ("Variance-based sensitivity analysis", "variance_sensitivity.py"),
    ("Performance benchmarking", "benchmark.py"),
]

def main():
    print("\nPCB COMPONENT RECOVERY ANALYSIS")
    print("=" * 45)

    start = time.perf_counter()

    for number, (description, filename) in enumerate(STEPS, 1):
        script = ROOT / "src" / filename

        print(
            f"\n[{number}/{len(STEPS)}] {description}",
            flush=True
        )

        if not script.is_file():
            print(f"ERROR: Missing script: {script}")
            return 1

        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            check=False
        )

        if result.returncode != 0:
            print(f"\nFAILED: {filename}")
            return result.returncode

        print(f"COMPLETED: {filename}", flush=True)

    elapsed = time.perf_counter() - start

    print("\n" + "=" * 45)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Total execution time: {elapsed:.2f} seconds")
    print("Outputs saved in results/")

    return 0

if __name__ == "__main__":
    sys.exit(main())
