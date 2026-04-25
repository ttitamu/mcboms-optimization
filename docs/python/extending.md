# Extending the Framework

## Adding a new benefit category

Suppose you want to add a "construction emissions" benefit category:

1. **Math** — define the equation in Chapter 2 (LaTeX edit). Number it 2.x to fit the existing scheme.
2. **AMPL** — add the parametric definition to a new instance `.mod` file in `models/ampl/`.
3. **GAMS** — mirror the implementation in `.gms`.
4. **Python** — create `src/mcboms/benefits/construction_emissions.py` following the pattern of `safety.py`. Implement a function `compute_construction_emissions_benefit()` that takes inputs and returns a present-value dollar amount.
5. **Tests** — add unit tests in `tests/test_construction_emissions.py`.
6. **Docs** — update this site (overview, formulation page) and the README.

The convention is: **lock the math first, then propagate to all three forms** (AMPL, GAMS, Python). Numerical results from any form must match.

## Adding a new validation case study

1. **Data** — create the alternative DataFrame (one row per (project, alternative) pair, with columns matching what `Optimizer` expects).
2. **Solver instances** — generate the AMPL/GAMS/LP files for the new case (use the existing Banihashemi script as a template).
3. **Python script** — create `examples/your_case_study.py`.
4. **Tests** — add validation tests in `tests/test_your_case_study.py`.
5. **Document** — add a section to Chapter 2 and update the [Validation](../validation/index.md) section of this site.

## Modifying the optimizer

If you need to add a new constraint type:

1. **Math** — edit Chapter 2 Section 2.2.
2. **AMPL** — edit `models/ampl/00_optimization.mod` to add the new constraint.
3. **GAMS** — mirror in `models/gams/00_optimization.gms`.
4. **Python** — edit `src/mcboms/core/optimizer.py` to add the constraint inside `_build_model()`.
5. **Tests** — add tests covering the new constraint behavior.

## Code style

- Plain, professional code comments. Reference Chapter 2 equation numbers (e.g., `# Eq 2.18`).
- Type hints where helpful but not required everywhere.
- `pytest` for tests, `pandas` for data, `pulp` and `gurobipy` for optimization.
- Match the existing module structure: classes for stateful objects, free functions for stateless calculations.
