# MCBOMs User Manual

This manual explains the MCBOMs (Multidisciplinary Cost-Benefit Optimization Models) GitHub repository: what's in it, how to install it, how to run it, what the files do, and how to interpret the results.

If you are reading this, you are most likely either reviewing the framework, maintaining it, or applying it to a transportation investment problem. The manual covers all three use cases without separate sections — every reader benefits from understanding the whole picture.

---

## Table of Contents

1. [What MCBOMs Is](#1-what-mcboms-is)
2. [Three Forms of the Same Mathematics](#2-three-forms-of-the-same-mathematics)
3. [Repository Tour](#3-repository-tour)
4. [Mathematical Formulation Summary](#4-mathematical-formulation-summary)
5. [The Mathematical Models (`models/`)](#5-the-mathematical-models-models)
6. [Validation Instances](#6-validation-instances)
7. [Default Parameter Values](#7-default-parameter-values)
8. [Quick Start by Access Method](#8-quick-start-by-access-method)
9. [Python Access Method](#9-python-access-method)
10. [Software Architecture](#10-software-architecture)
11. [Running the Validation Yourself](#11-running-the-validation-yourself)
12. [Extending the Framework](#12-extending-the-framework)
13. [Validation Status and Known Limitations](#13-validation-status-and-known-limitations)
14. [Troubleshooting](#14-troubleshooting)
15. [Glossary](#15-glossary)
16. [References](#16-references)

---

## 1. What MCBOMs Is

MCBOMs is a Mixed-Integer Linear Programming (MILP) framework for optimizing transportation infrastructure investment decisions. Given a portfolio of candidate projects (sites or intersections), each with multiple possible improvement alternatives, MCBOMs selects the combination that maximizes total societal benefit subject to a budget constraint.

The benefits the framework quantifies are:

- **Safety benefits** — reductions in expected crash costs, computed via the Highway Safety Manual (HSM) Crash Modification Factor (CMF) methodology
- **Operational benefits** — reductions in travel time and vehicle operating costs, valued at USDOT-recommended rates
- **Corridor condition benefits** — energy, environmental, accessibility, and resilience improvements (in development)

The framework is developed under FHWA Contract HRSO20240009PR by the Texas A&M Transportation Institute. It builds directly on Harwood, Rabbani, and Richard (2003) — who developed the RSRAP optimization tool for safety improvements within Resurfacing, Restoration, and Rehabilitation (RRR) projects — and Banihashemi (2007) — who extended that framework to include intersection-level optimization with the IHSDM Crash Prediction Module.

The full mathematical formulation is documented in `docs/chapter2/chapter2.pdf`. This manual is the operational guide for using the framework.

---

## 2. Three Forms of the Same Mathematics

The MCBOMs framework is mathematically a single optimization model. That single model is expressed in three forms in this repository, each suited to a different audience:

| Form | Where it lives | Best for |
|---|---|---|
| **Formal mathematical specification** | `docs/chapter2/chapter2.pdf` | Reading the math; auditing the formulation; citing in reports |
| **Solver-language models (AMPL, GAMS, LP)** | `models/` | Running the validation in CPLEX, Gurobi, or any commercial MILP solver |
| **Python implementation** | `src/mcboms/` | Programmatic use, custom data integration, building extensions |

These three forms are equivalent — they implement the same equations. The numerical results from any of them, on any validation instance, match to the cent.

A reviewer or analyst who works in classical optimization software does not need to install or run Python. The models in `models/` are the canonical mathematical artifact and can be loaded directly into AMPL, GAMS, or any LP-format-aware solver.

The Python implementation is the access method for users who want to integrate MCBOMs into a larger Python pipeline, automate runs, or extend the framework with new benefit categories.

---

## 3. Repository Tour

Here is what every top-level directory contains and why it exists.

```
mcboms-optimization/
├── README.md                     Quick reference, validation results table
├── USER_MANUAL.md                This document
├── INSTRUCTIONS.md               Setup-only instructions (subset of this manual)
├── LICENSE                       MIT License
├── pyproject.toml                Python package metadata
├── requirements.txt              Python dependencies
├── run_harwood_validation.py     Python script for end-to-end Harwood validation
│
├── docs/                         Documentation
│   ├── chapter2/                   Methodology chapter (the formal spec)
│   │   ├── chapter2.tex              LaTeX source
│   │   ├── chapter2.pdf              30-page rendered PDF
│   │   └── chapter2_styled.docx      Word version
│   └── Harwood_2003_Methodology_Reference.md
│
├── models/                       Solver-language mathematical models
│   ├── README.md                   Explains the model files in detail
│   ├── ampl/                       AMPL .mod + .dat + .run files
│   ├── gams/                       GAMS .gms files
│   └── lp/                         LP solver-native format files
│
├── src/mcboms/                   Python implementation
│   ├── core/                       MILP optimizer engine
│   ├── benefits/                   Benefit calculation modules
│   │   ├── safety.py                 Eq 2.18 (HSM-based) - implemented
│   │   ├── operations.py             Eq 2.21 - in development
│   │   └── ccm.py                    Eq 2.27 - in development
│   ├── io/                         Input/output modules
│   ├── utils/economics.py          Discount factors, unit costs
│   └── data/harwood_alternatives.py  Harwood (2003) data
│
├── tests/                        Test suite (32 tests, all passing)
│
├── examples/                     Reproducible Python examples
│   ├── banihashemi_intersections.py   Banihashemi sub-problem reproduction
│   └── banihashemi_alts.csv           Pre-generated alternative table
│
├── notebooks/                    Jupyter notebooks
│   └── MCBOMs_Harwood_Validation.ipynb
│
└── data/                         Empty directories for user data
    ├── input/                      Place your input data here
    ├── output/                     Optimization results land here
    └── validation/                 Validation case data here
```

You do not need to use every folder. For most users, the entry points are `README.md`, `USER_MANUAL.md`, `docs/chapter2/chapter2.pdf`, and `models/`.

---

## 4. Mathematical Formulation Summary

The full formulation is in `docs/chapter2/chapter2.pdf`. This section gives a one-page summary so you do not need to flip back and forth.

### Decision variable

`x_ij ∈ {0, 1}` — equals 1 if alternative `j` is selected for project `i`, 0 otherwise.

### Objective (Eq 2.4)

```
maximize sum over (i, j) of (B_ij - C_ij_disc) * x_ij
```

Where `B_ij` is the total present-value benefit of alternative `j` at project `i`, and `C_ij_disc` is the discretionary cost component.

For most projects, discretionary cost equals total cost (`C_ij_disc = C_ij`). For Harwood's RRR projects, where pavement resurfacing is committed (every site is resurfaced regardless), only the safety improvement cost is discretionary.

### Total benefit (Eq 2.2)

```
B_ij = sum over years t of (B_safety_t + B_operations_t + B_corridor_t) * DF_t
```

Where `DF_t = 1 / (1+r)^t` is the year-t discount factor.

### Core constraints

- **Total budget** (Eq 2.5): `sum C_ij * x_ij <= B_total`
- **Mutual exclusivity** (Eq 2.6): `sum_j x_ij <= 1` for each project (at most one alternative per project)
- **Binary** (Eq 2.7): `x_ij ∈ {0, 1}`

### Optional constraints (Eq 2.8 - 2.10)

- **Dependency**: `x_ij <= x_i'j'` (alternative requires another)
- **Cross-project exclusivity**: `x_ij + x_i'j' <= 1` (alternatives conflict)
- **Minimum BCR**: `sum B_ij * x_ij >= theta * sum C_ij * x_ij`

### Network-level constraints (Eq 2.14 - 2.16)

- **Facility-type sub-budget**: budget caps per facility type
- **Regional cap**: budget caps per region
- **Regional floor**: minimum spend per region

### Safety benefit (Eq 2.18)

For one segment, one alternative, one year:

```
B_safety_year = sum over severity s of (E_nobuild_s - E_build_s) * UC_s
              = sum_s [N * p_s * (1 - CMF)] * UC_s
```

Where `N` is observed annual crashes, `p_s` is severity proportion, `CMF` is the Crash Modification Factor for the treatment, and `UC_s` is the unit cost per crash of severity `s` (USDOT BCA May 2025 values).

Present value: `B_safety_PV = B_safety_year * PWF(r, T)` where `PWF(r, T) = ((1+r)^T - 1) / (r * (1+r)^T)`.

For r=0.07 and T=20, `PWF = 10.594`.

### Operational benefit (Eq 2.21)

```
B_operations_year = sum over vehicle classes of [Δd * AADT * 365 * OCC * VOT + ΔVOC * VMT]
```

Present value: `B_operations_PV = B_operations_year * PWF(r, T)`.

This module is in development.

### Corridor condition benefit (Eq 2.27)

```
B_corridor = sum over CCM categories c of sum over years t of ΔQ_c * V_c * DF_t
```

This module is in development.

Every equation listed above is encoded explicitly in the model files in `models/`. See Section 5.

---

## 5. The Mathematical Models (`models/`)

The `models/` folder is the canonical solver-language expression of the MCBOMs framework. For users who run MILP problems in commercial solvers (CPLEX, Gurobi, FICO Xpress, GAMS, AMPL, CBC, SCIP), this is the entry point — no Python required.

### 5.1 Three formats, four instances

| Format | When to use it | File extensions |
|---|---|---|
| **AMPL** | Strongest semantic structure; model and data are separate, so the math is most readable | `.mod` (model), `.dat` (data), `.run` (script) |
| **GAMS** | Combined model + data in one file; common in policy and economics modeling | `.gms` |
| **LP** | Solver-native format, fully portable, drop into any MILP solver | `.lp` |

| Instance | Purpose | Equations exercised |
|---|---|---|
| `worked_example` | Single-segment safety-only example from Chapter 2 Section 2.3.7 | Full Eq 2.18 chain (severity disaggregation → CMF → annual → PWF → PV) plus Eq 2.4–2.7 |
| `harwood_50m` | Harwood (2003) 10-site case study, $50M budget | Eq 2.2 aggregation (PSB + PTOB) plus Eq 2.4–2.7 |
| `harwood_10m` | Harwood (2003), $10M budget | Same as `harwood_50m` |
| `banihashemi_intersections` | Banihashemi (2007) 13-intersection sub-problem | Full Banihashemi Eq 15 (IHSDM CPM) chain plus Eq 2.4–2.7 |

Each format covers all four instances. That is 4 × 3 = 12 model instances total, plus shared optimization-layer files in AMPL.

### 5.2 What the AMPL files look like

The AMPL folder contains:

- **`optimization.mod`** — generic optimization-layer model with all 10 constraints (Eq 2.4–2.10 + 2.14–2.16) declared. Optional and network-level constraints are activated by populating the corresponding sets in the `.dat` file.
- **`worked_example.mod` + `worked_example.run`** — the full Eq 2.18 chain end-to-end. Severity distribution, CMF, unit costs, and PWF are all parameters declared in the model. The optimizer recomputes the safety benefit from raw inputs every time the file is run.
- **`harwood.mod`** — paper-faithful aggregation. PSB and PTOB are inputs taken directly from Harwood Tables 2 and 3. Discretionary-cost objective convention.
- **`harwood_50m.dat`, `harwood_10m.dat`, `harwood_50m.run`, `harwood_10m.run`** — Harwood instance data and run scripts.
- **`banihashemi_intersections.mod` + `.dat` + `.run`** — full parametric IHSDM CPM. Per-intersection ADTs, skew angles, traffic control, LTL/ISD attributes are inputs; the model computes crashes per year from Banihashemi Eq 15 and (crash + delay) cost over 20 years.

### 5.3 What the GAMS files look like

The GAMS folder contains a single self-contained `.gms` file per instance: `worked_example.gms`, `harwood_50m.gms`, `harwood_10m.gms`, `banihashemi_intersections.gms`. Each file declares sets, parameters, equations, variables, and a model definition, then solves it.

### 5.4 What the LP files look like

The LP folder contains a single solver-native `.lp` file per instance. These files are validated by solving with CBC; the optimal objectives match the AMPL, GAMS, and Python results to the cent. Every coefficient in the LP file traces back to the formal Eq 2.4-2.18 chain documented in Chapter 2 — the LP header comments explain exactly how each coefficient was derived.

### 5.5 Running the models

**AMPL**:
```
cd models/ampl
ampl harwood_50m.run
```

**GAMS**:
```
cd models/gams
gams harwood_50m.gms
```

**LP** (with CPLEX):
```
cplex
> read models/lp/harwood_50m.lp
> mipopt
> display solution variables -
```

**LP** (with Gurobi):
```
gurobi_cl models/lp/harwood_50m.lp
```

**LP** (with CBC, free):
```
cbc models/lp/harwood_50m.lp solve solu /dev/stdout
```

Expected results are in Section 6 below.

### 5.6 Honest scope disclosure for each instance

The four instances do not all reach the same level of parametric detail. This is honest about what data is publicly available:

- **`worked_example`** is fully parametric end-to-end. Every input from raw crash count to the optimization is declared in the model file. The optimizer recomputes the safety benefit from raw inputs every time. Use this instance to demonstrate Eq 2.18 to a reviewer who wants to see the full chain.
- **`banihashemi_intersections`** is fully parametric for the IHSDM crash prediction module. Per-intersection ADTs, skew angles, traffic control type, LTL/ISD attributes, and delay times are inputs; the model computes crashes/year via Banihashemi Eq 15 and the (crash + delay) cost over 20 years. The AMF values used are standard IHSDM/Vogt-Bared values; Banihashemi did not publish his exact AMF values in the paper.
- **`harwood_50m`** and **`harwood_10m`** use Harwood's published per-site, per-alternative values from Tables 2 and 3 directly (resurfacing cost, safety improvement cost, PSB, PTOB). Harwood's RSRAP computes PSB internally from per-severity AMFs and accident frequencies (his Eq 1, paper page 151), but those raw inputs are not published in the paper — only the aggregate PSB values are. Reconstructing Harwood's per-severity inputs would require fabricating data; instead, this file uses Harwood's published aggregates and demonstrates the per-severity Eq 2.18 chain in `worked_example` instead.

This is also documented in `models/README.md` per instance.

---

## 6. Validation Instances

The framework is validated against three benchmarks. Each is reproducible from the repository — by running the AMPL/GAMS/LP files in `models/` or by running the Python scripts.

### 6.1 Worked Example (Section 2.3.7 of Chapter 2)

A single 5-mile rural two-lane segment. We constructed this example specifically to demonstrate the safety benefit chain (Eq 2.18) end-to-end with full per-severity inputs.

**Inputs:**
- Annual crash count: 6.0
- Severity distribution (KABCO): 1.3% / 6.5% / 9.5% / 11.7% / 71.0%
- Treatment: lane widening 10 ft → 12 ft, CMF = 0.88
- Discount rate: 7%, horizon: 20 years
- Unit costs: USDOT BCA May 2025 (K=$13.2M, A=$1.25M, B=$247k, C=$118k, O=$5.3k)

**Expected:**
- Annual safety benefit: **$211,810**
- Present value safety benefit: **$2,243,914**
- Optimal MILP objective at $1M budget: **$1,493,914** (= PV − treatment cost)

**How to reproduce:**
- Solver-direct: open `models/lp/worked_example.lp` in any MILP solver
- AMPL: `cd models/ampl && ampl worked_example.run`
- GAMS: `cd models/gams && gams worked_example.gms`

### 6.2 Harwood (2003) Case Study

A 10-site case study published in TRR 1840. Mix of rural and urban undivided/divided 2- and 4-lane nonfreeway facilities. Two budget levels: $50M and $10M.

**Expected at $50M:**
- Total safety benefit (PSB): $9,831,263
- Total operational benefit (PTOB): $809,651
- Net benefit: **$6,159,517**
- All 10 sites get an alternative

**Expected at $10M:**
- Net benefit (Harwood paper): $4,675,033
- Net benefit (MCBOMs): **$4,931,520** (5.5% higher)

The $10M divergence is intentional and documented in Chapter 2 Section 2.7.3. Harwood implements a "Penalty for Not Resurfacing" (PNR) that we cannot reproduce because Harwood does not publish per-site PNR values. Without PNR, MCBOMs is free to defer sites strictly on net-benefit grounds, finding a strictly better solution by net-benefit at the lower budget. This is consistent with Banihashemi (2007), which also omits PNR.

**How to reproduce:**
- Solver-direct: `models/lp/harwood_50m.lp` or `models/lp/harwood_10m.lp`
- AMPL: `models/ampl/harwood_50m.run` or `harwood_10m.run`
- GAMS: `models/gams/harwood_50m.gms` or `harwood_10m.gms`
- Python: `python run_harwood_validation.py`

### 6.3 Banihashemi (2007) Intersection Sub-Problem

A 13-intersection sub-problem from Banihashemi's TRR 2019 paper. Each intersection has 2-5 alternatives covering left-turn-lane addition, traffic control changes, sight distance correction, and skew angle adjustment.

**Implementation:** The IHSDM Crash Prediction Module (Banihashemi Eq 15) is implemented parametrically. Inputs are per-intersection ADTs, skew angles, traffic control type, LTL/ISD attributes, and delay times. The model computes expected crashes per year, then 20-year (crash + delay) cost.

**Expected structural results (the rank ordering of cost-effective improvements):**
- Most cost-effective: Intersection 12 LTL (B/C ≈ 11.5) — selected at every nonzero budget
- Signalization at Intersections 3 and 4 correctly rejected at every budget (delay cost increase dominates crash savings)
- Rank ordering of LTL improvements matches Banihashemi Table 5

**Numerical divergence from Banihashemi's published full-network solution is documented:**
1. We validate the intersection sub-problem; Banihashemi optimized the full network jointly
2. Banihashemi did not publish his exact AMF values; we use standard IHSDM/Vogt-Bared values

**How to reproduce:**
- Solver-direct: `models/lp/banihashemi_intersections.lp`
- AMPL: `models/ampl/banihashemi_intersections.run`
- GAMS: `models/gams/banihashemi_intersections.gms`
- Python: `python examples/banihashemi_intersections.py`

---

## 7. Default Parameter Values

The framework ships with USDOT BCA Guidance May 2025 defaults. All values are in 2023 dollars unless noted otherwise.

| Parameter | Value | Source |
|---|---|---|
| Discount rate | 7% real | USDOT BCA May 2025 Section 4.3 |
| Analysis horizon | 20 years | USDOT BCA May 2025 Section 4.4 |
| Crash unit costs (KABCO) | | USDOT BCA May 2025 Table A-1, p.39 |
| K (fatal) | $13,200,000 | |
| A (incapacitating injury) | $1,254,700 | |
| B (non-incapacitating injury) | $246,900 | |
| C (possible injury) | $118,000 | |
| O (PDO) | $5,300 | |
| Value of Time (all-purposes) | $21.10 / person-hour | USDOT BCA May 2025 Table A-2, p.40 |
| Value of Time (personal) | $19.40 / person-hour | |
| Value of Time (business) | $33.50 / person-hour | |
| Average vehicle occupancy (passenger) | 1.52 | USDOT BCA May 2025 Table A-3, p.41 |
| Vehicle Operating Cost (light-duty) | $0.56 / vehicle-mile | USDOT BCA May 2025 Table A-4, p.41 |

### Overriding defaults

State agencies may override these with state-specific values.

**In the solver-language models** — edit the parameter values directly in the relevant `.dat` file (AMPL) or at the top of the `.gms` file (GAMS). The values are explicit at the top of each instance file.

**In the Python implementation** — edit `src/mcboms/utils/economics.py` to change globally, or pass values as arguments to the relevant functions.

For HSIP-context applications, FHWA-SA-25-021 (October 2025) Step 5 documents a per-capita-income procedure for adjusting national crash costs to state-specific values.

---

## 8. Quick Start by Access Method

The framework can be accessed three ways. Pick whichever matches the tool you already use.

### 8.1 Just want to read the math?

Open these three files on GitHub or your local clone:

1. **`docs/chapter2/chapter2.pdf`** — formal mathematical formulation, ~30 pages
2. **`models/ampl/worked_example.mod`** — Eq 2.18 in solver-readable form, ~120 lines, easiest entry
3. **`models/lp/harwood_50m.lp`** — actual MILP problem text for a real instance

You now understand the math, the model, and one realistic instance. No software needed.

### 8.2 Have CPLEX, Gurobi, GAMS, or any MILP solver?

Run any instance directly. The expected objectives in Section 6 are what you should see.

```
# CPLEX
cplex
> read models/lp/harwood_50m.lp
> mipopt
> display solution objective       (expected: 6,159,512.00)
```

```
# Gurobi
gurobi_cl models/lp/harwood_50m.lp     (expected: Optimal objective: 6.159512e+06)
```

```
# AMPL with CPLEX
cd models/ampl
ampl harwood_50m.run
```

```
# GAMS with CPLEX
cd models/gams
gams harwood_50m.gms
```

If you get the expected objective on any one instance, the framework is operational on your machine. No further setup required.

### 8.3 Have Python?

```
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
pip install -e .
python run_harwood_validation.py
pytest tests/ -q
```

You should see "32 passed" and a "VALIDATION SUCCESSFUL" message. See Section 9 for details.

---

## 9. Python Access Method

The Python implementation is in `src/mcboms/`. It is one of three access methods, intended for users who want to integrate MCBOMs into a larger Python pipeline, automate runs, or extend the framework with new benefit categories.

### 9.1 Prerequisites

- **Python 3.11 or higher.** Check with `python --version` or `python3 --version`. Download from https://www.python.org/downloads/ if needed.
- **A MILP solver.** The framework supports two backends:
  - **CBC** (open-source, bundled with PuLP) — works out of the box, slower for large problems
  - **Gurobi** (commercial, free academic license) — faster, used in the validation runs

### 9.2 Setup

**On Linux/Mac:**

```
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
source venv/bin/activate
pip install -e .
```

**On Windows (PowerShell or Git Bash):**

```
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
venv\Scripts\activate
pip install -e .
```

That installs the `mcboms` package and all Python dependencies (pandas, numpy, pulp, pytest, openpyxl).

### 9.3 Optional: Gurobi installation

If you want to use Gurobi instead of CBC:

1. Get a license at https://www.gurobi.com/academia/ (academic, free) or https://www.gurobi.com/solutions/licensing/ (commercial)
2. Install Gurobi following their installer
3. Activate the license: `grbgetkey YOUR-LICENSE-KEY`
4. Install the Python interface: `pip install gurobipy`

Without Gurobi, the framework falls back to CBC automatically.

### 9.4 Verifying the Python installation

Run the test suite. All 32 tests should pass:

```
pytest tests/ -q
```

Expected output:

```
............................
32 passed in 2 seconds
```

If any tests fail, see Section 14 (Troubleshooting).

### 9.5 Programmatic use

```python
from mcboms.core import Optimizer
from mcboms.data.harwood_alternatives import get_harwood_alternatives
import pandas as pd

alternatives = get_harwood_alternatives()
sites = pd.DataFrame({"site_id": sorted(alternatives["site_id"].unique())})

optimizer = Optimizer(
    sites=sites,
    alternatives=alternatives,
    budget=50_000_000,
    discount_rate=0.04,        # Harwood used 4% per AASHTO 1977
    analysis_horizon=20,
)
result = optimizer.solve()
print(f"Net benefit: ${result.net_benefit:,.0f}")
print(f"Total cost:  ${result.total_cost:,.0f}")
```

Expected output:

```
Net benefit: $6,159,512
Total cost:  $16,271,247
```

---

## 10. Software Architecture

This section describes how the Python code is organized and how to navigate it.

### 10.1 The `mcboms.core` package

**`src/mcboms/core/optimizer.py`** — the main `Optimizer` class. Construct with sites, alternatives, budget, discount rate, analysis horizon. Call `.solve()` to run the MILP and get an `OptimizationResult` back.

The optimizer uses Gurobi if available, falling back to CBC. The decision variables are binary, the objective is linear, and the constraints are linear — it is a standard MILP that any solver handles.

**`src/mcboms/core/alternatives.py`** — helpers for enumerating alternatives. Used by the data layer.

### 10.2 The `mcboms.benefits` package

This is where the benefit equations live. Currently:

**`safety.py`** is fully implemented. It exposes the `compute_safety_benefit()` function that takes per-severity inputs and returns the present-value benefit. It implements Eq 2.18 from Chapter 2.

**`operations.py`** is in development. The formulation is locked (see Chapter 2 Section 2.4); the implementation will follow the same preprocessing pattern as `safety.py`.

**`ccm.py`** is in development. The computational structure is in Chapter 2 Section 2.5.

### 10.3 The `mcboms.io` package

**`readers.py`** — reads CSV input files (sites, alternatives) and converts them to pandas DataFrames in the format the optimizer expects.

**`writers.py`** — writes results to CSV.

**`colleague_workbook.py`** — reads the Task 4 BCA spreadsheet (an Excel workbook your TTI colleague maintains) and converts it to the optimizer's input format.

### 10.4 The `mcboms.utils` package

**`economics.py`** — discount factor formulas, present-worth factor computation, and bundled USDOT BCA May 2025 default unit costs (crash costs, value of time, vehicle operating cost). All values are documented with their source in the file.

### 10.5 The `mcboms.data` package

**`harwood_alternatives.py`** — bundled Harwood (2003) case study data. Returns a DataFrame of 21 alternatives across 10 sites, with all the published cost and benefit components. This is what the validation runs against.

### 10.6 Tests

**`tests/test_harwood_validation.py`** — 16 tests that verify the Harwood reproduction. Includes Level 2a (rigorous $50M check) and Level 2b (documented $10M divergence) per Chapter 2 Section 2.7.

**`tests/test_safety.py`** — 16 tests covering per-severity disaggregation, CMF combination, and the worked example reproduction.

Run all tests with `pytest tests/ -q`.

---

## 11. Running the Validation Yourself

This section is the hands-on walkthrough. We assume you have set up either the solver tools (Section 5/8) or Python (Section 9).

### 11.1 The end-to-end Harwood validation (Python)

Run the script:

```
python run_harwood_validation.py
```

You should see two main output blocks:

**Level 2a ($50M, rigorous):** Total benefit, total cost, net benefit, and per-site selection should all match Harwood Table 4 within 1% (in practice within $5 due to rounding). All 4 metrics must pass.

**Level 2b ($10M, documented divergence):** Informational only. The +5.5% net benefit difference vs Harwood is expected per Chapter 2 Section 2.7.3 (no PNR).

The final banner says:
```
✓ VALIDATION SUCCESSFUL
  MCBOMs reproduces Harwood (2003) $50M published results.
  $10M divergence is documented methodological choice per
  formulation spec Section 7.3.
```

### 11.2 The Harwood validation in AMPL/GAMS/LP

Same numerical result, different access methods:

```
cd models/ampl && ampl harwood_50m.run        (CPLEX, Gurobi)
cd models/gams && gams harwood_50m.gms        (CPLEX, CONOPT)
cplex < models/lp/harwood_50m.lp              (CPLEX)
gurobi_cl models/lp/harwood_50m.lp            (Gurobi)
```

Each should print the optimal objective $6,159,512.

### 11.3 The Banihashemi intersection sub-problem

```
python examples/banihashemi_intersections.py        (Python)
ampl models/ampl/banihashemi_intersections.run      (AMPL)
gams models/gams/banihashemi_intersections.gms      (GAMS)
gurobi_cl models/lp/banihashemi_intersections.lp    (Gurobi LP)
```

The structural result (Int 12 LTL most cost-effective; signalization at Int 3 and Int 4 rejected) is what we validate.

### 11.4 Modifying a parameter

Suppose you want to see what happens if the discount rate is 4% instead of 7%.

**In Python:** edit `src/mcboms/utils/economics.py`:
```
DEFAULT_DISCOUNT_RATE = 0.04
```

**In AMPL worked example:** edit `models/ampl/worked_example.mod`:
```
param r := 0.04;
```

**In GAMS worked example:** edit `models/gams/worked_example.gms`:
```
Scalar r 'discount rate' / 0.04 /;
```

**In LP files:** the discount rate is baked into the objective coefficients. To change it, regenerate the LP from the AMPL or Python source after changing the parameter there.

---

## 12. Extending the Framework

This section is for users who want to add new functionality.

### 12.1 Adding a new benefit category

Suppose you want to add a "construction emissions" benefit category. Steps:

1. **Math:** define the equation in Chapter 2 (LaTeX edit). Number it 2.x to fit the existing scheme.
2. **AMPL:** add the parametric definition to a new instance `.mod` file in `models/ampl/`.
3. **GAMS:** mirror in `.gms`.
4. **Python:** create `src/mcboms/benefits/construction_emissions.py` following the pattern of `safety.py`.
5. **Tests:** add unit tests in `tests/test_construction_emissions.py`.
6. **README and USER_MANUAL:** update the structure and validation tables.

The convention is to lock the math first, then propagate to all three forms (AMPL, GAMS, Python). Numerical results from any form must match.

### 12.2 Adding a new validation case study

1. **Data:** create the alternative DataFrame (one row per (project, alternative) pair).
2. **Solver instances:** generate the AMPL/GAMS/LP files for the new case (use the existing Banihashemi script as a template).
3. **Python script:** create `examples/your_case_study.py`.
4. **Tests:** add validation tests in `tests/test_your_case_study.py`.
5. **Document:** add a section to Chapter 2 and update Section 6 of this manual.

### 12.3 Modifying the optimizer

If you need to add a new constraint type:

1. **Math:** edit Chapter 2 Section 2.2.
2. **AMPL:** edit `models/ampl/optimization.mod` to add the new constraint.
3. **GAMS:** mirror.
4. **Python:** edit `src/mcboms/core/optimizer.py` to add the constraint inside `_build_model()`.
5. **Tests:** add tests covering the new constraint behavior.

### 12.4 Code style

- Plain, professional code comments. Reference Chapter 2 equation numbers (e.g., `# Eq 2.18`).
- Type hints where helpful but not required everywhere.
- `pytest` for tests, `pandas` for data, `pulp` and `gurobipy` for optimization.
- Match the existing module structure: classes for stateful objects, free functions for stateless calculations.

---

## 13. Validation Status and Known Limitations

This section is what you tell a reviewer who asks "what works and what doesn't yet."

### 13.1 What is validated

- **Worked example (Section 2.3.7)**: arithmetic verified against Chapter 2 to the cent, in Python and AMPL/GAMS/LP.
- **Harwood $50M**: 4 of 4 rigorous metrics match Harwood Table 4 within $5 (rounding). 10 of 10 site selections match exactly. Validated in Python; LP files solve to the same objective with CBC.
- **Harwood $10M**: documented +5.5% divergence on net benefit. The MCBOMs solution has higher net benefit than Harwood's because PNR is not implemented.
- **Banihashemi intersection sub-problem**: structural validation passes. Int 12 LTL identified as most cost-effective, signalization at Int 3/4 rejected, rank ordering of LTL improvements consistent with Banihashemi Table 5.
- **Cross-validation against TTI BCA spreadsheet**: 35 segment-alternative pairs checked, $0.00 maximum error after applying the 10.594× present-worth factor bridge.

### 13.2 What is implemented but not yet validated against external benchmarks

- The optional constraints (Eq 2.8 dependency, Eq 2.9 cross-project exclusivity, Eq 2.10 minimum BCR) are formulated and the AMPL `optimization.mod` supports them. They are not exercised by the current validation cases. They will be tested when an agency provides a use case.

### 13.3 What is documented but not yet implemented

- **`operations.py`**: Operational benefit module (Eq 2.21). Formulation is locked (corrected USDOT form per Chapter 2 Section 2.4). Implementation follows the same pattern as `safety.py`.
- **`ccm.py`**: Corridor condition benefit module (Eq 2.27). Computational structure is locked. Per-category monetization functions to be added incrementally.
- **Network-level constraints in the Python optimizer**: Eqs 2.14-2.16 (facility-type sub-budget, regional cap, regional floor) are in the AMPL `optimization.mod` but not yet wired into the Python `Optimizer` class.

### 13.4 What is documented as a deferred enhancement

- **Banihashemi full-network validation**: the published Banihashemi case has 135 homogeneous segments plus 13 intersections (3,385 binary variables). We currently validate the intersection sub-problem. Full-network validation requires segment geometry data not published in the paper.
- **Segment-level treatment composition**: Chapter 2 Section 2.1.2 documents this concept (per FHWA reviewer requirement) and the Eq 2.5a cost decomposition. The Python prototype currently uses alternative-level aggregate costs. Per-treatment decomposition will be added when an agency provides treatment-cost catalog data.

### 13.5 Known data quality concerns

- The Task 4 BCA spreadsheet has an operational benefit formula in cell AH3 that contains documented unit-conversion and missing-AADT issues. The framework's correct Eq 2.21 implementation will not match the spreadsheet output until the spreadsheet formula is corrected. Tracking this with the spreadsheet maintainer.

---

## 14. Troubleshooting

### Solver-language model issues

**LP file does not solve in CPLEX/Gurobi.**
The LP files have been validated by solving with CBC. If your solver rejects them, check:
- Solver version (CPLEX 12.10+ and Gurobi 9+ should both work)
- File path (LP format is sensitive to leading/trailing whitespace in line continuations)
- File encoding (must be ASCII or UTF-8)

**AMPL or GAMS reports "set is empty" warnings.**
The optimization model includes optional and network-level constraints (Eq 2.8-2.10, 2.14-2.16) that are activated only when the corresponding sets are populated in the data file. When the validation instances do not exercise these constraints, AMPL or GAMS may emit warnings; the warnings are expected and the solution remains optimal.

**Solver reports "infeasible" for an intersection sub-problem.**
The default budget is $12M (effectively unconstrained for the intersection sub-problem). If you tightened the budget, check that it is positive and large enough to accommodate at least one improvement.

### Python-side issues

**"ModuleNotFoundError: No module named 'mcboms'"**
You did not run `pip install -e .` from the repo root. Do that, then try again. If the error persists, your `pip` is pointing to a different Python than `python` is — use `python -m pip install -e .` instead.

**"ModuleNotFoundError: No module named 'gurobipy'"**
You do not have Gurobi installed. The framework falls back to CBC automatically. If you still see this error, the fallback is not triggering — check that `pulp` is installed (`pip install pulp`).

**"GUROBI license expired" or "GRBgetkey error"**
Your Gurobi license expired or was never activated. Either renew the academic license or skip Gurobi (the framework will use CBC).

**Tests fail on Windows with path errors.**
Some Windows shells handle path separators differently. Use Git Bash or WSL instead of cmd.exe. If you must use cmd.exe, replace forward slashes with backslashes in commands.

**`python run_harwood_validation.py` prints validation results but no green banner.**
The Level 2a check failed. Run `pytest tests/test_harwood_validation.py -v` to see which specific test failed and what the difference is. Most likely cause: someone modified `economics.py` to use non-Harwood unit costs, breaking the reproduction.

---

## 15. Glossary

- **AADT** — Annual Average Daily Traffic. Vehicles per day at a location, averaged over a year.
- **AMF** — Accident Modification Factor. Multiplier (typically 0.5-1.5) representing the safety effect of a treatment. AMF < 1 means crash reduction. Now usually called CMF (see below).
- **BCA** — Benefit-Cost Analysis.
- **CMF** — Crash Modification Factor. Modern term for AMF. Both terms appear in the literature; the framework treats them synonymously.
- **CPM** — Crash Prediction Module. The IHSDM Crash Prediction Module (Banihashemi Eq 15) predicts expected annual crashes at intersections from ADTs and intersection attributes.
- **HSM** — Highway Safety Manual (AASHTO 2010). The standard reference for safety performance functions and crash modification factors.
- **IHSDM** — Interactive Highway Safety Design Model. FHWA software with the original Crash Prediction Module that Banihashemi used.
- **KABCO** — Five-level crash severity scale: K = fatal, A = incapacitating injury, B = non-incapacitating injury, C = possible injury, O = property damage only.
- **MILP** — Mixed-Integer Linear Programming. The optimization technique MCBOMs uses.
- **PDO** — Property Damage Only. Same as KABCO level O.
- **PNR** — Penalty for Not Resurfacing. Harwood's mechanism for assigning a deferral cost to do-nothing alternatives. Not implemented in MCBOMs because per-site PNR values are not published.
- **PRP** — Penalty for Resurfacing-only Project. Harwood's penalty applied when a site is resurfaced without geometric improvements. Not implemented in MCBOMs.
- **PSB** — Present value of Safety Benefits. Harwood's notation for the safety benefit component.
- **PTOB** — Present value of Traffic Operational Benefits. Harwood's notation for the operational benefit component.
- **PV** — Present Value.
- **PWF** — Present Worth Factor. The factor that converts a stream of equal annual payments to a single present value. Formula: `PWF(r, T) = ((1+r)^T - 1) / (r * (1+r)^T)`. For r=0.07, T=20: PWF = 10.594.
- **RRR** — Resurfacing, Restoration, Rehabilitation. The federal program that funds the kind of pavement work Harwood's case study addresses.
- **RSRAP** — Resurfacing Safety Resource Allocation Program. The software tool Harwood developed.
- **SPF** — Safety Performance Function. A statistical model that predicts expected crashes from facility characteristics.
- **TRR** — Transportation Research Record. The journal where Harwood (2003) and Banihashemi (2007) were published.
- **VOC** — Vehicle Operating Cost. Per-mile fuel, maintenance, and tire costs.
- **VOT** — Value of Time. Hourly rate at which travelers value their time, used to monetize travel time savings.

---

## 16. References

1. Harwood, D. W., Rabbani, E. R. K., & Richard, K. R. (2003). Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects. *Transportation Research Record*, 1840(1), 148–157.
2. Banihashemi, M. (2007). Optimization of highway safety and operation by using crash prediction models with accident modification factors. *Transportation Research Record*, 2019(1), 111–117.
3. AASHTO. (2010). *Highway Safety Manual* (1st ed.). American Association of State Highway and Transportation Officials.
4. USDOT. (2025). *Benefit-Cost Analysis Guidance for Discretionary Grant Programs*, May 2025. U.S. Department of Transportation.
5. FHWA. (2025). *Updated Crash Costs for Highway Safety Analysis*, FHWA-SA-25-021, October 2025. Federal Highway Administration.
6. Vogt, A., & Bared, J. (1998). *Accident Models for Two-Lane Rural Roads: Segments and Intersections*. FHWA-RD-98-133.
7. Federal Highway Administration. (1999). *Interactive Highway Safety Design Model: Crash Prediction Module*, FHWA-RD-99-207.

---

## Contact

For questions about MCBOMs methodology or implementation, contact the Texas A&M Transportation Institute, College Station, TX. Reports of bugs or feature requests should go to the GitHub issues page: https://github.com/sa-ameen/mcboms-optimization/issues.

This work was conducted under FHWA Contract HRSO20240009PR.
