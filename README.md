# MCBOMs: Multidisciplinary Cost-Benefit Optimization Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python framework for optimizing transportation infrastructure investment decisions using Mixed-Integer Linear Programming (MILP). MCBOMs integrates safety, operational, and corridor condition benefits into a unified resource allocation framework.

Developed under FHWA Contract HRSO20240009PR by the Texas A&M Transportation Institute.

> **New here?** See **[USER_MANUAL.md](USER_MANUAL.md)** for a complete walkthrough — what the framework does, how to install it, how to run the validation, how to extend it, and how to interpret results. The manual is the single document that takes you from clone to result.

## Overview

MCBOMs supports transportation agencies in:

- Optimizing project selection across multiple sites under one or more budget constraints
- Quantifying multidisciplinary benefits (safety, operational, corridor condition)
- Enumerating segment-level alternative compositions
- Producing reproducible, auditable optimization results

The framework builds on:

- Harwood et al. (2003) — RSRAP (Resurfacing Safety Resource Allocation Program) for safety improvements within RRR projects on nonfreeway facilities
- Banihashemi (2007) — segment- and intersection-level optimization with the IHSDM Crash Prediction Module
- Highway Safety Manual (AASHTO, 2010) — Safety Performance Functions and Crash Modification Factors
- USDOT BCA Guidance for Discretionary Grant Programs (May 2025) — unit crash costs, value of travel time, and discounting parameters

The mathematical formulation is documented in detail in `docs/chapter2/`.

## Project Structure

```
mcboms-optimization/
├── README.md                       Quick reference (this file)
├── USER_MANUAL.md                  Complete walkthrough — start here
├── INSTRUCTIONS.md                 Setup-only instructions
│
├── docs/
│   ├── chapter2/                   Methodology chapter (LaTeX, PDF, Word)
│   └── Harwood_2003_Methodology_Reference.md
│
├── models/                         Solver-language mathematical models
│   ├── README.md
│   ├── ampl/                       AMPL .mod + .dat + .run files
│   ├── gams/                       GAMS .gms files
│   └── lp/                         LP solver-native format files
│
├── src/mcboms/                     Python implementation
│   ├── core/                       MILP optimizer
│   ├── benefits/
│   │   ├── safety.py               Eq 2.18 (HSM-based)
│   │   ├── operations.py           Eq 2.21 (in development)
│   │   └── ccm.py                  Eq 2.27 (in development)
│   ├── io/
│   │   ├── readers.py
│   │   ├── writers.py
│   │   └── colleague_workbook.py   Reader for the Task 4 BCA spreadsheet
│   ├── utils/economics.py          Discount factors, unit costs (USDOT BCA May 2025)
│   └── data/harwood_alternatives.py    Harwood (2003) validation data
│
├── tests/                          32 tests; run with `pytest`
│
├── examples/                       Reproducible Python examples
│   ├── banihashemi_intersections.py    Banihashemi (2007) sub-problem
│   └── banihashemi_alts.csv
│
└── run_harwood_validation.py       End-to-end Harwood reproduction script
```

The framework is the same mathematics in three forms: the formal spec in `docs/chapter2/`, solver-language models in `models/`, and Python implementation in `src/mcboms/`. All three produce the same numerical results.

## Installation

### Prerequisites

- Python 3.11+
- Either Gurobi (recommended) or CBC (open-source, bundled with PuLP)

### Setup

```bash
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
source venv/bin/activate
pip install -e .
```

For the optional Gurobi backend, obtain a license at https://www.gurobi.com/academia/ (free academic) or https://www.gurobi.com/solutions/licensing/ (commercial).

## Quick Start

```python
import pandas as pd
from mcboms.core import Optimizer
from mcboms.data.harwood_alternatives import get_harwood_alternatives

alternatives = get_harwood_alternatives()
sites = pd.DataFrame({"site_id": sorted(alternatives["site_id"].unique())})

optimizer = Optimizer(
    sites=sites,
    alternatives=alternatives,
    budget=50_000_000,
    discount_rate=0.04,        # Harwood used 4% per AASHTO 1977
    analysis_horizon=20,
    verbose=False,
)
result = optimizer.solve()
print(f"Net benefit: ${result.net_benefit:,.0f}")
print(f"Total cost:  ${result.total_cost:,.0f}")
```

## Validation

The framework is validated against two published benchmarks.

### Harwood et al. (2003)

10-site case study, mix of rural and urban undivided and divided nonfreeway facilities (2- and 4-lane). Run with:

```bash
python run_harwood_validation.py
```

Results:

| Budget | Metric | Harwood (2003) | MCBOMs | Difference |
|--------|--------|----------------|--------|------------|
| $50M   | Total benefit  | $10,640,914 | $10,640,909 | $-5 (rounding) |
| $50M   | Net benefit    | $6,159,517  | $6,159,512  | $-5 (rounding) |
| $50M   | Site selection | 10/10 sites match | | |
| $10M   | Net benefit    | $4,675,033  | $4,931,520  | +5.5% (documented) |

The $10M divergence is methodologically intentional and documented in `docs/chapter2/` Section 2.7.3: the MCBOMs prototype does not implement Harwood's deferral-penalty (PNR) mechanism, since per-site PNR values are not published and the Banihashemi (2007) benchmark also omits PNR. Without PNR, MCBOMs is free to defer sites strictly on net-benefit grounds and finds a strictly net-benefit-superior solution at the $10M budget.

### Banihashemi (2007) intersection sub-problem

