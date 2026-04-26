# AMPL Models

AMPL separates the model declaration (`.mod`), the input data (`.dat`), and the run script (`.run`) into distinct files. This separation places the algebraic structure of the formulation directly in the model file, with no numerical clutter — the constraints and objective read close to the form used in the methodology document. The files are compatible with any AMPL-supported solver, including CPLEX, Gurobi, and CBC.

This page renders every AMPL file in `models/ampl/`. Each file's source can be expanded inline; download buttons retrieve individual files.

---

## How to run

Place all the `.mod`, `.dat`, and `.run` files in the same directory. Then from a shell:

```bash
ampl 02_harwood_50m.run
```

Each `.run` script invokes the solver, prints the optimal objective, and lists which alternatives were selected. Expected results are documented in [Validation](../validation/index.md).

---

## 00_optimization.mod — Core MCBOMs MILP

The abstract optimization-layer model. Encodes the project-level core and the network-level extensions. Optional and network-level constraints are activated by populating the corresponding sets in the data file.

[:material-download: Download `00_optimization.mod`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/00_optimization.mod){ .md-button }

??? abstract "View source"
    ```ampl
    --8<-- "models/ampl/00_optimization.mod"
    ```

---

## 01_worked_example.mod — Worked Example

Single-segment safety-only instance with the full safety-benefit derivation declared parametrically. Severity disaggregation, CMF application, and present-worth conversion are all expressed symbolically in the model file.

[:material-download: Download `01_worked_example.mod`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/01_worked_example.mod){ .md-button }
[:material-download: Download `01_worked_example.run`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/01_worked_example.run){ .md-button }

??? abstract "View 01_worked_example.mod"
    ```ampl
    --8<-- "models/ampl/01_worked_example.mod"
    ```

??? abstract "View 01_worked_example.run"
    ```ampl
    --8<-- "models/ampl/01_worked_example.run"
    ```

---

## 02_harwood — Harwood (2003) Case Study

Paper-faithful Harwood reproduction. Uses Tables 2 and 3 of the paper directly (PSB and PTOB as published aggregates). Two budget instances: $50M and $10M.

The model file is shared between the two budget instances; only the data and run files differ.

[:material-download: Download `02_harwood.mod`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/02_harwood.mod){ .md-button }

??? abstract "View 02_harwood.mod (model file, shared by both budgets)"
    ```ampl
    --8<-- "models/ampl/02_harwood.mod"
    ```

### $50M instance

[:material-download: Download `02_harwood_50m.dat`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/02_harwood_50m.dat){ .md-button }
[:material-download: Download `02_harwood_50m.run`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/02_harwood_50m.run){ .md-button }

??? abstract "View 02_harwood_50m.dat"
    ```ampl
    --8<-- "models/ampl/02_harwood_50m.dat"
    ```

??? abstract "View 02_harwood_50m.run"
    ```ampl
    --8<-- "models/ampl/02_harwood_50m.run"
    ```

### $10M instance

[:material-download: Download `02_harwood_10m.dat`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/02_harwood_10m.dat){ .md-button }
[:material-download: Download `02_harwood_10m.run`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/02_harwood_10m.run){ .md-button }

??? abstract "View 02_harwood_10m.dat"
    ```ampl
    --8<-- "models/ampl/02_harwood_10m.dat"
    ```

??? abstract "View 02_harwood_10m.run"
    ```ampl
    --8<-- "models/ampl/02_harwood_10m.run"
    ```

---

## 03_banihashemi_intersections — Banihashemi (2007) Sub-Problem

Full parametric IHSDM Crash Prediction Module. Per-intersection ADTs, skew angles, traffic control, LTL/ISD attributes are inputs; the model computes crashes/year from Banihashemi Eq 15.

[:material-download: Download `03_banihashemi_intersections.mod`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/03_banihashemi_intersections.mod){ .md-button }
[:material-download: Download `03_banihashemi_intersections.dat`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/03_banihashemi_intersections.dat){ .md-button }
[:material-download: Download `03_banihashemi_intersections.run`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/ampl/03_banihashemi_intersections.run){ .md-button }

??? abstract "View 03_banihashemi_intersections.mod"
    ```ampl
    --8<-- "models/ampl/03_banihashemi_intersections.mod"
    ```

??? abstract "View 03_banihashemi_intersections.dat"
    ```ampl
    --8<-- "models/ampl/03_banihashemi_intersections.dat"
    ```

??? abstract "View 03_banihashemi_intersections.run"
    ```ampl
    --8<-- "models/ampl/03_banihashemi_intersections.run"
    ```
