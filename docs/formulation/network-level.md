# Network-Level Extensions

The project-level MILP treats every candidate project as competing equally for one shared budget. In practice, transportation agencies often have additional constraints that the project-level model cannot express: separate funding streams for different facility categories, caps on per-region spending, and minimum-investment floors that protect underserved areas. The network-level extensions add these constraints to the formulation while preserving the project-level structure intact.

These constraints are optional: when their corresponding sets are empty (e.g., no facility types defined), the constraints are vacuously satisfied and the model reduces to the pure project-level form.

## Facility-type sub-budget

$$
\sum_{i \in I_m} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \leq B_m \quad \forall m \in M
$$

Where:

- $M$ — set of facility types (e.g., rural two-lane, urban four-lane, freeway, intersection)
- $I_m$ — subset of projects of facility type $m$
- $B_m$ — sub-budget allocated to facility type $m$

This constraint reflects how transportation agencies typically receive funding: HSIP funds may be earmarked for safety improvements, RRR funds for pavement, and so on. The sub-budgets sum to no more than the total program budget, but each can be tighter if the agency wants to enforce a category-specific spending cap. When all facility types share a single pool, this constraint is omitted.

## Regional cap

$$
\sum_{i \in I_r} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \leq B_r^{\mathrm{cap}} \quad \forall r \in R
$$

Where:

- $R$ — set of regions
- $I_r$ — subset of projects in region $r$
- $B_r^{\mathrm{cap}}$ — maximum spend allowed in region $r$

Useful when an agency wants to prevent one high-benefit region from absorbing the entire program budget. Without this constraint, the optimizer concentrates spending where benefit-cost is highest, which may produce a politically untenable allocation.

## Regional minimum-investment floor

$$
\sum_{i \in I_r} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \geq \beta_r \cdot B^{\mathrm{total}} \quad \forall r \in R
$$

Where $\beta_r$ is the minimum fraction of total budget that must be spent in region $r$. This addresses regional balance — ensuring that low-benefit-cost regions still receive infrastructure investment, even when a strict net-benefit-maximizing allocation would skip them.

## Interaction with the project-level constraints

The network-level constraints add to (do not replace) the project-level constraints. A solution that satisfies the project-level model must additionally satisfy any active facility-type or regional constraints. The objective is unchanged.

When facility-type and regional constraints are both active, they may interact restrictively: a region might receive its required minimum, but only by spending in a facility type that has hit its sub-budget cap. In such cases, the optimizer either finds the best available allocation given the constraints or, if the problem is infeasible, reports that no allocation can satisfy all constraints simultaneously. Diagnosing infeasibility usually points to either a too-tight sub-budget or a too-aggressive regional floor.

## Implementation

The network-level constraints are declared in the abstract optimization model file and activated by populating the corresponding sets in the data file:

- AMPL: `models/ampl/00_optimization.mod` declares all 10 constraints
- GAMS: `models/gams/00_optimization.gms` mirrors the same structure
- LP: not represented symbolically (LP is a flat numeric form)

The current validation case studies (Harwood, Banihashemi worked example, Banihashemi intersection sub-problem) do not exercise these constraints. They are part of the formulation framework and will be tested when an agency provides a use case requiring them.
