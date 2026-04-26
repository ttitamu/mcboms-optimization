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

    The core formulation: decision variables, objective function, total benefit aggregation, and the always-active constraints (budget, mutual exclusivity, binary). Optional constraints — dependency, cross-project exclusivity, minimum benefit-cost ratio — are documented here.

-   **[Network-Level Extensions](network-level.md)**

    Additional constraints for facility-type sub-budgets, regional spending caps, and regional minimum-investment floors. Used when an agency must allocate a single budget across categories or geography.

-   **[Safety Benefit](safety.md)**

    The HSM Crash Modification Factor methodology applied to compute per-alternative safety benefits, with severity disaggregation, multi-CMF combination, and present-worth conversion.

-   **[Operational Benefit](operations.md)**

    Travel time savings and vehicle operating cost reductions, summed across vehicle classes and converted to present value at USDOT-recommended unit rates.

-   **[Corridor Condition Benefit](ccm.md)**

    Energy, emissions, accessibility, resilience, and pavement improvements. Per-category monetization with explicit double-counting prevention against the operational benefit.

-   **[MCBOMs Methodology (PDF)](methodology.md)**

    The complete formulation in a single standalone document. Includes proofs, full validation discussion, and bibliography.

</div>

## Cross-referencing the methodology PDF

Each equation in the methodology PDF carries a numeric label (e.g., the safety benefit equation appears as Eq 2.18). The same equations are rendered with the same labels on the formulation pages of this site, and on the AMPL, GAMS, and LP files in `models/`. This consistency lets readers move between the formal document, the rendered web pages, and the solver-readable code without losing track of which equation is which.
