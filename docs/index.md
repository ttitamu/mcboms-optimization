# MCBOMs Documentation

**Multidisciplinary Cost-Benefit Optimization Models** — a Mixed-Integer Linear Programming framework for transportation infrastructure investment decisions.

Developed under FHWA Contract HRSO20240009PR by the Texas A&M Transportation Institute.

---

## Where to start

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **I want to read the math**

    ---

    Start with the mathematical formulation. the MCBOMs Methodology document is the formal specification.

    [:octicons-arrow-right-24: Mathematical Formulation](formulation/index.md)

-   :material-format-list-bulleted-square:{ .lg .middle } **I want to run the model in CPLEX/Gurobi/GAMS**

    ---

    The `models/` folder contains the MILP in three solver-language forms: AMPL, GAMS, and LP. No Python required.

    [:octicons-arrow-right-24: Mathematical Models](models/index.md)

-   :material-language-python:{ .lg .middle } **I want to use the Python implementation**

    ---

    Install the package, run validation, integrate into your pipeline, or extend with new benefit categories.

    [:octicons-arrow-right-24: Python Implementation](python/index.md)

-   :material-check-decagram:{ .lg .middle } **I want to verify the framework**

    ---

    Three benchmark validations: a worked example, Harwood (2003), and Banihashemi (2007). All reproducible from the repository.

    [:octicons-arrow-right-24: Validation](validation/index.md)

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

These three forms produce the same numerical results to the cent. A reviewer who works in classical optimization software does not need to install or run Python.

---

## Validation summary

| Instance | Optimal objective | Status |
|---|---|---|
| Worked example | $1,493,914 | Matches Section 2.3.7 |
| Harwood $50M | $6,159,512 | Matches Harwood Table 4 within $5 |
| Harwood $10M | $4,931,520 | +5.5% above Harwood (no PNR; documented) |
| Banihashemi sub-problem | $5,177,251 | Structural validation passes |

Full details on the [Validation](validation/index.md) page.
