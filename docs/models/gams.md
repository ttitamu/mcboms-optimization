# GAMS Models

GAMS combines model and data into a single file per instance. Common in policy and economics modeling.

This page shows the full content of every GAMS file in `models/gams/`. Click any file's name to expand its content; use the download links to save individual files.

---

## How to run

From a shell:

```bash
gams 02_harwood_50m.gms
```

GAMS compiles the model, invokes the configured solver, and writes a results file. Expected results are documented in [Validation](../validation/index.md).

---

## 00_optimization.gms — Core MCBOMs MILP

The abstract optimization-layer model. Encodes Eq 2.4 through 2.10 (project-level) and Eq 2.14 through 2.16 (network-level extensions).

[:material-download: Download `00_optimization.gms`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/gams/00_optimization.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/00_optimization.gms"
    ```

---

## 01_worked_example.gms — Worked Example

Single-segment safety-only example with the full Eq 2.18 chain.

[:material-download: Download `01_worked_example.gms`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/gams/01_worked_example.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/01_worked_example.gms"
    ```

---

## 02_harwood_50m.gms — Harwood $50M

[:material-download: Download `02_harwood_50m.gms`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/gams/02_harwood_50m.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/02_harwood_50m.gms"
    ```

---

## 02_harwood_10m.gms — Harwood $10M

[:material-download: Download `02_harwood_10m.gms`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/gams/02_harwood_10m.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/02_harwood_10m.gms"
    ```

---

## 03_banihashemi_intersections.gms — Banihashemi Sub-Problem

[:material-download: Download `03_banihashemi_intersections.gms`](https://github.com/sa-ameen/mcboms-optimization/raw/main/models/gams/03_banihashemi_intersections.gms){ .md-button }

??? abstract "View source"
    ```gams
    --8<-- "models/gams/03_banihashemi_intersections.gms"
    ```
