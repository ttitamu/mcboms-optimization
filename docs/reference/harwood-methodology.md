# Harwood (2003) Methodology Notes

This page documents the methodology of Harwood, Rabbani, and Richard (2003) in detail, as a reference for the MCBOMs validation against their published case studies.

## Citation

Harwood, D.W., Rabbani, E.R.K., and Richard, K.R. (2003). "[Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects](https://doi.org/10.3141/1840-17){target="_blank" rel="noopener"}." *Transportation Research Record* 1840, pp. 148–157.

## Optimization formulation

#### Objective function (Equation 4)

$$
\max \quad TB = \sum_j \sum_k NB_{jk} \cdot X_{jk}
$$

Where:

- $TB$ — total benefits from all selected improvements
- $j$ — site index ($1$ to $y$ sites)
- $k$ — alternative index at site $j$ ($0$ to $z$ alternatives)
- $X_{jk}$ — binary decision variable ($1$ if selected, $0$ otherwise)

#### Net benefit equation (Equation 3)

$$
NB_{jk} = PSB_{jk} + PTOB_{jk} + PNR_{jk} - PRP_{jk} - CC_{jk}
$$

Where:

- $PSB_{jk}$ — present value of safety benefits (from AMFs)
- $PTOB_{jk}$ — present value of traffic operations benefits (travel time)
- $PNR_{jk}$ — penalty for not resurfacing (only for the do-nothing alternative)
- $PRP_{jk}$ — penalty for resurfacing without safety improvements
- $CC_{jk}$ — construction cost for alternative $k$ at site $j$

#### Constraints

Mutual exclusivity (Equations 5–7) — exactly one alternative per site:

$$
\sum_k X_{jk} = 1 \quad \forall j
$$

Budget constraint (Equation 8):

$$
\sum_j \sum_k CC_{jk} \cdot X_{jk} \leq B
$$

## Safety benefit calculation

Present value of safety benefits (Equation 2):

$$
PSB_{jk} = \sum_m \sum_s N_{jms} \cdot (1 - AMF_{mk}) \cdot RF_{ms} \cdot AC_s \cdot (P/A, i, n)
$$

Where:

- $m$ — location type index ($m=1$: non-intersection, $m=2$: intersections)
- $s$ — severity level index ($s=1$: fatal and injury, $s=2$: PDO)
- $N_{jms}$ — expected annual accident frequency for location type $m$, severity $s$, at site $j$
- $AMF_{mk}$ — Accident Modification Factor for alternative $k$ at location type $m$
- $RF_{ms}$ — proportion of total accidents in severity level $s$
- $AC_s$ — cost savings per accident reduced for severity level $s$
- $(P/A, i, n)$ — uniform-series present worth factor, with $i = 4\%$ (AASHTO 1977 recommendation) and $n =$ service life (typically 20 years)

#### AMF interpretation

- $AMF = 1.0$ — base condition (no change)
- $AMF < 1.0$ — safety improvement (crashes reduced)
- $AMF > 1.0$ — safety degradation (crashes increased)

The improvement AMF is computed as $AMF_{\text{after}} / AMF_{\text{before}}$.

## Net benefit formula and budget treatment

The Harwood objective subtracts only the safety improvement cost from total benefits, not the resurfacing cost:

$$
NB_{jk} = (PSB_{jk} + PTOB_{jk}) - CC_{jk}^{\text{safety}}
$$

Resurfacing cost enters the budget constraint but not the objective. From the paper (page 153):

> "The net safety benefit is calculated by subtracting the construction cost related to the safety improvements from the total benefits."

This is the discretionary-versus-committed cost decomposition that MCBOMs follows.

#### Verification from Table 4 ($50M budget)

| Component | Value |
|---|---|
| Safety benefits (PSB) | $9,831,263 |
| Operations benefits (PTOB) | $809,651 |
| Total benefits | $10,640,914 |
| Safety improvement cost | $4,481,397 |
| **Net benefit** | **$10,640,914 − $4,481,397 = $6,159,517** |

## Site characteristics (Table 1)

| Site | Area | Roadway | Lanes | ADT | Speed | Length | Lane W | Shoulder W | Shoulder Type | Non-Int | Int | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Rural | Undivided | 2 | 1,000 | 35 | 5.2 | 9 | 2 | Turf | 5 | 3 | 8 |
| 2 | Rural | Undivided | 2 | 3,000 | 40 | 4.6 | 10 | 4 | Composite | 4 | 4 | 8 |
| 3 | Rural | Undivided | 2 | 4,000 | 45 | 5.7 | 11 | 4 | Paved | 11 | 11 | 22 |
| 4 | Urban | Divided | 2 | 7,000 | 50 | 2.5 | 10 | 4 | Paved | 15 | 3 | 18 |
| 5 | Rural | Undivided | 4 | 4,000 | 55 | 4.8 | 10 | 4 | Gravel | 10 | 10 | 20 |
| 6 | Urban | Undivided | 4 | 6,000 | 55 | 5.6 | 11 | 6 | Paved | 14 | 14 | 28 |
| 7 | Rural | Divided | 4 | 5,000 | 50 | 5.6 | 11 | 4 | Paved | 13 | 13 | 26 |
| 8 | Rural | Divided | 4 | 10,000 | 50 | 4.5 | 12 | 8 | Paved | 15 | 15 | 30 |
| 9 | Urban | Undivided | 4 | 10,000 | 60 | 3.5 | 10 | 2 | Paved | 12 | 12 | 24 |
| 10 | Urban | Divided | 6 | 15,000 | 60 | 2.3 | 11 | 4 | Paved | 14 | 14 | 28 |

