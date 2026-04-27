# LP Format Models

The LP format is the standard solver-native flat representation of a linear or mixed-integer linear program. Unlike AMPL or GAMS, the LP format does not carry symbolic structure: each constraint appears as an explicit numeric row, and variables are listed individually. The format is read by every major MILP solver, including CPLEX, Gurobi, CBC, and MOSEK, without modification.

This page renders every LP file in `models/lp/`. Each file's source can be expanded inline; download buttons retrieve individual files.

---

## How to run

With CPLEX:

```
cplex
> read 02_harwood_50m.lp
> mipopt
> display solution objective
```

With Gurobi:

```bash
gurobi_cl 02_harwood_50m.lp
```

With CBC (free, open-source):

```bash
cbc 02_harwood_50m.lp solve
```

Expected objectives are documented in [Validation](../validation/index.md). All five LP files have been validated with CBC; the optimal objective values match the AMPL/GAMS/Python implementations numerically.

---

## 00_optimization.lp — Core MCBOMs MILP (illustrative)

The abstract optimization layer cannot be expressed symbolically in LP format. This file is a minimal two-project, four-alternative instance with extensive header comments documenting the constraint structure that the other LP instances expand on.

[:material-download: Download `00_optimization.lp`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/lp/00_optimization.lp){ .md-button .file-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/00_optimization.lp"
    ```

---

## 01_worked_example.lp — Worked Example

[:material-download: Download `01_worked_example.lp`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/lp/01_worked_example.lp){ .md-button .file-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/01_worked_example.lp"
    ```

---

## 02_harwood_50m.lp — Harwood $50M

Expected optimal objective: **$6,159,512** (matches Harwood Table 4 within $5).

[:material-download: Download `02_harwood_50m.lp`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/lp/02_harwood_50m.lp){ .md-button .file-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/02_harwood_50m.lp"
    ```

---

## 02_harwood_10m.lp — Harwood $10M

Expected optimal objective: **$4,931,520** (5.5% above Harwood; documented divergence per Section 2.7.3).

[:material-download: Download `02_harwood_10m.lp`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/lp/02_harwood_10m.lp){ .md-button .file-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/02_harwood_10m.lp"
    ```

---

## 03_banihashemi_intersections.lp — Banihashemi Sub-Problem

[:material-download: Download `03_banihashemi_intersections.lp`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/lp/03_banihashemi_intersections.lp){ .md-button .file-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/03_banihashemi_intersections.lp"
    ```
