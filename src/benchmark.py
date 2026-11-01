
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results"
import csv
from collections import Counter

with (ROOT / "results" / "component_inventory.csv").open(newline="") as file:
    counts = Counter(
        row["component"].strip()
        for row in csv.DictReader(file)
    )

COMPONENT_COUNT = counts["capacitor"]

SAMPLE_SIZES = [1000, 10000, 100000, 1000000]
REPEATS = 5

def simulate(n, seed=42):
    rng = np.random.default_rng(seed)

    presence = rng.uniform(0.10, 0.40, n)
    mass = rng.uniform(0.25, 0.75, n)
    recovery = rng.uniform(0.50, 0.90, n)

    return COMPONENT_COUNT * presence * mass * recovery

results = []

# Warm-up run
simulate(1000)

for n in SAMPLE_SIZES:
    timings = []

    for repeat in range(REPEATS):
        start = perf_counter()
        output = simulate(n, seed=42 + repeat)
        elapsed = perf_counter() - start

        assert len(output) == n
        assert np.all(np.isfinite(output))

        timings.append(elapsed)

    median_time = float(np.median(timings))

    results.append({
        "simulations": n,
        "median_seconds": median_time,
        "simulations_per_second": n / median_time,
    })

df = pd.DataFrame(results)
df.to_csv(OUTPUT / "benchmark_results.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(
    df["simulations"],
    df["median_seconds"],
    marker="o",
)

ax.set_xscale("log")
ax.set_xlabel("Number of simulations (log scale)")
ax.set_ylabel("Median execution time (seconds)")
ax.set_title("Monte Carlo Simulation Scalability")
ax.grid(alpha=0.25)

plt.tight_layout()
plt.savefig(OUTPUT / "benchmark.png", dpi=300)
plt.show()

print("\nPERFORMANCE BENCHMARK")
print(df.to_string(index=False))
print("\nSaved benchmark_results.csv")
print("Saved benchmark.png")
