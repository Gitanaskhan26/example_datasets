"""Extract the fixed IHDP covariates + treatment from a CEVAE/NPCI replication.

Source: ihdp_npci_1.csv from
https://github.com/AMLab-Amsterdam/CEVAE/tree/master/datasets/IHDP/csv

Covariates and treatment are identical across all 1000 CEVAE/NPCI
replications (only the simulated outcome columns y_factual, y_cfactual,
mu0, mu1 vary), so extracting from replication #1 is sufficient and
representative of every other replication.

This file becomes permanent shared infrastructure once uploaded to the
pgmpy/example_datasets HuggingFace repo and loaded via _get_raw_data()
on every IHDPDataset instantiation, so the assertions below are meant
to catch a bad extraction (wrong source file, corrupted download,
upstream format change) before it ships, not just document intent.
"""

import numpy as np
import pandas as pd

file_path = "ihdp_npci_1.csv"
output_path = "ihdp_covariates.csv"

cols = ["treatment", "y_factual", "y_cfactual", "mu0", "mu1"] + [f"x{i}" for i in range(1, 26)]
df = pd.read_csv(file_path, header=None, names=cols)

print(f"Original shape: {df.shape}")
assert df.shape == (747, 30), f"Expected (747, 30), got {df.shape}"

# Extract covariates + treatment
covariates = df[["treatment"] + [f"x{i}" for i in range(1, 26)]]

print(f"Extracted shape: {covariates.shape}")
assert covariates.shape == (747, 26), f"Expected (747, 26), got {covariates.shape}"

n_treated = int(covariates["treatment"].sum())
n_control = len(covariates) - n_treated
print(f"Treated count: {n_treated}")
print(f"Control count: {n_control}")
assert (n_treated, n_control) == (139, 608), (
    f"Expected 139 treated / 608 control (the standard post-exclusion "
    f"IHDP sample), got {n_treated} / {n_control}"
)

# x1-x6 (bw, b.head, preterm, birth.o, nnhealth, momage) are continuous
# and, per the upstream NPCI/CEVAE pipeline, already standardized. This
# is what lets the simulator skip re-standardizing on every load.
continuous_cols = [f"x{i}" for i in range(1, 7)]
means = covariates[continuous_cols].mean()
stds = covariates[continuous_cols].std()
assert np.allclose(means, 0, atol=1e-8), f"x1-x6 means not ~0:\n{means}"
assert np.allclose(stds, 1, atol=1e-6), f"x1-x6 stds not ~1:\n{stds}"
print("Continuous columns x1-x6 confirmed pre-standardized (mean~0, std=1).")

# x7-x25 are binary/categorical site & demographic indicators. All are
# {0,1} except x14 ("first" = firstborn indicator), which is {1,2} in
# the canonical CEVAE/NPCI data — not a bug: EconML's own port carries
# an explicit comment doing the equivalent {0,1}->{1,2} shift for this
# same variable, so this is the literature-standard coding, kept as-is.
strictly_binary_cols = [f"x{i}" for i in range(7, 26) if i != 14]
for col in strictly_binary_cols:
    uniques = set(covariates[col].unique().tolist())
    assert uniques <= {0, 1}, f"{col} is not binary, found values: {uniques}"
assert set(covariates["x14"].unique().tolist()) == {1, 2}, (
    "x14 ('first') expected to be {1,2}-coded (matches EconML's convention "
    "for this variable) — got a different value set, upstream file may "
    "have changed."
)
print("Columns x7-x25 confirmed binary (0/1), except x14 ('first') which is {1,2} by design.")

covariates.to_csv(output_path, index=False)
print(f"Saved {output_path}")
