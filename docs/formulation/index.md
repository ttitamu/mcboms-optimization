# Mathematical Formulation

The MCBOMs framework is a Mixed-Integer Linear Programming formulation that integrates safety, operational, and corridor condition benefits within a single optimization problem. The contribution is not the use of MILP itself — that has been standard in transportation investment literature since RSRAP (Harwood et al., 2003) — but in the explicit segment-level structure of project alternatives, the unified treatment of multiple benefit categories, and the use of preprocessing-based alternative enumeration to keep the problem solver-agnostic and globally optimal.

Three structural elements distinguish this formulation:

**Segment-level alternative composition.** A project alternative is not a single uniform treatment applied to a whole site. It is a composition of segment-specific treatments, where different homogeneous segments within the same project may receive different treatments under the same alternative. This generalization is essential for the rural two-lane prototype, where treatments and crash propensities vary along a project's length.

**Multi-category benefit aggregation.** The total benefit is the sum of safety, operational, and corridor condition components, each computed from raw inputs through documented formulas with USDOT-recommended unit values. The framework's modular structure prevents double-counting between the operational and corridor condition modules — a real concern when energy productivity and travel time savings overlap.

**Preprocessing-based alternative enumeration.** Rather than embedding combinatorial logic inside the optimization (which complicates the constraints and risks slow solver behavior on large problems), MCBOMs enumerates feasible alternatives during preprocessing and presents each one as a single binary decision variable to the solver. This keeps the MILP linear and structurally simple while preserving the full combinatorial space of segment-level treatment choices.

## How this section is organized

The pages below document the formulation in detail. Pages are intended to be read in order:

<div class="grid cards" markdown>

-   **[Project-Level MILP](project-level.md)**

    The core formulation: decision variables, objective function, total benefit aggregation, and constraints (Eq 2.4–2.10). Includes optional dependency, cross-project exclusivity, and minimum-BCR constraints.

-   **[Network-Level Extensions](network-level.md)**

    Additional constraints that handle facility-type sub-budgets and regional caps and floors (Eq 2.14–2.16). Used when an agency must allocate budget across categories or geography.

-   **[Safety Benefit (Eq 2.18)](safety.md)**

    The HSM Crash Modification Factor methodology applied to compute per-alternative safety benefits, with severity disaggregation, multi-CMF combination, and present-worth conversion.

-   **[Operational Benefit (Eq 2.21)](operations.md)**

    Travel time savings and vehicle operating cost reductions, valued at USDOT-recommended rates. Documents the formulation; a parametric Python implementation is planned.

-   **[Corridor Condition Benefit (Eq 2.27)](ccm.md)**

    Energy, emissions, accessibility, and resilience improvements. Documents the multi-category structure and double-counting prevention.

-   **[MCBOMs Methodology (PDF)](methodology.md)**

    The complete formulation in a single 30-page PDF. Includes proofs, validation discussion, and full bibliography.

</div>

## Equation conventions

Equations are numbered consistently across this site and the methodology PDF:

- **Eq 2.1, 2.2, 2.3** — project six-tuple, total benefit aggregation, discount factor
- **Eq 2.4 – 2.7** — core MILP (objective, budget, mutual exclusivity, binary)
- **Eq 2.8 – 2.10** — optional constraints (dependency, cross-project exclusivity, minimum BCR)
- **Eq 2.14 – 2.16** — network-level constraints
- **Eq 2.18** — safety benefit
- **Eq 2.21** — operational benefit
- **Eq 2.27** — corridor condition benefit

Every equation in the solver-language models in `models/` carries the same equation number for cross-reference.
