# GAMS Models

GAMS combines model and data into a single file per instance. Common in policy and economics modeling.

## Files in `models/gams/`

| File | Purpose |
|---|---|
| `00_optimization.gms` | Core MCBOMs MILP — abstract model |
| `01_worked_example.gms` | Worked example with Eq 2.18 |
| `02_harwood_50m.gms` | Harwood $50M instance |
| `02_harwood_10m.gms` | Harwood $10M instance |
| `03_banihashemi_intersections.gms` | Banihashemi sub-problem |

## Running

From the `models/gams/` directory:

```bash
gams 02_harwood_50m.gms
gams 02_harwood_10m.gms
gams 03_banihashemi_intersections.gms
gams 01_worked_example.gms
```

GAMS will compile the model, invoke the configured solver, and write a results file.

## What `00_optimization.gms` looks like

The core MILP follows the same equation structure as AMPL with GAMS syntax:

```gams
* Eq 2.4 - Objective
Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost_disc(i,j)) * x(i,j));

* Eq 2.5 - total budget
TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

* Eq 2.6 - mutual exclusivity
MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;
```

## Solver compatibility

GAMS runs with any of its supported solvers. Common choices for MILP:

- **CPLEX** (default in many GAMS installations)
- **Gurobi**
- **XA**, **CBC**, **SCIP**, etc.
