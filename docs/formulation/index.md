# Mathematical Formulation

The full formulation is in [Chapter 2 PDF](chapter2.md). The pages in this section give you a navigable web version with rendered equations.

## Sections

<div class="grid cards" markdown>

-   **[Project-Level MILP](project-level.md)**

    Decision variable, objective function, total benefit aggregation, and the core constraints (Eq 2.4 through 2.10).

-   **[Network-Level Extensions](network-level.md)**

    Facility-type sub-budgets and regional caps/floors (Eq 2.14 through 2.16).

-   **[Safety Benefit (Eq 2.18)](safety.md)**

    The HSM-based crash modification factor methodology applied to compute safety benefits per alternative.

-   **[Operational Benefit (Eq 2.21)](operations.md)**

    Travel time and vehicle operating cost savings, valued at USDOT-recommended rates.

-   **[Corridor Condition Benefit (Eq 2.27)](ccm.md)**

    Multi-category corridor condition measures: energy, emissions, accessibility, resilience.

-   **[Chapter 2 (Full PDF)](chapter2.md)**

    Direct link to the full 30-page LaTeX-rendered mathematical specification.

</div>

## Equation conventions

Throughout this documentation, equations are numbered to match Chapter 2 of the Task 4 Report:

- **Eq 2.1, 2.2, 2.3** — Project six-tuple definition, total benefit decomposition, discount factor formula
- **Eq 2.4 – 2.7** — Core MILP (objective, budget, mutual exclusivity, binary)
- **Eq 2.8 – 2.10** — Optional constraints (dependency, cross-project exclusivity, minimum BCR)
- **Eq 2.14 – 2.16** — Network-level constraints
- **Eq 2.18** — Safety benefit (HSM-based)
- **Eq 2.21** — Operational benefit
- **Eq 2.27** — Corridor condition benefit

Every equation in the solver-language models in `models/` is labeled with its Chapter 2 number for cross-reference.
