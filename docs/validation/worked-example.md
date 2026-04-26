# Worked Example

A single 5-mile rural two-lane segment, designed specifically to demonstrate the safety benefit chain end-to-end with full per-severity inputs.

## Setup

| Input | Value |
|---|---|
| Length | 5 miles |
| Annual crash count | 6.0 |
| Severity distribution (KABCO) | 1.3% / 6.5% / 9.5% / 11.7% / 71.0% |
| Treatment | Lane widening 10 ft → 12 ft |
| CMF | 0.88 |
| Discount rate | 7% |
| Analysis horizon | 20 years |
| Treatment cost | $750,000 |
| Total budget | $1,000,000 |

Unit costs are USDOT BCA May 2025 (2023 dollars):

| Severity | Unit cost |
|---|---|
| K (fatal) | $13,200,000 |
| A (incapacitating injury) | $1,254,700 |
| B (non-incapacitating injury) | $246,900 |
| C (possible injury) | $118,000 |
| O (PDO) | $5,300 |

## Expected results

- **Annual safety benefit**: $211,810
- **Present value safety benefit**: $211,810 × PWF(0.07, 20) = $211,810 × 10.594 = $2,243,914
- **Optimal MILP net benefit at $1M budget**: $2,243,914 − $750,000 = **$1,493,914**

## Reproducing

### Solver-direct (LP)

```bash
cplex < models/lp/01_worked_example.lp
# Or: gurobi_cl models/lp/01_worked_example.lp
```

Expected: `Objective value: 1493913.92`.

### AMPL

```bash
cd models/ampl
ampl 01_worked_example.run
```

The script displays `PWF`, `B_safety_year`, `B_safety_PV`, and the optimal `NetBenefit` variable.

### GAMS

```bash
cd models/gams
gams 01_worked_example.gms
```

### Python

The arithmetic is exercised by `tests/test_safety.py`. Run:

```bash
pytest tests/test_safety.py -v
```

Sixteen tests pass, including the worked example reproduction.

## Why this validation matters

The worked example is the only validation instance where MCBOMs implements the safety benefit chain end-to-end from raw severity inputs all the way through to the optimization. The Harwood instance uses paper-aggregated PSB values (because Harwood does not publish per-severity data); the Banihashemi instance uses a different methodology (IHSDM CPM rather than HSM).

For a reviewer asking "does the safety benefit equation work as written?", this is the file to point to.
