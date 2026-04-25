# MCBOMs Mathematical Models

This folder contains the formal mathematical models for the MCBOMs MILP framework, expressed in three industry-standard MILP modeling languages.

These are the primary models — the equations from Chapter 2 of the Task 4 Report rendered in solver-readable form. The Python implementation in `src/mcboms/` is one access method; the AMPL, GAMS, and LP files in this folder are another. Reviewers and analysts who use CPLEX, Gurobi, GAMS, or any other commercial MILP solver can run the models directly from this folder without involving Python.

## Formats

- **AMPL** (`ampl/`) — `.mod` model + `.dat` data + `.run` execution script. Reads into CPLEX, Gurobi, or any AMPL-compatible solver.
- **GAMS** (`gams/`) — `.gms` combined model and data, single-file. Reads into GAMS with CPLEX, CONOPT, or any GAMS-compatible solver.
- **LP** (`lp/`) — solver-native format, fully self-contained per file. Reads into CPLEX, Gurobi, CBC, SCIP, and most other MILP solvers directly.

## Instances

Each format contains four instances:

| Instance | Purpose | Equations exercised |
|---|---|---|
| `worked_example` | Single-segment safety-only example from Chapter 2 Section 2.3.7 | Full Eq 2.18 chain (severity disaggregation → CMF → annual → PWF → PV) plus Eq 2.4–2.7 |
| `harwood_50m` | Harwood (2003) 10-site case study, $50M budget | Eq 2.2 aggregation (PSB + PTOB) plus Eq 2.4–2.7 |
| `harwood_10m` | Harwood (2003), $10M budget | Same as `harwood_50m` |
| `banihashemi_intersections` | Banihashemi (2007) 13-intersection sub-problem | Full Banihashemi Eq 15 (IHSDM CPM) chain plus Eq 2.4–2.7 |

## Data scope

The files do not all reach the same level of parametric detail. This is honest about what data is publicly available:

- **`worked_example`** is fully parametric end-to-end. All raw inputs (annual crash count, severity distribution, CMF, unit costs, discount parameters) are declared in the model file. The optimizer can recompute the safety benefit from raw inputs every time.
- **`banihashemi_intersections`** is fully parametric for the IHSDM crash prediction module. Per-intersection ADTs, skew angles, traffic control, LTL/ISD attributes, and delay times are inputs; the model computes crashes/year via Banihashemi Eq 15 and the (crash + delay) cost over 20 years. The AMF values used (Skew, Traffic Control, LTL, Sight Distance) are standard IHSDM/Vogt-Bared values; Banihashemi did not publish his exact AMF values in the paper.
- **`harwood_50m`** and **`harwood_10m`** use Harwood's published per-site, per-alternative values from Tables 2 and 3 directly (resurfacing cost, safety improvement cost, PSB, PTOB). Harwood's RSRAP computes PSB internally from per-severity AMFs and accident frequencies (his Eq 1, paper page 151), but those raw inputs are not published in the paper — only the aggregate PSB values are. Reconstructing Harwood's per-severity inputs would require fabricating data; instead, this file uses Harwood's published aggregates and demonstrates the per-severity Eq 2.18 chain in `worked_example` instead.

## Running

### AMPL

From the `ampl/` directory:

```
ampl harwood_50m.run
ampl harwood_10m.run
ampl banihashemi_intersections.run
ampl worked_example.run
```

### GAMS

From the `gams/` directory:

```
gams harwood_50m.gms
gams harwood_10m.gms
gams banihashemi_intersections.gms
gams worked_example.gms
```

### LP (solver-direct)

From the `lp/` directory, with CPLEX:

```
cplex
> read harwood_50m.lp
> mipopt
> display solution variables -
```

Or with Gurobi:

```
gurobi_cl harwood_50m.lp
```

## Expected results

| Instance | Optimal objective | Notes |
|---|---|---|
| `worked_example` | $1,493,914 | Net benefit at $1M budget |
| `harwood_50m` | $6,159,512 | Matches Harwood Table 4 within $5 rounding |
| `harwood_10m` | $4,931,520 | 5.5% above Harwood's published $4,675,033 (no PNR; documented in Chapter 2 Section 2.7.3) |
| `banihashemi_intersections` | varies by budget | Int 12:LTL is most cost-effective (B/C ≈ 11.5) |

The LP files have been validated by solving with CBC; the optimal objective values match the Python implementation to the cent.

## Mathematical reference

All files reference equations by their Chapter 2 numbering (Eq 2.4 = project-level objective, Eq 2.5 = total budget, Eq 2.18 = safety benefit, etc.). The full mathematical formulation is in `docs/chapter2/`.
