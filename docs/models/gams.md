# GAMS Models

GAMS combines the model declaration and the input data into a single `.gms` file per instance. The format is widely used in transportation, energy, and economic modeling, and is compatible with the GAMS commercial solver suite.

This page renders every GAMS file in `models/gams/`. Each file's source can be expanded inline; download buttons retrieve individual files.

---

## How to run

From a shell:

```bash
gams 02_harwood_50m.gms
```

GAMS compiles the model, invokes the configured solver, and writes a results file. Expected results are documented in [Validation](../validation/index.md).

---

## 00_optimization.gms — Core MCBOMs MILP

The abstract optimization-layer model. Encodes the project-level core and the network-level extensions.

[:material-download: Download `00_optimization.gms`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/gams/00_optimization.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/00_optimization.gms"
    ```

---

## 01_worked_example.gms — Worked Example

Single-segment safety-only instance with the full safety-benefit derivation expressed symbolically.

[:material-download: Download `01_worked_example.gms`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/gams/01_worked_example.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/01_worked_example.gms"
    ```

---

## 02_harwood_50m.gms — Harwood $50M

[:material-download: Download `02_harwood_50m.gms`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/gams/02_harwood_50m.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/02_harwood_50m.gms"
    ```

---

## 02_harwood_10m.gms — Harwood $10M

[:material-download: Download `02_harwood_10m.gms`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/gams/02_harwood_10m.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/02_harwood_10m.gms"
    ```

---

## 03_banihashemi_intersections.gms — Banihashemi Sub-Problem

[:material-download: Download `03_banihashemi_intersections.gms`](https://github.com/ttitamu/mcboms-optimization/raw/main/models/gams/03_banihashemi_intersections.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/03_banihashemi_intersections.gms"
    ```
