# Network-Level Extensions

Beyond the core project-level constraints, MCBOMs supports network-level constraints that model how a transportation agency might allocate budget across facility types or geographic regions.

## Facility-type sub-budget (Eq 2.14)

$$
\sum_{i \in I_m} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \leq B_m \quad \forall m \in M
$$

Where:

- $M$ is the set of facility types (e.g., rural two-lane, urban four-lane, freeway)
- $I_m$ is the subset of projects of facility type $m$
- $B_m$ is the maximum spend allowed on facility type $m$

This constraint lets agencies cap spending per facility category. Useful when a program has multiple funding streams with separate ceilings (e.g., HSIP funds for safety improvements, RRR funds for pavement work).

## Regional cap (Eq 2.15)

$$
\sum_{i \in I_r} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \leq B_r^{\mathrm{cap}} \quad \forall r \in R
$$

Where:

- $R$ is the set of regions
- $I_r$ is the subset of projects in region $r$
- $B_r^{\mathrm{cap}}$ is the maximum spend allowed in region $r$

## Regional minimum-investment floor (Eq 2.16)

$$
\sum_{i \in I_r} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \geq \beta_r \cdot B^{\mathrm{total}} \quad \forall r \in R
$$

Where $\beta_r$ is the minimum fraction of total budget that must be spent in region $r$. This constraint addresses regional balance considerations, ensuring some level of investment reaches each region rather than concentrating all spending in a few high-benefit areas.

## Solver-language implementations

The optional and network-level constraints are activated by populating the corresponding sets in the data file. When the sets are empty (e.g., no facility types defined), the constraints are vacuously satisfied and the model reduces to the project-level form.

See:

- AMPL: `models/ampl/00_optimization.mod` (all constraints declared at top of file)
- GAMS: `models/gams/00_optimization.gms`
- LP: not represented symbolically (LP files are flat numeric forms)