13 intersections, 43 alternatives total, IHSDM Crash Prediction Module with published parameters. Run with:

```bash
python examples/banihashemi_intersections.py
```

The MCBOMs MILP correctly identifies Int 12:LTL as the most cost-effective improvement (B/C ≈ 11.5), correctly rejects signalization at Intersections 3 and 4 on delay-cost grounds, and produces a rank ordering of LTL improvements consistent with Banihashemi's Table 5. Numerical divergence from Banihashemi's full-network solution is attributable to (a) intersection sub-problem scope and (b) AMF values not published in the original paper.

## Mathematical Models (`models/`)

The `models/` folder contains the formal mathematical models in three solver-language forms. For users running MILP problems in CPLEX, Gurobi, GAMS, AMPL, or any LP-format-aware solver, this is the entry point — Python is not required.

- AMPL (`.mod` model + `.dat` data + `.run` script) — strongest semantic structure; model and data separate
- GAMS (`.gms`) — combined model and data, single-file
- LP (`.lp`) — solver-native, fully portable

Each format contains four instances:

- `worked_example` — Single-segment safety-only example with the **full Eq 2.18 chain** declared parametrically (severity disaggregation, CMF application, present-worth conversion). Demonstrates how raw inputs become benefit values.
- `harwood_50m` — Harwood at $50M budget. Uses published per-site values from Tables 2 and 3 (PSB and PTOB) with the Chapter 2 aggregation (Eq 2.2) and discretionary-cost objective (Section 2.2.1).
- `harwood_10m` — Harwood at $10M budget.
- `banihashemi_intersections` — 13-intersection sub-problem with the **full Banihashemi Eq 15 (IHSDM CPM)** declared parametrically, including AMF computation from raw skew, control, LTL, and ISD inputs.

LP files have been validated by solving with CBC; objective values match the Python implementation to the cent.

See `models/README.md` for run instructions and expected results per instance.

## Mathematical Formulation (Summary)

The full formulation, with derivations and worked examples, is in `docs/chapter2/`.

Objective (project-level, Eq 2.4):

```
max Z = Σ_i Σ_{j∈A_i} ( B_ij^total - C_ij^disc ) x_ij
```

Where C_ij^disc is the discretionary cost component subject to the optimization. For projects without a committed cost (most common case), C_ij^disc = C_ij. For Harwood-style RRR projects with required resurfacing, C_ij^disc is the safety improvement cost only.

Total benefit (Eq 2.2):

```
B_ij^total = Σ_{t=1}^{T} [ B_ijt^safety + B_ijt^operations + B_ijt^corridor ] · DF_t
```

Constraints:

- Total budget (Eq 2.5): Σ C_ij x_ij ≤ B
- Mutual exclusivity (Eq 2.6): Σ_j x_ij ≤ 1, ∀i
- Optional: dependency, cross-project exclusivity, minimum BCR (Eqs 2.8–2.10)
- Network: facility-type sub-budget, regional cap and floor (Eqs 2.14–2.16)

## Default Parameter Values

From USDOT BCA Guidance for Discretionary Grant Programs, May 2025 (Appendix A, in 2023 dollars):

| Parameter | Value | Source |
|-----------|-------|--------|
| Discount rate | 7% real | Section 4.3 |
| Analysis horizon | 20 years | Section 4.4 |
| Fatal (K) crash | $13,200,000 | Table A-1, p.39 |
| Incapacitating (A) | $1,254,700 | Table A-1, p.39 |
| Non-incapacitating (B) | $246,900 | Table A-1, p.39 |
| Possible injury (C) | $118,000 | Table A-1, p.39 |
| PDO (O) | $5,300 | Table A-1, p.39 |
| VOT (all-purposes) | $21.10/person-hour | Table A-2, p.40 |
| Average vehicle occupancy (passenger) | 1.52 | Table A-3, p.41 |
| VOC (light-duty vehicle) | $0.56/vehicle-mile | Table A-4, p.41 |

Agencies applying MCBOMs may override these with state-specific values. FHWA-SA-25-021 (October 2025) Step 5 documents a per-capita-income procedure for adjusting national crash costs to state-specific values.

## Tests

```bash
pytest tests/ -v
```

32 tests, all passing. Coverage includes the worked example reproduction (16 tests in `test_safety.py`), Harwood $50M rigorous reproduction (4/4 metrics within 1%), and Harwood $10M documented divergence.

## License

MIT License. See `LICENSE`.

## Citation

```bibtex
@techreport{mcboms2026,
  title = {MCBOMs: Multidisciplinary Cost-Benefit Optimization Models, Task 4 Report},
  author = {Texas A\&M Transportation Institute},
  year = {2026},
  institution = {Federal Highway Administration},
  number = {HRSO20240009PR}
}
```

## References

1. Harwood, D. W., Rabbani, E. R. K., & Richard, K. R. (2003). Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects. *Transportation Research Record*, 1840(1), 148–157.
2. Banihashemi, M. (2007). Optimization of highway safety and operation by using crash prediction models with accident modification factors. *Transportation Research Record*, 2019(1), 111–117.
3. AASHTO. (2010). *Highway Safety Manual* (1st ed.).
4. USDOT. (2025). *Benefit-Cost Analysis Guidance for Discretionary Grant Programs*, May 2025.
5. FHWA-SA-25-021. (2025). *Updated Crash Costs for Highway Safety Analysis*, October 2025.

## Contact

Texas A&M Transportation Institute, College Station, TX.
