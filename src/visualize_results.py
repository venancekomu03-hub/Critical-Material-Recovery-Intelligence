
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "results/monte_carlo_results.csv"
OUTPUT = ROOT / "results/material_uncertainty.png"

df = pd.read_csv(INPUT)
df = df.sort_values("mean_mg")

# Calculate uncertainty distances from the mean
lower = df["mean_mg"] - df["p5_mg"]
upper = df["p95_mg"] - df["mean_mg"]

fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    df["material"],
    df["mean_mg"],
    color="steelblue",
    alpha=0.85,
    label="Mean estimated mass"
)

ax.errorbar(
    df["mean_mg"],
    df["material"],
    xerr=[lower, upper],
    fmt="none",
    ecolor="black",
    capsize=5,
    label="5th–95th percentile"
)

ax.set_xscale("log")
ax.set_xlabel("Estimated recoverable mass (mg, log scale)")
ax.set_title("Critical-Material Recovery: Monte Carlo Uncertainty")

ax.legend()
ax.grid(axis="x", alpha=0.2)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=300)
plt.show()

print(f"Graph saved to: {OUTPUT}")
