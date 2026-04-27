# Architecture

The Python code is organized as a standard Python package under `src/mcboms/`. This page shows the full structure with inline source code for every module — click "View source" on any module to see its content.

## Interactive examples

Three notebooks accompany this codebase. Each is self-contained: it pulls the framework from this repository, runs an end-to-end case, and prints a result that can be checked against a reference value.

<div class="run-on-colab" markdown>
[:simple-googlecolab: &nbsp; Worked example](https://colab.research.google.com/github/ttitamu/mcboms-optimization/blob/main/notebooks/01_worked_example.ipynb){ .md-button .colab-button target="_blank" rel="noopener" }
[:simple-googlecolab: &nbsp; Harwood case study](https://colab.research.google.com/github/ttitamu/mcboms-optimization/blob/main/notebooks/02_harwood_50m.ipynb){ .md-button .colab-button target="_blank" rel="noopener" }
[:simple-googlecolab: &nbsp; Optimizer capabilities](https://colab.research.google.com/github/ttitamu/mcboms-optimization/blob/main/notebooks/03_optimizer_capabilities.ipynb){ .md-button .colab-button target="_blank" rel="noopener" }
</div>

The first notebook derives the safety benefit for a single rural two-lane segment from KABCO crash counts and unit costs, then verifies that the optimizer reproduces the manual derivation. The second reproduces Harwood et al. (2003) at the $50M unconstrained budget and compares against published Table 4 values. The third is a synthetic 6-site network that exercises every optional constraint type — dependencies, conflicts, minimum BCR, facility-type sub-budgets, regional caps, and regional floors — to demonstrate the optimizer's full capability surface.

---

## Package layout

```
src/mcboms/
├── __init__.py                  Package init
├── core/                        MILP optimizer
│   ├── __init__.py
│   ├── optimizer.py             Project-level and network-level constraints
│   └── alternatives.py
├── benefits/                    Benefit calculation modules
│   ├── __init__.py
│   ├── safety.py                HSM-based safety benefit
│   ├── operations.py            Travel-time and vehicle-operating-cost benefit
│   └── ccm.py                   Corridor condition measures (energy, emissions, accessibility, resilience, pavement)
├── io/                          Input/output modules
│   ├── __init__.py
│   ├── readers.py
│   ├── writers.py
│   └── bca_workbook.py          BCA workbook import adapter
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

The MILP optimizer. Construct with sites, alternatives, and budget; pass optional kwargs to activate additional constraints. Call `.solve()` to run. The backend auto-detects: prefers Gurobi when installed, otherwise falls back to PuLP+CBC. Pass `solver="pulp"` or `solver="gurobi"` to force a choice.

The constructor accepts the following optional constraints, each activated only when the corresponding kwarg is provided:

| Constraint | Kwarg | Methodology |
|---|---|---|
| Project dependencies (alternative A requires alternative B) | `dependencies=` | Section 2.2.1 |
| Cross-project exclusivity (two alternatives cannot both be selected) | `conflicts=` | Section 2.2.1 |
| Minimum benefit-cost ratio per project | `min_bcr=` | Section 2.2.1 |
| Facility-type sub-budgets | `facility_budgets=` | Section 2.2.2 |
| Regional spending caps | `regional_caps=` | Section 2.2.2 |
| Regional minimum-investment floors | `regional_floors=` | Section 2.2.2 |

When optional kwargs are not provided, the corresponding constraints are inactive — the same class handles project-level-only and full network-level cases. The methodology PDF gives the formal mathematical statement of each constraint with its equation number.

<div class="action-buttons" markdown>
[:material-download: &nbsp; Download `optimizer.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/core/optimizer.py){ .md-button .file-button target="_blank" rel="noopener" }
</div>

??? abstract "View source: optimizer.py"
    ```python
    --8<-- "src/mcboms/core/optimizer.py"
    ```

### `alternatives.py` — alternative enumeration helpers

[:material-download: Download `alternatives.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/core/alternatives.py){ .md-button .file-button target="_blank" rel="noopener" }

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

This package houses the three benefit-equation implementations.

| Module | Purpose | Tests |
|---|---|---|
| `safety.py` | Safety benefit (HSM crash-modification methodology) | 16 |
| `operations.py` | Operational benefit (travel-time + vehicle operating cost) | 26 |
| `ccm.py` | Corridor condition benefit (energy, emissions, accessibility, resilience, pavement) | 34 |

### `safety.py`

Computes the present-value safety benefit from per-severity inputs. Validated against the worked example to within numerical precision.

[:material-download: Download `safety.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/benefits/safety.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: safety.py"
    ```python
    --8<-- "src/mcboms/benefits/safety.py"
    ```

### `operations.py`

Travel-time savings and vehicle-operating-cost reductions, summed across vehicle classes and converted to present value. USDOT BCA May 2025 default unit values for value of time, occupancy, and operating cost. Component functions for each term, an aggregator over vehicle classes, a convenience helper for the single-passenger-class case, and a DataFrame batch interface.

[:material-download: Download `operations.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/benefits/operations.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: operations.py"
    ```python
    --8<-- "src/mcboms/benefits/operations.py"
    ```

### `ccm.py`

Corridor Condition Measures across five categories: energy, emissions, accessibility, resilience, and pavement / asset condition. Per-category monetization functions and a top-level aggregator with explicit double-counting prevention against `operations.py` (the accessibility category overlaps with the operational benefit's mobility component). Default unit values from USDOT BCA May 2025, EPA Social Cost of Carbon, and FEMA Standard Economic Values v13.

[:material-download: Download `ccm.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/benefits/ccm.py){ .md-button .file-button target="_blank" rel="noopener" }

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

[:material-download: Download `readers.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/io/readers.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: readers.py"
    ```python
    --8<-- "src/mcboms/io/readers.py"
    ```

### `writers.py` — results output

[:material-download: Download `writers.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/io/writers.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: writers.py"
    ```python
    --8<-- "src/mcboms/io/writers.py"
    ```

### `bca_workbook.py` — TTI BCA workbook reader

Imports the parallel TTI BCA Excel workbook, reconstructs its per-segment safety benefit using `safety.py`, and converts the segment data to the optimizer's `SafetySegment` format. Used to reconcile the workbook's precomputed values against this codebase's implementation.

[:material-download: Download `bca_workbook.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/io/bca_workbook.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: bca_workbook.py"
    ```python
    --8<-- "src/mcboms/io/bca_workbook.py"
    ```

??? abstract "View source: io/__init__.py"
    ```python
    --8<-- "src/mcboms/io/__init__.py"
    ```

---

## `mcboms.utils`

### `economics.py` — discounting and unit costs

PWF computation, USDOT BCA May 2025 default unit costs (crash costs, value of time, vehicle operating cost). Every value is documented with its source in the file.

[:material-download: Download `economics.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/utils/economics.py){ .md-button .file-button target="_blank" rel="noopener" }

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

[:material-download: Download `harwood_alternatives.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/src/mcboms/data/harwood_alternatives.py){ .md-button .file-button target="_blank" rel="noopener" }

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

`pytest tests/ -q` runs **109 tests** covering the worked example, Harwood reproduction, the safety module, the operations module, the CCM module, and the optional and network-level optimizer constraints.

### `test_harwood_validation.py` — Harwood reproduction tests

[:material-download: Download `test_harwood_validation.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/tests/test_harwood_validation.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: test_harwood_validation.py"
    ```python
    --8<-- "tests/test_harwood_validation.py"
    ```

### `test_safety.py` — safety module unit tests

[:material-download: Download `test_safety.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/tests/test_safety.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: test_safety.py"
    ```python
    --8<-- "tests/test_safety.py"
    ```

### `test_operations.py` — operations module unit tests

[:material-download: Download `test_operations.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/tests/test_operations.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: test_operations.py"
    ```python
    --8<-- "tests/test_operations.py"
    ```

### `test_ccm.py` — CCM module unit tests

[:material-download: Download `test_ccm.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/tests/test_ccm.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: test_ccm.py"
    ```python
    --8<-- "tests/test_ccm.py"
    ```

### `test_optimizer_constraints.py` — optional and network constraint tests

[:material-download: Download `test_optimizer_constraints.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/tests/test_optimizer_constraints.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: test_optimizer_constraints.py"
    ```python
    --8<-- "tests/test_optimizer_constraints.py"
    ```

---

## Top-level scripts

### `run_harwood_validation.py` — end-to-end Harwood validation

Runs both Level 2a (rigorous $50M check) and Level 2b (documented $10M divergence). Prints a complete validation summary.

[:material-download: Download `run_harwood_validation.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/run_harwood_validation.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: run_harwood_validation.py"
    ```python
    --8<-- "run_harwood_validation.py"
    ```

### `examples/banihashemi_intersections.py` — Banihashemi sub-problem reproduction

Builds the alternative table from raw IHSDM CPM inputs, runs the optimizer at the unconstrained budget, prints the structural results.

[:material-download: Download `banihashemi_intersections.py`](https://github.com/ttitamu/mcboms-optimization/raw/main/examples/banihashemi_intersections.py){ .md-button .file-button target="_blank" rel="noopener" }

??? abstract "View source: banihashemi_intersections.py"
    ```python
    --8<-- "examples/banihashemi_intersections.py"
    ```
