# Banihashemi (2007) Methodology Notes

This page documents the methodology of Banihashemi (2007) in detail, as a reference for the MCBOMs validation against the intersection sub-problem of his published case study.

## Citation

Banihashemi, M. (2007). "Optimization of highway safety and operation by using crash prediction models with accident modification factors." *Transportation Research Record* 2019, pp. 108–118. DOI: 10.3141/2019-14.

## Optimization formulation

Banihashemi formulates the problem as **cost minimization** rather than benefit maximization. The objective is to minimize the total of crash and delay costs across the network, subject to a budget constraint on improvement spending.

#### Objective function (Equation 7)

$$
\min \quad \sum_{h=1}^{n_{\mathrm{hwy}}} \sum_{i=1}^{n_{S_h}} \left[ C_{sc} \cdot f_s(\mathrm{ADT}_{h,i}, L_{h,i}) \cdot \prod_{S=1}^{a} \mathrm{AMF}^S_{h,i,(j,k,\ldots)} X_{h,i,(j,k,\ldots)} \right] + \sum_{i=1}^{n_{\mathrm{int}}} \left[ C_{i,ic} \cdot f_i(\mathrm{ADT}_{i,b}) \cdot \prod_{S=1}^{c} \mathrm{AMF}^S_{i,(s,t,\ldots)} Y_{i,(s,t,\ldots)} \right] + C_D \cdot \left( \sum D_{h,i} \cdot X_{h,i} + \sum D_i \cdot Y_i \right)
$$

The first sum is segment crash cost, the second is intersection crash cost, the third is delay cost.

#### Constraints

**Segment covering (Equation 8)** — exactly one improvement combination per homogenous highway segment:

$$
\sum_{(j,k,\ldots)} X_{h,i,(j,k,\ldots)} = 1 \quad \forall h, i
$$

**Intersection covering (Equation 9)** — exactly one improvement combination per intersection:

$$
\sum_{(s,t,\ldots)} Y_{i,(s,t,\ldots)} = 1 \quad \forall i
$$

**Budget (Equation 10)**:

$$
\sum_{h,i} \sum_{(j,k,\ldots)} C_{h,i,(j,k,\ldots)} \cdot X_{h,i,(j,k,\ldots)} + \sum_i \sum_{(s,t,\ldots)} C_{i,(s,t,\ldots)} \cdot Y_{i,(s,t,\ldots)} \leq B^{\mathrm{total}}
$$

**Improvement length limitation (Equation 11)** — the Minimum Improvement Length (MIL) constraint, which Banihashemi introduces as a structural innovation. It enforces that certain improvements (e.g., lane widening) must be applied continuously over a minimum length rather than to single segments. This enables the model to autogenerate feasible improvement combinations rather than requiring the analyst to enumerate them.

**Integrality (Equation 12)** — all decision variables are binary integers.

## Crash and delay cost computation

#### Unit crash costs (FHWA 2002)

Banihashemi uses the FHWA 2002 estimates:

| Severity | Cost per crash |
|---|---|
| Fatal | $3,000,000 |
| Incapacitating injury | $208,000 |
| Serious injury | $42,000 |
| Minor injury | $22,000 |
| Property damage only | $2,300 |

#### Average crash costs by location type

Combining the unit costs with IHSDM default crash severity distributions:

| Location type | Average crash cost |
|---|---|
| Highway segments | $59,562 |
| Three-leg stop-controlled intersections | $55,239 |
| Four-leg stop-controlled intersections | $81,375 |
| Four-leg signalized intersections | $31,665 |

#### Delay cost

A unit cost of $12.50 per vehicle-hour is used for in-vehicle travel time and delay. This is computed as $10/hour value of time multiplied by a vehicle occupancy of 1.25.

## IHSDM Crash Prediction Module

The optimization model is presented in conjunction with the Crash Prediction Module of the Interactive Highway Safety Design Model (IHSDM), documented in FHWA-RD-99-207.

#### Highway segment model (Equation 13)

$$
N_S = \sum_h \sum_i 365 \cdot 10^{-6} \cdot e^{-0.4865} \cdot \mathrm{ADT}_{h,i} \cdot L_{h,i} \cdot C_r \cdot \prod_{S=1}^{9} \mathrm{AMF}^S_{h,i}
$$

where $C_r$ is the state calibration factor (2.376 for the northeastern U.S. state Banihashemi uses).

#### Intersection model (Equation 15)

$$
N_I = \sum_i e^{(\alpha + \beta \ln \mathrm{ADT}_1 + \gamma \ln \mathrm{ADT}_2)} \cdot C_i \cdot \prod_{S=1}^{5} \mathrm{AMF}^S_i
$$

with intersection-type-specific coefficients:

| Intersection type | $\alpha$ | $\beta$ | $\gamma$ | $C_i$ |
|---|---|---|---|---|
| Three-leg stop-control | $-10.9$ | $0.79$ | $0.49$ | $0.79$ |
| Four-leg stop-control | $-9.34$ | $0.60$ | $0.61$ | $0.98$ |
| Four-leg signalized | $-5.73$ | $0.60$ | $0.20$ | $0.94$ |

