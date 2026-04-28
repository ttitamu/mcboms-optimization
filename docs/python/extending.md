# Extending the Framework

## Adding a new benefit category

To add a new benefit category (e.g., construction emissions):

1. Define the equation in the MCBOMs Methodology document. Number it 2.x to fit the existing scheme.
2. Create `src/mcboms/benefits/construction_emissions.py` following the pattern of `safety.py`. Implement a function `compute_construction_emissions_benefit()` that takes inputs and returns a present-value dollar amount.
3. Add unit tests in `tests/test_construction_emissions.py`.
4. Update the overview page, the relevant formulation page, and the README.

## Adding a new validation case study

1. Create the alternative DataFrame (one row per project-alternative pair, with columns matching what `Optimizer` expects).
2. Create `examples/your_case_study.py` following the pattern of `examples/banihashemi_intersections.py`.
3. Add validation tests in `tests/test_your_case_study.py`.
4. Add a section to the MCBOMs Methodology document and update the [Validation](../validation/index.md) section of this site.

## Modifying the optimizer

To add a new constraint type:

1. Define the constraint in MCBOMs Methodology Section 2.2.
2. Edit `src/mcboms/core/optimizer.py` to add the constraint inside `_build_model()`.
3. Add tests covering the new constraint behavior.

## Code conventions

The framework uses `pytest` for tests, `pandas` for data structures, and `pulp` and `gurobipy` for optimization. Type hints are used where they add clarity. The package layout is documented in [Architecture](architecture.md).
