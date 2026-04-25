# LP Format Models

LP files are flat numeric forms — they cannot represent the abstract model symbolically. Each LP file is an instantiation of the model with specific numbers. Drop into any MILP solver directly.

## Files in `models/lp/`

| File | Purpose |
|---|---|
| `00_optimization.lp` | Core model structure with annotated 2-project illustrative example |
| `01_worked_example.lp` | Worked example evaluated to numeric coefficients |
| `02_harwood_50m.lp` | Harwood $50M evaluated coefficients |
| `02_harwood_10m.lp` | Harwood $10M evaluated coefficients |
| `03_banihashemi_intersections.lp` | Banihashemi sub-problem evaluated coefficients |

## Running

With CPLEX:

```
cplex
> read models/lp/02_harwood_50m.lp
> mipopt
> display solution objective
```

Expected: `Objective value of the MIP = 6,159,512.00`.

With Gurobi:

```bash
gurobi_cl models/lp/02_harwood_50m.lp
```

Expected: `Optimal objective: 6.159512e+06`.

With CBC (free, open-source):

```bash
cbc models/lp/02_harwood_50m.lp solve
```

## What an LP file looks like

LP files contain:

- An `OBJ:` line with the objective function (max or min, listing each variable's coefficient)
- A `Subject To:` block with constraint rows (e.g., `Constraint_name: 100 x_1 + 200 x_2 <= 500`)
- A `Binaries` block listing all binary variables
- An `End` marker

Example excerpt from `02_harwood_50m.lp`:

```
\* Harwood et al. (2003) - Harwood 50M *\
\* Per-alternative coefficient = total_benefit - safety_improvement_cost *\
\* Expected optimal objective Z = $6,159,512 *\
Maximize
OBJ: 1356661 x_10_1 + 35107 x_1_1 + 279756 x_2_1 + 628606 x_3_1
   + 261392 x_4_1 + 1168618 x_5_1 + 341437 x_6_1 + 680641 x_7_1
   + 525644 x_8_1 + 590056 x_8_2 + 817238 x_9_1
Subject To
MutEx_1: x_1_0 + x_1_1 <= 1
...
```

The header comments explain how each coefficient was derived from the source data (Harwood Tables 2 and 3 in this case).

## Why we provide LP files

LP files are the universal exchange format. Every MILP solver reads LP. If a reviewer has CPLEX, Gurobi, CBC, SCIP, FICO Xpress, or any combination, they can read these files without any model-language compiler.

For symbolic readability, see the [AMPL](ampl.md) or [GAMS](gams.md) models, which retain the parametric structure.
