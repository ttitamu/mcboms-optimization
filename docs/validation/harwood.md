# Harwood (2003) Case Study

The benchmark Harwood (2003) validation case. Ten sites, mix of rural and urban undivided/divided 2- and 4-lane nonfreeway facilities. Two budget levels: $50M and $10M.

**Reference**: Harwood, D. W., Rabbani, E. R. K., & Richard, K. R. (2003). Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects. *Transportation Research Record*, 1840(1), 148–157.

## Expected results at $50M

| Metric | Harwood (2003) | MCBOMs | Difference |
|---|---|---|---|
| Total cost | $16,271,246 | $16,271,247 | +$1 (rounding) |
| Total safety benefit (PSB) | $9,831,263 | $9,831,258 | -$5 (rounding) |
| Total operational benefit (PTOB) | $809,651 | $809,651 | $0 |
| Net benefit | **$6,159,517** | **$6,159,512** | -$5 (rounding) |
| Sites improved | 10 of 10 | 10 of 10 | match |
| Per-site selections | All match | All match | exact |

The match at $50M is rigorous: 4 of 4 metrics agree within $5 (rounding).

## Expected results at $10M

| Metric | Harwood (2003) | MCBOMs |
|---|---|---|
| Net benefit | $4,675,033 | **$4,931,520** |
| Difference | — | +5.5% |

The MCBOMs solution has higher net benefit than Harwood's because MCBOMs does not implement Harwood's "Penalty for Not Resurfacing" (PNR) mechanism. Without PNR, MCBOMs is free to defer sites strictly on net-benefit grounds, finding a strictly better solution by net-benefit at the lower budget.

## Why no PNR?

Harwood's PNR is a deferral penalty assigned to do-nothing alternatives. The penalty's magnitude depends on how close the pavement is to needing replacement (a function of remaining useful life and pavement condition).

We chose not to implement PNR because:

1. **Per-site PNR values are not published** in Harwood (2003). The paper describes the PNR concept (page 152) but the actual values used in the case study are not in Tables 2 or 3.
2. **Banihashemi (2007) also omits PNR**, so the deferred-penalty mechanism is not part of the published validation literature.
3. **Reconstructing PNR would require fabricating data**, which the framework avoids on principle.

The +5.5% MCBOMs solution at $10M is the strictly net-benefit-optimal solution given the available data. This is documented in **Section 2.7.3**.

## Reproducing

### Solver-direct

```bash
cplex < models/lp/02_harwood_50m.lp
# Or:
gurobi_cl models/lp/02_harwood_50m.lp

# Same for $10M:
cplex < models/lp/02_harwood_10m.lp
```

### AMPL

```bash
cd models/ampl
ampl 02_harwood_50m.run
ampl 02_harwood_10m.run
```

### GAMS

```bash
cd models/gams
gams 02_harwood_50m.gms
gams 02_harwood_10m.gms
```

### Python (end-to-end with full reporting)

```bash
python run_harwood_validation.py
```

Output includes:

- **Level 2a ($50M, rigorous)**: 4 of 4 metrics match Harwood Table 4 within 1%. All checks pass.
- **Level 2b ($10M, documented divergence)**: +5.5% difference reported as expected; not a failure.

## Tests

```bash
pytest tests/test_harwood_validation.py -v
```

Sixteen tests pass, including the rigorous $50M reproduction tests and the documented $10M divergence assertion.
