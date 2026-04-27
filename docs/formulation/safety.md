# Safety Benefit

The safety benefit of an alternative is computed via the Highway Safety Manual (HSM) Crash Modification Factor (CMF) methodology, valued at USDOT-recommended unit crash costs.

## The equation

For one segment, one alternative, one year:

$$
B_{ij,t}^{\mathrm{safety}} = \sum_{s \in S} \left( E_{i,s}^{\mathrm{nobuild}} - E_{ij,s}^{\mathrm{build}} \right) \cdot UC_s
$$

Where:

- $S = \{K, A, B, C, O\}$ is the KABCO severity scale
- $E_{i,s}^{\mathrm{nobuild}}$ is expected crashes of severity $s$ at site $i$ in the no-build scenario
- $E_{ij,s}^{\mathrm{build}}$ is expected crashes of severity $s$ at site $i$ under alternative $j$
- $UC_s$ is the unit cost per crash of severity $s$ (USDOT BCA May 2025 values)

## Severity disaggregation

Total expected crashes are disaggregated by severity using a known proportion vector $p_s$:

$$
E_{i,s}^{\mathrm{nobuild}} = N_i \cdot p_s
$$

where $N_i$ is the observed (or SPF-predicted) annual crash count at site $i$, and $p_s$ is the empirical proportion of crashes of severity $s$. The severity proportions sum to 1: $\sum_s p_s = 1$.

## CMF application

The build-scenario crashes are computed by applying the Crash Modification Factor:

$$
E_{ij,s}^{\mathrm{build}} = E_{i,s}^{\mathrm{nobuild}} \cdot \mathrm{CMF}_{ij}
$$

When multiple treatments are applied at the same site (e.g., lane widening plus shoulder paving), CMFs are typically combined multiplicatively per HSM convention:

$$
\mathrm{CMF}_{ij,\,\mathrm{combined}} = \prod_{m} \mathrm{CMF}_{ij,m}
$$

## Annual to present value

The annual safety benefit is multiplied by the Present Worth Factor for a uniform stream of constant annual amounts:

$$
B_{ij}^{\mathrm{safety, PV}} = B_{ij}^{\mathrm{safety, year}} \cdot \mathrm{PWF}(r, T)
$$

where

$$
\mathrm{PWF}(r, T) = \frac{(1+r)^T - 1}{r \cdot (1+r)^T}
$$

For the USDOT default $r = 0.07$ and $T = 20$, $\mathrm{PWF} = 10.594$.

## Worked example

Section 2.3.7 walks through a complete example:

- 5-mile rural two-lane segment
- Annual crash count: $N = 6.0$
- Severity distribution (KABCO): $p = (0.013, 0.065, 0.095, 0.117, 0.710)$
- Treatment: lane widening 10 ft → 12 ft, $\mathrm{CMF} = 0.88$
- Discount rate $r = 0.07$, horizon $T = 20$ years
- Unit costs (USDOT BCA May 2025, 2023 dollars):

| Severity | Unit cost |
|---|---|
| K (fatal) | $13,200,000 |
| A (incapacitating injury) | $1,254,700 |
| B (non-incapacitating injury) | $246,900 |
| C (possible injury) | $118,000 |
| O (PDO) | $5,300 |

The annual benefit works out to:

$$
B^{\mathrm{safety, year}} = \sum_{s} 6.0 \cdot p_s \cdot (1 - 0.88) \cdot UC_s = \$211{,}810
$$

And the present value:

$$
B^{\mathrm{safety, PV}} = \$211{,}810 \cdot 10.594 = \$2{,}243{,}914
$$

This is the only validation instance where MCBOMs implements the safety benefit equation end-to-end from raw severity inputs. See [Worked Example validation](../validation/worked-example.md) for the full reproduction across all three solver formats.

## Implementations

- **Python**: `src/mcboms/benefits/safety.py` — `compute_safety_benefit()` function
- **AMPL** (full chain): `models/ampl/01_worked_example.mod` declares severity proportions, unit costs, CMF, and the full safety-benefit chain as parametric expressions
- **GAMS** (full chain): `models/gams/01_worked_example.gms`
- **LP**: `models/lp/01_worked_example.lp` carries the evaluated coefficient ($1,493,914 net at $1M budget) with header comments showing the derivation

## Tests

`tests/test_safety.py` includes 16 unit tests covering:

- Severity disaggregation
- Single-CMF application
- Multi-CMF multiplicative combination
- PWF computation across discount rates and horizons
- Reproduces the worked example to within numerical precision
