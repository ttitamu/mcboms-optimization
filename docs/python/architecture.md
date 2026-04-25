# Architecture

The Python code is organized as a standard Python package under `src/mcboms/`.

## `mcboms.core`

**`src/mcboms/core/optimizer.py`** — the main `Optimizer` class. Construct with sites, alternatives, budget, discount rate, and analysis horizon. Call `.solve()` to run the MILP.

The optimizer uses Gurobi if available, falling back to CBC. Decision variables are binary, the objective is linear, constraints are linear — a standard MILP that any solver handles.

**`src/mcboms/core/alternatives.py`** — helpers for enumerating alternatives.

## `mcboms.benefits`

This is where the benefit equations live.

| Module | Status | Equation |
|---|---|---|
| `safety.py` | ✓ Implemented | Eq 2.18 |
| `operations.py` | In development | Eq 2.21 |
| `ccm.py` | In development | Eq 2.27 |

`safety.py` exposes the `compute_safety_benefit()` function that takes per-severity inputs and returns the present-value benefit. See [Safety Benefit](../formulation/safety.md).

## `mcboms.io`

**`readers.py`** — reads CSV input files (sites, alternatives) and converts them to pandas DataFrames in the format the optimizer expects.

**`writers.py`** — writes results to CSV.

**`colleague_workbook.py`** — reads the Task 4 BCA spreadsheet (an Excel workbook from a TTI colleague) and converts it to the optimizer's input format.

## `mcboms.utils`

**`economics.py`** — discount factor formulas, Present Worth Factor computation, and bundled USDOT BCA May 2025 default unit costs (crash costs, value of time, vehicle operating cost). All values are documented with their source in the file.

## `mcboms.data`

**`harwood_alternatives.py`** — bundled Harwood (2003) case study data. Returns a DataFrame of 21 alternatives across 10 sites with all the published cost and benefit components. This is what the validation runs against.

## Tests

| File | Coverage |
|---|---|
| `tests/test_harwood_validation.py` | 16 tests — Harwood reproduction at $50M (Level 2a rigorous) and $10M (Level 2b documented divergence) |
| `tests/test_safety.py` | 16 tests — severity disaggregation, CMF combination, worked example reproduction |

Run all tests with `pytest tests/ -q`.
