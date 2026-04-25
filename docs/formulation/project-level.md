# Project-Level MILP

The MCBOMs framework is fundamentally a binary optimization problem: for each candidate project, decide which improvement alternative (if any) to implement, subject to a budget constraint.

## Decision variable

$$
x_{ij} \in \{0, 1\} \quad \text{for each project } i \text{ and alternative } j
$$

$x_{ij} = 1$ if alternative $j$ is selected for project $i$, $0$ otherwise.

## Objective function (Eq 2.4)

$$
\max \quad Z = \sum_{i=1}^{I} \sum_{j \in A_i} \left( B_{ij} - C_{ij}^{\mathrm{disc}} \right) x_{ij}
$$

Where:

- $B_{ij}$ is the **total present-value benefit** of alternative $j$ at project $i$
- $C_{ij}^{\mathrm{disc}}$ is the **discretionary cost component** of alternative $j$ at project $i$
- $A_i$ is the set of alternatives available for project $i$ (always includes a do-nothing alternative)

### Discretionary versus committed cost

For most projects, discretionary cost equals total cost: $C_{ij}^{\mathrm{disc}} = C_{ij}$.

For Harwood-style RRR projects where pavement resurfacing is committed (every site is resurfaced regardless of the optimization outcome), only the safety improvement cost is discretionary:

$$
C_{ij} = C_{ij}^{\mathrm{comm}} + C_{ij}^{\mathrm{disc}}
$$

The total cost is used in the budget constraint. The discretionary cost is used in the objective.

## Total benefit (Eq 2.2)

The total benefit aggregates safety, operational, and corridor condition benefits over the analysis horizon:

$$
B_{ij} = \sum_{t=1}^{T} \left( B_{ijt}^{\mathrm{safety}} + B_{ijt}^{\mathrm{operations}} + B_{ijt}^{\mathrm{corridor}} \right) \cdot DF_t
$$

Where $DF_t = 1 / (1+r)^t$ is the year-$t$ discount factor with discount rate $r$.

## Core constraints

### Total budget (Eq 2.5)

$$
\sum_{i=1}^{I} \sum_{j \in A_i} C_{ij} \cdot x_{ij} \leq B^{\mathrm{total}}
$$

The full cost (including any committed component) is what counts against the budget.

### Mutual exclusivity (Eq 2.6)

$$
\sum_{j \in A_i} x_{ij} \leq 1 \quad \forall i
$$

At most one alternative can be selected per project. The inequality (rather than equality) allows for the "do nothing" option, encoded as $x_{ij} = 0$ for all $j \in A_i$.

### Binary (Eq 2.7)

$$
x_{ij} \in \{0, 1\} \quad \forall i, j
$$

Decision variables are binary integers.

## Optional constraints

These constraints are activated when the relevant data is provided.

### Dependency (Eq 2.8)

$$
x_{ij} \leq x_{i'j'} \quad \text{for each } (i,j,i',j') \in D
$$

Selecting alternative $(i,j)$ requires selecting alternative $(i',j')$. Useful for modeling phased improvements where one project must be completed before another.

### Cross-project exclusivity (Eq 2.9)

$$
x_{ij} + x_{i'j'} \leq 1 \quad \text{for each } (i,j,i',j') \in K
$$

Alternatives $(i,j)$ and $(i',j')$ cannot both be selected. Useful for modeling alternatives that physically conflict or compete for the same resources.

### Minimum benefit-cost ratio (Eq 2.10)

$$
\sum_{j \in A_i} B_{ij} x_{ij} \geq \theta \cdot \sum_{j \in A_i} C_{ij} x_{ij} \quad \forall i
$$

For a selected alternative, the benefit-to-cost ratio must meet a minimum threshold $\theta$. When $\theta = 1$, this enforces benefit ≥ cost on each selection.

## Solver-language implementations

This formulation is implemented in:

- [AMPL](../models/ampl.md) — `models/ampl/00_optimization.mod`
- [GAMS](../models/gams.md) — `models/gams/00_optimization.gms`
- [LP](../models/lp.md) — `models/lp/00_optimization.lp` (with illustrative example since LP is numeric-only)
- [Python](../python/architecture.md) — `src/mcboms/core/optimizer.py`

All four produce identical numerical results.
