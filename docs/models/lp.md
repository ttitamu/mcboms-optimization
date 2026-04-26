# LP Format Models

LP files are flat numeric forms — they cannot represent the abstract model symbolically. Each LP file is an instantiation of the model with specific numeric coefficients. Drop into any MILP solver directly.

This page shows the full content of every LP file in `models/lp/`. Click any file's name to expand its content; use the download links to save individual files.

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

Expected objectives are documented in [Validation](../validation/index.md). All five LP files have been validated with CBC; the optimal objective values match the AMPL/GAMS/Python implementations to the cent.

---

## 00_optimization.lp — Core MCBOMs MILP (illustrative)

LP cannot express abstract symbolic models. This file uses a small 2-project, 4-alternative illustrative example with extensive header comments explaining the structure that all other LP instances follow.

[:material-download: Download `00_optimization.lp`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/lp/00_optimization.lp){ .md-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/00_optimization.lp"
    ```

---

## 01_worked_example.lp — Worked Example

[:material-download: Download `01_worked_example.lp`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/lp/01_worked_example.lp){ .md-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/01_worked_example.lp"
    ```

---

## 02_harwood_50m.lp — Harwood $50M

Expected optimal objective: **$6,159,512** (matches Harwood Table 4 within $5).

[:material-download: Download `02_harwood_50m.lp`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/lp/02_harwood_50m.lp){ .md-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/02_harwood_50m.lp"
    ```

---

## 02_harwood_10m.lp — Harwood $10M

Expected optimal objective: **$4,931,520** (5.5% above Harwood; documented divergence per Section 2.7.3).

[:material-download: Download `02_harwood_10m.lp`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/lp/02_harwood_10m.lp){ .md-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/02_harwood_10m.lp"
    ```

---

## 03_banihashemi_intersections.lp — Banihashemi Sub-Problem

[:material-download: Download `03_banihashemi_intersections.lp`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/lp/03_banihashemi_intersections.lp){ .md-button }

??? abstract "View source"
    ```
    --8<-- "models/lp/03_banihashemi_intersections.lp"
    ```
