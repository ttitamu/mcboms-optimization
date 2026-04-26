# Architecture

The Python code is organized as a standard Python package under `src/mcboms/`. This page shows the full structure with inline source code for every module — click "View source" on any module to see its content.

---

## Package layout

```
src/mcboms/
├── __init__.py                  Package init
├── core/                        MILP optimizer
│   ├── __init__.py
│   ├── optimizer.py             All 9 constraints (Eq 2.4–2.10, 2.14–2.16)
│   └── alternatives.py
├── benefits/                    Benefit calculation modules
│   ├── __init__.py
│   ├── safety.py                Eq 2.18 (HSM-based)
│   ├── operations.py            Eq 2.21 (travel-time + VOC)
│   └── ccm.py                   Eq 2.27 (energy, emissions, accessibility, resilience, pavement)
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

The MILP optimizer. Construct with sites, alternatives, budget, discount rate, and analysis horizon, plus optional kwargs for the additional constraints. Call `.solve()` to run the MILP. Uses Gurobi.

The optimizer implements the full project-level and network-level formulation:

| Equation | Constraint | Activated by |
|---|---|---|
| Eq 2.4 | Objective (max net benefit) | always |
| Eq 2.5 | Total budget | always |
| Eq 2.6 | Mutual exclusivity | always |
| Eq 2.7 | Binary | always |
| Eq 2.8 | Dependency | `dependencies=` kwarg |
| Eq 2.9 | Cross-project exclusivity | `conflicts=` kwarg |
| Eq 2.10 | Minimum BCR | `min_bcr=` kwarg |
| Eq 2.14 | Facility-type sub-budget | `facility_budgets=` kwarg |
| Eq 2.15 | Regional cap | `regional_caps=` kwarg |
| Eq 2.16 | Regional minimum-investment floor | `regional_floors=` kwarg |

When optional constraints are not provided, the corresponding equations are vacuously satisfied — the same model handles project-level-only and network-level-extended cases.

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

| Module | Equation | Tests |
|---|---|---|
| `safety.py` | Eq 2.18 | 16 |
| `operations.py` | Eq 2.21 | 26 |
| `ccm.py` | Eq 2.27 | 34 |

### `safety.py` — Eq 2.18 implementation

`compute_safety_benefit()` takes per-severity inputs and returns the present-value benefit. Validated against the worked example to the cent (16 unit tests in `tests/test_safety.py`).

[:material-download: Download `safety.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/benefits/safety.py){ .md-button }

??? abstract "View source: safety.py"
    ```python
    --8<-- "src/mcboms/benefits/safety.py"
    ```

### `operations.py` — Eq 2.21 implementation

Travel-time savings and vehicle-operating-cost reductions, summed across vehicle classes and converted to present value via PWF. USDOT BCA May 2025 default unit values for VOT, OCC, VOC. Component functions for each term, an aggregator over vehicle classes, a convenience helper for the single-passenger-class case, and a DataFrame batch interface.

[:material-download: Download `operations.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/benefits/operations.py){ .md-button }

??? abstract "View source: operations.py"
    ```python
    --8<-- "src/mcboms/benefits/operations.py"
    ```

### `ccm.py` — Eq 2.27 implementation

Corridor Condition Measures across five categories: energy, emissions, accessibility, resilience, and pavement / asset condition. Per-category monetization functions, a top-level aggregator with explicit double-counting prevention against `operations.py` (the accessibility category overlaps with the operational benefit's mobility component), and a DataFrame batch interface. Default unit values from USDOT BCA May 2025, EPA Social Cost of Carbon, FEMA Standard Economic Values v13.

[:material-download: Download `ccm.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/src/mcboms/benefits/ccm.py){ .md-button }

??? abstract "View source: ccm.py"
    ```python
    --8<-- "src/mcboms/benefits/ccm.py"
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

`pytest tests/ -q` runs **109 tests** covering the worked example, Harwood reproduction, safety module, operations module, CCM module, and the new optimizer constraints (Eq 2.8–2.10, 2.14–2.16).

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

### `test_operations.py` — operations module unit tests

[:material-download: Download `test_operations.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/tests/test_operations.py){ .md-button }

??? abstract "View source: test_operations.py"
    ```python
    --8<-- "tests/test_operations.py"
    ```

### `test_ccm.py` — CCM module unit tests

[:material-download: Download `test_ccm.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/tests/test_ccm.py){ .md-button }

??? abstract "View source: test_ccm.py"
    ```python
    --8<-- "tests/test_ccm.py"
    ```

### `test_optimizer_constraints.py` — optional and network constraint tests

[:material-download: Download `test_optimizer_constraints.py`](https://github.com/sa-ameen/mcboms-optimization/raw/main/tests/test_optimizer_constraints.py){ .md-button }

??? abstract "View source: test_optimizer_constraints.py"
    ```python
    --8<-- "tests/test_optimizer_constraints.py"
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
