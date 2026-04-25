# Banihashemi (2007) Intersection Sub-Problem

A 13-intersection sub-problem from Banihashemi's TRR 2019 paper. Each intersection has 2-5 alternatives covering left-turn-lane addition, traffic control changes, sight distance correction, and skew angle adjustment.

**Reference**: Banihashemi, M. (2007). Optimization of highway safety and operation by using crash prediction models with accident modification factors. *Transportation Research Record*, 2019(1), 111–117.

## What's parametric

The IHSDM Crash Prediction Module (Banihashemi Eq 15) is implemented end-to-end:

$$
N_{ij} = \exp\left(\alpha + \beta \ln(ADT_1) + \gamma \ln(ADT_2)\right) \cdot C_i \cdot \prod_k \mathrm{AMF}_k
$$

Where the AMFs cover:

- **Skew angle**: $\mathrm{AMF}_{\mathrm{skew}} = \exp(0.0054 \cdot |skew|)$ for stop-controlled, $1.0$ for signalized
- **Traffic control**: minor-stop / all-stop / signalized
- **Left-turn lane**: 0.67 (stop-controlled) or 0.77 (signalized) when added
- **Sight distance**: 1.42 with deficiency, 1.0 if corrected

Per-intersection ADTs, skew angles, traffic control type, LTL/ISD attributes, and delay times are all inputs declared in the model file.

## Cost components

The total societal cost is the sum of crash cost and delay cost over the 20-year project lifetime:

$$
C_{ij}^{\mathrm{total}} = N_{ij} \cdot C_{\mathrm{crash}} \cdot 20 + d_{ij} \cdot C_{\mathrm{delay}} \cdot 20
$$

Where:

- $C_{\mathrm{crash}}$ depends on intersection type (4-leg stop: $81,375; 4-leg signalized: $31,665)
- $C_{\mathrm{delay}} = \$12.50$ per vehicle-hour
- $d_{ij}$ is annual delay in vehicle-hours

The MCBOMs framework converts this to benefit-maximization: $B_{ij} = C_{i,0}^{\mathrm{total}} - C_{ij}^{\mathrm{total}}$ (avoided cost vs the do-nothing alternative).

## Expected structural results

The validation is **structural** rather than numeric. The optimizer should produce:

| Result | Expected |
|---|---|
| Most cost-effective improvement | Intersection 12 LTL (B/C ≈ 11.5) |
| Selected at every nonzero budget | Yes, Int 12:LTL always picked first |
| Signalization at Intersections 3 and 4 | Correctly **rejected** at every budget (delay cost increase dominates crash savings) |
| Rank ordering of LTL improvements | Matches Banihashemi Table 5 |

## Numeric divergence vs Banihashemi paper

Two reasons MCBOMs numerical results diverge from Banihashemi's published full-network solution:

1. **We validate the intersection sub-problem.** Banihashemi optimized the full network jointly (135 segments + 13 intersections). The interaction between segment and intersection allocations affects optimal selections.
2. **Banihashemi did not publish his exact AMF values.** We use standard IHSDM/Vogt-Bared values from FHWA-RD-99-207. Banihashemi cites IHSDM but specific values are not in his paper.

These are both honest scope choices, not implementation defects.

## Reproducing

### Solver-direct

```bash
cplex < models/lp/03_banihashemi_intersections.lp
# Or:
gurobi_cl models/lp/03_banihashemi_intersections.lp
```

Expected: `Objective value: 5177250.91` (net benefit at $12M unconstrained).

### AMPL

```bash
cd models/ampl
ampl 03_banihashemi_intersections.run
```

The output displays `Crashes_per_year` and `Total_Cost_20yr` parametrically computed for every alternative, then the optimal selection.

### GAMS

```bash
cd models/gams
gams 03_banihashemi_intersections.gms
```

### Python

```bash
python examples/banihashemi_intersections.py
```

This builds the alternative table from raw IHSDM CPM inputs, runs the optimizer at the unconstrained budget, and prints the structural results.
