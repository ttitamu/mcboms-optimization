# Architecture

The Python code is organized as a standard Python package under `src/mcboms/`. This page shows the full structure with inline source code for every module — click "View source" on any module to see its content.

---

## Package layout

```
src/mcboms/
├── __init__.py                  Package init
├── core/                        MILP optimizer
│   ├── __init__.py
│   ├── optimizer.py
│   └── alternatives.py
├── benefits/                    Benefit calculation modules
│   ├── __init__.py
│   ├── safety.py                Eq 2.18 (HSM-based) — implemented
│   ├── operations.py            Eq 2.21 — in development
│   └── ccm.py                   Eq 2.27 — in development
├── io/                          Input/output modules
│   ├── __init__.py
│   ├── readers.py
│   ├── writers.py
│   └── colleague_workbook.py
├── utils/                       Utilities
│   ├── __init__.py
│   └── economics.py
└── data/                        Bundled validation data
    ├── __init__.py
    └── harwood_alternatives.py
```

---

## `mcboms.core`

### `optimizer.py` — main `Optimizer` class

The MILP optimizer. Construct with sites, alternatives, budget, discount rate, and analysis horizon. Call `.solve()` to run the MILP. Uses Gurobi if available, falls back to CBC via PuLP.

[:material-download: Download `optimizer.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/core/optimizer.py){ .md-button }

??? abstract "View source: optimizer.py"
    ```python
    --8<-- "src/mcboms/core/optimizer.py"
    ```

### `alternatives.py` — alternative enumeration helpers

[:material-download: Download `alternatives.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/core/alternatives.py){ .md-button }

??? abstract "View source: alternatives.py"
    ```python
    --8<-- "src/mcboms/core/alternatives.py"
    ```

??? abstract "View source: core/__init__.py"
    ```python
    --8<-- "src/mcboms/core/__init__.py"
    ```

---

## `mcboms.benefits`

This package houses the benefit-equation implementations.

| Module | Status | Equation |
|---|---|---|
| `safety.py` | ✓ Implemented | Eq 2.18 |
| `operations.py` | In development | Eq 2.21 |
| `ccm.py` | In development | Eq 2.27 |

### `safety.py` — Eq 2.18 implementation

`compute_safety_benefit()` takes per-severity inputs and returns the present-value benefit. Validated against the worked example to the cent (16 unit tests in `tests/test_safety.py`).

[:material-download: Download `safety.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/benefits/safety.py){ .md-button }

??? abstract "View source: safety.py"
    ```python
    --8<-- "src/mcboms/benefits/safety.py"
    ```

??? abstract "View source: benefits/__init__.py"
    ```python
    --8<-- "src/mcboms/benefits/__init__.py"
    ```

---

## `mcboms.io`

Input/output modules for reading data files and writing results.

### `readers.py` — generic CSV readers

[:material-download: Download `readers.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/io/readers.py){ .md-button }

??? abstract "View source: readers.py"
    ```python
    --8<-- "src/mcboms/io/readers.py"
    ```

### `writers.py` — results output

[:material-download: Download `writers.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/io/writers.py){ .md-button }

??? abstract "View source: writers.py"
    ```python
    --8<-- "src/mcboms/io/writers.py"
    ```

### `colleague_workbook.py` — TTI BCA spreadsheet reader

Reads the parallel TTI Task 4 benefit-cost analysis Excel workbook and converts it to optimizer-input format.

[:material-download: Download `colleague_workbook.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/io/colleague_workbook.py){ .md-button }

??? abstract "View source: colleague_workbook.py"
    ```python
    --8<-- "src/mcboms/io/colleague_workbook.py"
    ```

??? abstract "View source: io/__init__.py"
    ```python
    --8<-- "src/mcboms/io/__init__.py"
    ```

---

## `mcboms.utils`

### `economics.py` — discounting and unit costs

PWF computation, USDOT BCA May 2025 default unit costs (crash costs, value of time, vehicle operating cost). Every value is documented with its source in the file.

[:material-download: Download `economics.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/utils/economics.py){ .md-button }

??? abstract "View source: economics.py"
    ```python
    --8<-- "src/mcboms/utils/economics.py"
    ```

??? abstract "View source: utils/__init__.py"
    ```python
    --8<-- "src/mcboms/utils/__init__.py"
    ```

---

## `mcboms.data`

### `harwood_alternatives.py` — Harwood (2003) bundled data

Returns a DataFrame of 21 alternatives across 10 sites with all the published cost and benefit components.

[:material-download: Download `harwood_alternatives.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/data/harwood_alternatives.py){ .md-button }

??? abstract "View source: harwood_alternatives.py"
    ```python
    --8<-- "src/mcboms/data/harwood_alternatives.py"
    ```

??? abstract "View source: data/__init__.py"
    ```python
    --8<-- "src/mcboms/data/__init__.py"
    ```

??? abstract "View source: mcboms/__init__.py"
    ```python
    --8<-- "src/mcboms/__init__.py"
    ```

---

## Tests

`pytest tests/ -q` runs 32 tests covering the worked example, Harwood reproduction, and per-component unit tests for the safety module.

### `test_harwood_validation.py` — Harwood reproduction tests

[:material-download: Download `test_harwood_validation.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/tests/test_harwood_validation.py){ .md-button }

??? abstract "View source: test_harwood_validation.py"
    ```python
    --8<-- "tests/test_harwood_validation.py"
    ```

### `test_safety.py` — safety module unit tests

[:material-download: Download `test_safety.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/tests/test_safety.py){ .md-button }

??? abstract "View source: test_safety.py"
    ```python
    --8<-- "tests/test_safety.py"
    ```

---

## Top-level scripts

### `run_harwood_validation.py` — end-to-end Harwood validation

Runs both Level 2a (rigorous $50M check) and Level 2b (documented $10M divergence). Prints a complete validation summary.

[:material-download: Download `run_harwood_validation.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/run_harwood_validation.py){ .md-button }

??? abstract "View source: run_harwood_validation.py"
    ```python
    --8<-- "run_harwood_validation.py"
    ```

### `examples/banihashemi_intersections.py` — Banihashemi sub-problem reproduction

Builds the alternative table from raw IHSDM CPM inputs, runs the optimizer at the unconstrained budget, prints the structural results.

[:material-download: Download `banihashemi_intersections.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/examples/banihashemi_intersections.py){ .md-button }

??? abstract "View source: banihashemi_intersections.py"
    ```python
    --8<-- "examples/banihashemi_intersections.py"
    ```