#### AMFs in the IHSDM CPM

Nine highway segment AMFs (lane width, shoulder width and type, horizontal curvature, superelevation deficiency, grades, driveway density, passing lanes, two-way left-turn lanes, roadside hazard rating) and five intersection AMFs (skew angle, traffic control, left-turn lane, right-turn lane, intersection sight distance limitation).

## Test case

#### Network

- Three rural highways, 4 km to 10 km long
- 13 intersections (mix of stop-controlled and signalized four-leg)
- 135 homogenous segments after matching across improvement alternatives
- 3,385 binary decision variables
- 535 constraints

#### Budget scenarios

Nine budget scenarios were solved with CPLEX, ranging from a $1M cap to no limit (with $15M coded as the no-limit value, of which the optimal solution actually used $12,201,510). Scenarios at $10M, $8M, $6M, $5M, $4M, $3M, and $2M were also tested.

#### Published results (Table 5)

| Budget limit | Improvement cost spent | Total crash + delay cost |
|---|---|---|
| No limit ($15M cap) | $12,201,510 | $140,805,988 |
| $10M | $9,992,641 | $141,348,942 |
| $8M | $7,988,325 | $142,594,267 |
| $6M | $5,982,823 | $144,834,436 |
| $5M | $4,998,954 | $146,805,888 |
| $4M | $3,998,954 | $149,467,886 |
| $3M | $2,999,227 | $152,363,771 |
| $2M | $1,999,418 | $155,763,241 |
| $1M | $999,451 | $160,478,348 |
| $0 (no improvement) | $0 | $173,874,383 |

The maximum achievable saving is $33M (from $173.9M down to $140.8M) at the no-limit scenario. The B/C ratio for total improvements declines from about 13 at $1M down to about 2.5 at $12M.

## Strengths of the formulation

The paper identifies three structural strengths:

- **MIL concept** — autogeneration of feasible improvement combinations rather than manual enumeration. This is the key methodological contribution.
- **Delay cost in the objective** — prevents selection of safety improvements whose delay penalties exceed their crash savings. The paper notes that no traffic-control change improvement is chosen in any scenario for this reason.
- **No preprocessing to eliminate cost-ineffective options** — the model handles this automatically through the optimization.

## Cost minimization vs benefit maximization

Banihashemi's objective is cost minimization. MCBOMs is formulated as benefit maximization, where the benefit of an alternative is the avoided cost relative to the do-nothing alternative:

$$
B_{ij} = C_{i,0}^{\mathrm{total}} - C_{ij}^{\mathrm{total}}
$$

The two formulations are mathematically equivalent for the optimal selection. MCBOMs adopts the benefit-maximization framing for consistency with Harwood (2003) and with the USDOT BCA convention; the underlying solution is unchanged.

## MCBOMs validation against the intersection sub-problem

The MCBOMs validation extracts the 13-intersection sub-problem from Banihashemi's network and runs it through the MCBOMs optimizer. The intersection sub-problem is well-suited to validation because intersection improvements have explicit per-intersection costs and AMFs (whereas segment improvements depend on continuous-length cost calculations and the MIL machinery, which is a separate validation milestone).

| What was tested | Result |
|---|---|
| Structural reproduction | Passes |
| Rank ordering of left-turn-lane improvements | Consistent with the published case |

The full network reproduction (135 segments × 3,385 variables) is on the implementation roadmap but requires the segment geometry data that the paper does not publish.

## Limitation for full reproduction

The paper publishes intersection improvement costs (e.g., "Adding left-turn lane: $300,000 for Intersections 1 and 2; $400,000 for Intersections 5 and 6; $600,000 for Intersections 9, 10, and 13; and $100,000 for Intersection 12") and intersection delay times for each improvement combination. These are sufficient to reproduce the intersection sub-problem.

The paper does not publish the full per-segment AMF values used in the case study, the homogenous segment geometry, or the segment-level cost calculations. Reproducing the full network case from raw inputs would require those data, which are not in the paper. The MCBOMs intersection validation uses Banihashemi's published per-intersection values directly.

## Formulation summary

```python
# Objective: minimize total crash + delay cost
# In MCBOMs benefit-maximization form: maximize avoided cost vs do-nothing.

# Per-intersection benefit (avoided cost vs do-nothing):
# B_i_alt = (N_i_donothing * C_crash + D_i_donothing * C_delay) -
#           (N_i_alt * C_crash + D_i_alt * C_delay)
# where N is expected crashes (IHSDM CPM Eq 15) and D is delay (HCM 2000).

objective = sum(
    benefit_intersection[i, alt] * y[i, alt]
    for i in intersections
    for alt in alternatives[i]
)

# Intersection covering: exactly one alternative per intersection
for i in intersections:
    sum(y[i, alt] for alt in alternatives[i]) == 1

# Budget: total improvement cost <= budget
sum(
    cost_intersection[i, alt] * y[i, alt]
    for i in intersections
    for alt in alternatives[i]
) <= budget
```
