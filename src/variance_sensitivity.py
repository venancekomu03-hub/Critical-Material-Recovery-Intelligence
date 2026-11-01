
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results"
OUTPUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)
N = 20000
COMPONENT_COUNT = int(
    (pd.read_csv(ROOT / "results" / "component_inventory.csv")["component"]
     .str.strip()
     .str.lower() == "capacitor").sum()
)

PARAMETERS = ["presence", "mass_mg", "recovery"]

def sample_inputs(n):
    return np.column_stack([
        rng.uniform(0.10, 0.40, n),  # presence probability
        rng.uniform(0.25, 0.75, n),  # mass per component (mg)
        rng.uniform(0.50, 0.90, n),  # recovery efficiency
    ])

def model(x):
    p = x[:, 0]
    m = x[:, 1]
    r = x[:, 2]
    return COMPONENT_COUNT * p * m * r

A = sample_inputs(N)
B = sample_inputs(N)

YA = model(A)
YB = model(B)

variance = np.var(np.concatenate([YA, YB]), ddof=1)

indices = []

for i, parameter in enumerate(PARAMETERS):
    # C differs from A only in parameter i.
    C = A.copy()
    C[:, i] = B[:, i]

    YC = model(C)

    # First-order Sobol estimator (Saltelli form).
    first_order = np.mean(YB * (YC - YA)) / variance

    # Total-order estimator (Jansen form).
    total_order = np.mean((YA - YC) ** 2) / (2 * variance)

    indices.append({
        "parameter": parameter,
        "first_order": first_order,
        "total_order": total_order,
    })

df = pd.DataFrame(indices)
df.to_csv(OUTPUT / "variance_sensitivity.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5))

x = np.arange(len(df))
width = 0.35

ax.bar(
    x - width / 2,
    df["first_order"],
    width,
    label="First-order",
)

ax.bar(
    x + width / 2,
    df["total_order"],
    width,
    label="Total-order",
)

ax.set_xticks(x)
ax.set_xticklabels(["Presence", "Mass", "Recovery"])
ax.set_ylabel("Sobol sensitivity index")
ax.set_title("Tantalum Recovery: Variance-Based Sensitivity")
ax.legend()
ax.grid(axis="y", alpha=0.2)

plt.tight_layout()
plt.savefig(
    OUTPUT / "variance_sensitivity.png",
    dpi=300,
)
plt.show()

print("\nVARIANCE-BASED SENSITIVITY RESULTS")
print(df.round(4).to_string(index=False))
print("\nSaved variance_sensitivity.csv")
print("Saved variance_sensitivity.png")
print("NOTE: Input distributions are illustrative.")
