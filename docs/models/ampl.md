# AMPL Models

AMPL has the strongest semantic structure of the three formats. The model and data are separate files, so the math is most readable directly from the file.

## Files in `models/ampl/`

| File | Purpose |
|---|---|
| `00_optimization.mod` | Core MCBOMs MILP — abstract model, all 10 constraints declared |
| `01_worked_example.mod` + `.run` | Worked example with full Eq 2.18 chain |
| `02_harwood.mod` | Harwood model (paper-faithful aggregation) |
| `02_harwood_50m.dat` + `.run` | Harwood $50M instance data and script |
| `02_harwood_10m.dat` + `.run` | Harwood $10M instance |
| `03_banihashemi_intersections.mod` + `.dat` + `.run` | Banihashemi sub-problem with full IHSDM CPM |

## Running

From the `models/ampl/` directory:

```bash
ampl 02_harwood_50m.run
ampl 02_harwood_10m.run
ampl 03_banihashemi_intersections.run
ampl 01_worked_example.run
```

Each `.run` script invokes the solver, displays the optimal objective, and shows which alternatives were selected.

## What `00_optimization.mod` looks like

The core MILP is declared abstractly. Sets, parameters, decision variables, objective, and all 10 constraints (Eq 2.4 through 2.10 plus 2.14 through 2.16) are declared. Optional and network-level constraints are activated by populating the corresponding sets in the data file; when the sets are empty, the constraints are vacuously satisfied.

```ampl
# Eq 2.4 - Objective
maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost_disc[i,j]) * x[i,j];

# Eq 2.5 - total budget
subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

# Eq 2.6 - mutual exclusivity
subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;
```

The full file is at `models/ampl/00_optimization.mod` in the repository.

## Solver compatibility

The AMPL files run in any AMPL-compatible solver, including:

- **CPLEX** (commercial, common in transportation research)
- **Gurobi** (commercial, fastest for MILPs of this size)
- **CBC** (open-source)
- **SCIP** (academic, free for non-commercial use)
