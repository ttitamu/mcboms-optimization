# MCBOMs Mathematical Models

This folder contains the formal mathematical models for the MCBOMs MILP framework, expressed in three industry-standard MILP modeling languages.

These are the primary models — the equations from Chapter 2 of the Task 4 Report rendered in solver-readable form. The Python implementation in `src/mcboms/` is one access method; the AMPL, GAMS, and LP files in this folder are another. Reviewers and analysts who use CPLEX, Gurobi, GAMS, or any other commercial MILP solver can run the models directly from this folder without involving Python.

## How this folder is organized

Files are named with a numeric prefix indicating their role in the model hierarchy:

- **`00_`** — the **core MCBOMs optimization model**. The abstract, generic formulation from Chapter 2 Sections 2.2.1 and 2.2.2. This is the framework itself, divorced from any specific case study. Encodes Eq 2.4 through 2.10 (project-level) and Eq 2.14 through 2.16 (network-level).
- **`01_`** — the **worked example** from Chapter 2 Section 2.3.7. A single-segment instance demonstrating Eq 2.18 (safety benefit) end-to-end from raw severity inputs.
- **`02_`** — the **Harwood (2003) case study** instances at $50M and $10M budgets. Uses paper-faithful aggregate values (PSB and PTOB).
- **`03_`** — the **Banihashemi (2007) intersection sub-problem**. Full parametric IHSDM Crash Prediction Module reconstruction.

The same numeric prefix groups files that belong together. For AMPL, this means a `.mod` model file plus its associated `.dat` data file and `.run` script all share the same prefix. For GAMS and LP, each numeric prefix corresponds to a single self-contained file (since GAMS combines model and data, and LP is fully numeric).

## Three formats — same mathematics

The same model is expressed in three solver-language forms. Use whichever format your solver consumes natively:

- **AMPL** (`ampl/`) — `.mod` model + `.dat` data + `.run` execution script. Strongest semantic structure; the math is most readable directly from the file. Reads into CPLEX, Gurobi, or any AMPL-compatible solver.
- **GAMS** (`gams/`) — `.gms` combined model and data, single-file. Common in policy and economics modeling. Reads into GAMS with CPLEX, CONOPT, or any GAMS-compatible solver.
- **LP** (`lp/`) — solver-native format, fully self-contained per file. Numeric form, no symbolic expressions. Reads into CPLEX, Gurobi, CBC, SCIP, and most other MILP solvers directly.

## File inventory

### `ampl/`

| File | Purpose |
|---|---|
| `00_optimization.mod` | Core MCBOMs MILP — abstract model, all 10 constraints |
| `01_worked_example.mod` + `.run` | Worked example (Eq 2.18 end-to-end) |
| `02_harwood.mod` | Harwood model (paper-faithful aggregation) |
| `02_harwood_50m.dat` + `.run` | Harwood $50M instance data and script |
| `02_harwood_10m.dat` + `.run` | Harwood $10M instance |
| `03_banihashemi_intersections.mod` + `.dat` + `.run` | Banihashemi sub-problem with full IHSDM CPM |

### `gams/`

| File | Purpose |
|---|---|
| `00_optimization.gms` | Core MCBOMs MILP — abstract model |
| `01_worked_example.gms` | Worked example with Eq 2.18 |
| `02_harwood_50m.gms` | Harwood $50M instance |
| `02_harwood_10m.gms` | Harwood $10M instance |
| `03_banihashemi_intersections.gms` | Banihashemi sub-problem |

### `lp/`

| File | Purpose |
|---|---|
| `00_optimization.lp` | Core model structure with annotated 2-project illustrative example |
| `01_worked_example.lp` | Worked example evaluated to numeric coefficients |
| `02_harwood_50m.lp` | Harwood $50M evaluated coefficients |
| `02_harwood_10m.lp` | Harwood $10M evaluated coefficients |
| `03_banihashemi_intersections.lp` | Banihashemi sub-problem evaluated coefficients |

## Note on the LP format

LP files are flat numeric forms — they cannot represent the abstract model symbolically (no sets, no indexed sums, no parameter formulas). Each LP file is an instantiation of the model with specific numbers. The `00_optimization.lp` file therefore shows the structural form of an MCBOMs LP using a small 2-project illustrative example, with comment blocks that describe how to read the file and how the other LP instances extend the same pattern.

For the abstract symbolic form, see `00_optimization.mod` (AMPL) or `00_optimization.gms` (GAMS).

## Running the models

### AMPL

From the `ampl/` directory:

```
ampl 02_harwood_50m.run
ampl 02_harwood_10m.run
ampl 03_banihashemi_intersections.run
ampl 01_worked_example.run
```

### GAMS

From the `gams/` directory:

```
gams 02_harwood_50m.gms
gams 02_harwood_10m.gms
gams 03_banihashemi_intersections.gms
gams 01_worked_example.gms
```

### LP (solver-direct)

From the `lp/` directory, with CPLEX:

```
cplex
> read 02_harwood_50m.lp
> mipopt
> display solution variables -
```

Or with Gurobi:

```
gurobi_cl 02_harwood_50m.lp
```

## Expected results

| Instance | Optimal objective | Notes |
|---|---|---|
| `00_optimization` | $300 | Illustrative 2-project example, $300K budget |
| `01_worked_example` | $1,493,914 | Net benefit at $1M budget |
| `02_harwood_50m` | $6,159,512 | Matches Harwood Table 4 within $5 rounding |
| `02_harwood_10m` | $4,931,520 | 5.5% above Harwood's published $4,675,033 (no PNR; documented in Chapter 2 Section 2.7.3) |
| `03_banihashemi_intersections` | varies by budget | Int 12:LTL is most cost-effective (B/C ≈ 11.5) |

The LP files have been validated by solving with CBC; the optimal objective values match the Python implementation numerically.

## Data scope

The four numbered instance groups do not all reach the same level of parametric detail. This is honest about what data is publicly available:

- **`01_worked_example`** is fully parametric end-to-end. All raw inputs (annual crash count, severity distribution, CMF, unit costs, discount parameters) are declared in the model file. The optimizer can recompute the safety benefit from raw inputs every time.
- **`03_banihashemi_intersections`** is fully parametric for the IHSDM crash prediction module. Per-intersection ADTs, skew angles, traffic control, LTL/ISD attributes, and delay times are inputs; the model computes crashes/year via Banihashemi Eq 15 and the (crash + delay) cost over 20 years. The AMF values used (Skew, Traffic Control, LTL, Sight Distance) are standard IHSDM/Vogt-Bared values; Banihashemi did not publish his exact AMF values in the paper.
- **`02_harwood_50m`** and **`02_harwood_10m`** use Harwood's published per-site, per-alternative values from Tables 2 and 3 directly (resurfacing cost, safety improvement cost, PSB, PTOB). Harwood's RSRAP computes PSB internally from per-severity AMFs and accident frequencies (his Eq 1, paper page 151), but those raw inputs are not published in the paper — only the aggregate PSB values are. Reconstructing Harwood's per-severity inputs would require fabricating data; instead, this file uses Harwood's published aggregates and demonstrates the per-severity Eq 2.18 chain in `01_worked_example` instead.

## Mathematical reference

All files reference equations by their Chapter 2 numbering (Eq 2.4 = project-level objective, Eq 2.5 = total budget, Eq 2.18 = safety benefit, etc.). The full mathematical formulation is in `docs/chapter2/`.