## Published results (Table 4)

#### $50M budget (unconstrained)

| Component | Value |
|---|---|
| Resurfacing cost | $11,789,849 |
| Safety improvement cost | $4,481,397 |
| Total cost | $16,271,247 |
| Safety benefits (PSB) | $9,831,263 |
| Operations benefits (PTOB) | $809,651 |
| Total benefits | $10,640,914 |
| Penalty for resurfacing without safety (PRP) | $1,563,278 |
| Penalty for not resurfacing (PNR) | $0 |
| **Net benefit** | **$6,159,517** |

#### $10M budget (constrained)

| Component | Value |
|---|---|
| Resurfacing cost | $7,440,798 |
| Safety improvement cost | $2,512,781 |
| Total cost | $9,953,579 |
| Safety benefits (PSB) | $6,610,690 |
| Operations benefits (PTOB) | $577,124 |
| Total benefits | $7,187,814 |
| PRP | $1,223,009 |
| PNR | $5,576,145 |
| **Net benefit** | **$4,675,033** |
| **Do-nothing sites** | **4, 6, 9** |

## Improvement types in RSRAP

The paper considers eight improvement types:

1. Pavement resurfacing — default cost calculation
2. Lane widening — default cost calculation
3. Shoulder widening — default cost calculation
4. Shoulder paving — default cost calculation
5. Horizontal curve improvements — user-supplied costs
6. Roadside improvements — user-supplied costs
7. Intersection turn-lane improvements — default cost calculation
8. User-defined alternatives — user-supplied costs and benefits

## Penalty terms (PNR and PRP)

#### Penalty for not resurfacing (PNR)

- Applied only to the do-nothing alternative ($k = 0$)
- Based on a percentage of pavement replacement cost
- Increases as pavement gets closer to failure
- Reflects avoided future reconstruction costs

#### Penalty for resurfacing without safety improvements (PRP)

- Applied when resurfacing without geometric improvements
- Based on findings that resurfacing may increase speeds and short-term crashes
- Only applies when lane width $< 11$ ft OR shoulder width $< 6$ ft
- User can elect to include or exclude this effect

## Key references for AMFs

The AMFs used in RSRAP are based on:

- Zegeer et al. (1987) — cross-section design effects
- Zegeer et al. (1981) — lane and shoulder width effects
- Zegeer et al. (1992) — horizontal curve improvements
- Griffin and Mak (1987) — Texas farm-to-market road widening
- FHWA Technical Advisory T7570.2 — accident costs

## Limitation for full reproduction

The paper only shows the **selected** alternatives in Tables 2 and 3. It does not provide:

- Costs and benefits for non-selected alternatives
- The specific AMFs used for each improvement type
- The unit construction costs used

The MCBOMs validation uses Harwood's published per-site values for the selected alternatives directly. This verifies that the optimizer reproduces Harwood's site selections at $50M, but it does not test the cost-and-benefit calculation chain (RSRAP cost methodology, AMF-based benefit calculation) against Harwood's published totals. That chain is exercised separately in the worked example validation.

## MCBOMs validation against this case study

| Case | What was tested | Result |
|---|---|---|
| $50M (Table 4) | The MCBOMs optimizer, run on Harwood's published per-site cost and benefit values, reproduces Harwood's published totals | All reported costs and benefits match within rounding; all ten site selections match exactly |
| $10M (Table 3) | The same optimizer at a tight budget where alternative selection becomes binding | Net benefit $4,931,520 vs Harwood's $4,675,033 (5.5% higher); do-nothing sites {4, 6, 9} match exactly |

**The 5.5% divergence at $10M is structural, not a reproduction error.** The MCBOMs prototype does not implement the PNR (Penalty for Not Resurfacing) and PRP (Penalty for Resurfacing without safety improvements) mechanisms. These are excluded by design because Harwood does not publish per-site PNR and PRP values, making them impossible to reproduce from the published data. Without these penalties, the MCBOMs solution at constrained budgets is structurally allowed to outperform Harwood by selecting do-nothing alternatives whose deferral costs are not penalized.

Discount rate and horizon for the validation match Harwood: $i = 4\%$ (AASHTO 1977), $n = 20$ years. The corresponding present worth factor is $(P/A, 4\%, 20) = 13.590$.

## Formulation summary

```python
# Objective: maximize net benefit
# net benefit = total benefits - safety improvement cost
# where total benefits = PSB + PTOB
objective = sum(
    (total_benefit[j, k] - safety_improvement_cost[j, k]) * x[j, k]
    for j in sites
    for k in alternatives[j]
)

# Budget constraint: total cost <= budget
# total cost = resurfacing cost + safety improvement cost
budget_constraint = sum(
    (resurfacing_cost[j, k] + safety_improvement_cost[j, k]) * x[j, k]
    for j in sites
    for k in alternatives[j]
) <= budget

# Mutual exclusivity: exactly one alternative per site
for j in sites:
    sum(x[j, k] for k in alternatives[j]) == 1
```
