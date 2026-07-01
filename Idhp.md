## Add `ihdp_covariates.csv` to pgmpy/example_datasets

### Summary

Adds `ihdp_covariates.csv` (747 rows × 26 columns: `treatment` + `x1`-`x25`)
to the `pgmpy/example_datasets` HuggingFace repo. This is the fixed,
real-covariate design matrix that `IHDPDataset` loads via
`_get_raw_data("ihdp_covariates.csv")` on every instantiation — see
companion code PR: <link>.

### Provenance

- Source: `ihdp_npci_1.csv` from the CEVAE repository
  (`github.com/AMLab-Amsterdam/CEVAE/tree/master/datasets/IHDP/csv`),
  one of the standard NPCI-generated (Dorie, 2016) IHDP replications
  built on real covariates from the Infant Health and Development
  Program (Hill, 2011).
- Only `treatment` and `x1`-`x25` are kept. `y_factual`, `y_cfactual`,
  `mu0`, `mu1` are dropped — those are outcome columns specific to that
  one CEVAE replication; `IHDPDataset` regenerates outcomes itself from
  these fixed covariates, so shipping baked-in outcomes would be
  actively misleading (and would tie the package to one arbitrary
  replication out of 1000).
- Generation script: `prep.py` (included in this PR), which now
  validates its own output before writing — shape, treated/control
  counts, and per-column value ranges — since this file becomes
  permanent shared infrastructure once uploaded.

### Validated properties

- Shape: 747 × 26. 139 treated / 608 control — the standard
  post-selection-bias IHDP sample size used throughout the literature.
- `x1`-`x6` (birth weight, head circumference, weeks preterm, birth
  order, neonatal health index, mother's age) are continuous and
  already standardized (mean≈0, std=1) as part of the upstream
  NPCI/CEVAE pipeline — this extraction doesn't standardize them itself,
  it inherits that property.
- `x7`-`x25` are binary (0/1) site and demographic indicators, **with
  one documented exception**: `x14` ("first" — firstborn indicator) is
  `{1,2}`-coded, not `{0,1}`. This isn't a data error — EconML's own
  port carries an explicit comment doing the equivalent adjustment for
  this same variable, so `{1,2}` is the literature-standard coding for
  it and has been left as-is.
- Covariates are identical across all CEVAE replications
  (`ihdp_npci_1.csv` through `_1000.csv`) by construction, so this file
  is replication-agnostic — extracting from replication 1 is
  representative of all of them.

### Why this file instead of shipping the full CEVAE CSV

`IHDPDataset` treats IHDP as a real simulator: covariates are fixed,
outcomes are generated fresh per instantiation from a parameterized
response surface. A file with baked-in `y_factual`/`mu0`/`mu1` would
suggest those are meant to be read directly rather than regenerated.



