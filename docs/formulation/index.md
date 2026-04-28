# Mathematical Formulation

The MCBOMs framework is a Mixed-Integer Linear Programming formulation that integrates safety, operational, and corridor condition benefits within a single optimization problem. The formulation builds on Harwood, Rabbani, and Richard (2003) and Banihashemi (2007), with three structural elements that the rest of this section documents.

**Segment-level alternative composition.** A project alternative is a composition of segment-specific treatments rather than a single uniform treatment applied to a whole site. Different homogeneous segments within the same project may receive different treatments under the same alternative. This is essential for the rural two-lane prototype, where treatments and crash propensities vary along a project's length.

**Multi-category benefit aggregation.** The total benefit is the sum of safety, operational, and corridor condition components, each computed from documented formulas with USDOT-recommended unit values. The framework's modular structure addresses double-counting between the operational and corridor condition modules, a real concern when energy productivity and travel time savings overlap.

**Preprocessing-based alternative enumeration.** Following Harwood (2003), MCBOMs enumerates feasible alternatives during preprocessing and presents each one as a single binary decision variable to the solver, rather than embedding combinatorial logic inside the optimization. This keeps the MILP linear and structurally simple while preserving the full combinatorial space of segment-level treatment choices.

## Section pages

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

    Energy, emissions, accessibility, resilience, and pavement improvements. Per-category monetization with double-counting protocols against the operational benefit.

-   **[MCBOMs Methodology (PDF)](methodology.md)**

    The complete formulation in a single standalone document, with full validation discussion.

</div>

## Cross-referencing the methodology PDF

The methodology PDF is the formal specification, with numbered equations and full validation discussion. The pages on this site present the same formulation in browser-readable form for reference.
