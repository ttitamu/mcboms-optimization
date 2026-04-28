# Multidisciplinary Cost-Benefit Optimization Models (MCBOMs)

A mixed-integer linear programming framework for transportation infrastructure investment decisions, integrating safety, operations, and corridor condition measures into a single optimization model. Builds directly on Harwood, Rabbani, and Richard (2003) and Banihashemi (2007), parameterized with USDOT Benefit-Cost Analysis Guidance values. Developed at the Texas A&M Transportation Institute under FHWA Contract HRSO20240009PR. [Read the full overview →](overview.md)

---

## Where to start

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Mathematical Formulation**

    ---

    The MCBOMs Methodology document is the formal specification of the framework, with the equations, variables, and constraints.

    [:octicons-arrow-right-24: Read the formulation](formulation/index.md)

-   :material-check-decagram:{ .lg .middle } **Validation**

    ---

    Three benchmarks: a worked example, Harwood (2003), and Banihashemi (2007). All three are reproducible from the repository.

    [:octicons-arrow-right-24: See validation results](validation/index.md)

-   :material-format-list-bulleted-square:{ .lg .middle } **Solver Models**

    ---

    AMPL, GAMS, and LP files for commercial MILP solvers, plus Microsoft Excel workbooks.

    [:octicons-arrow-right-24: View the models](models/index.md)

-   :material-language-python:{ .lg .middle } **Python Implementation**

    ---

    Install the package, run the validation, integrate into a Python pipeline, or extend the framework with new benefit categories.

    [:octicons-arrow-right-24: Get started in Python](python/index.md)

</div>
