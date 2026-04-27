# Multidisciplinary Cost-Benefit Optimization Models (MCBOMs)

A mixed-integer linear programming framework for transportation infrastructure investment decisions, integrating safety, operations, and corridor condition measures into a single optimization model. Developed at the Texas A&M Transportation Institute.

---

## Where to start

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Mathematical Formulation**

    ---

    The MCBOMs Methodology document is the formal specification of the framework, with the equations, variables, and constraints.

    [:octicons-arrow-right-24: Read the formulation](formulation/index.md)

-   :material-format-list-bulleted-square:{ .lg .middle } **Solver-Language Models**

    ---

    The `models/` folder contains the MILP in three formats: AMPL, GAMS, and LP. Use these directly in CPLEX, Gurobi, or any commercial MILP solver. No Python required.

    [:octicons-arrow-right-24: View the models](models/index.md)

-   :material-language-python:{ .lg .middle } **Python Implementation**

    ---

    Install the package, run the validation, integrate into a Python pipeline, or extend the framework with new benefit categories.

    [:octicons-arrow-right-24: Get started in Python](python/index.md)

-   :material-check-decagram:{ .lg .middle } **Validation**

    ---

    Three benchmarks: a worked example, Harwood (2003), and Banihashemi (2007). All three are reproducible from the repository.

    [:octicons-arrow-right-24: See validation results](validation/index.md)

</div>

---

## What MCBOMs does

Given a portfolio of candidate transportation projects (sites or intersections), each with multiple possible improvement alternatives, MCBOMs selects the combination that maximizes total societal benefit subject to a budget constraint. The benefits include:

- **Safety** — reductions in expected crash costs, computed via the Highway Safety Manual (HSM) Crash Modification Factor methodology
- **Operational** — reductions in travel time and vehicle operating costs, valued at USDOT-recommended rates
- **Corridor condition** — energy, environmental, accessibility, and resilience improvements

The framework builds on Harwood, Rabbani, and Richard (2003) and Banihashemi (2007), and is parameterized with USDOT BCA Guidance values from May 2025.

---

## Three forms of the same mathematics

MCBOMs is mathematically a single optimization model. That single model is expressed in three forms in this repository, each suited to a different audience:

| Form | Where it lives | Best for |
|---|---|---|
| **Formal mathematical specification** | [MCBOMs Methodology (PDF)](formulation/methodology.md) | Reading the math; auditing the formulation; citing in reports |
| **Solver-language models** (AMPL, GAMS, LP) | [`models/`](models/index.md) | Running the validation in CPLEX, Gurobi, or any commercial MILP solver |
| **Python implementation** | [`src/mcboms/`](python/index.md) | Programmatic use, custom data integration, building extensions |

These three forms produce numerically identical results. A reviewer who works in classical optimization software does not need to install or run Python.

---

## Validation summary

| Instance | Optimal objective | Status |
|---|---|---|
| Worked example | $1,493,914 | Matches Section 2.3.7 |
| Harwood $50M | $6,159,512 | Matches Harwood Table 4 within $5 |
| Harwood $10M | $4,931,520 | +5.5% above Harwood (no PNR; documented) |
| Banihashemi sub-problem | $5,177,251 | Structural validation passes |

Full details on the [Validation](validation/index.md) page.
