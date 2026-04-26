# Validation

The MCBOMs framework is validated against three benchmarks. Each is reproducible from the repository — by running the AMPL/GAMS/LP files in `models/` or by running the Python scripts.

<div class="grid cards" markdown>

-   **[Worked Example](worked-example.md)**

    Single-segment safety-only example from Section 2.3.7. Demonstrates the safety benefit chain end-to-end with full per-severity inputs.

    Expected: $1,493,914 net benefit at $1M budget.

-   **[Harwood (2003)](harwood.md)**

    10-site case study at $50M and $10M budgets. The benchmark Harwood validation case, paper-faithful aggregation.

    Expected at $50M: $6,159,517 (matches paper within $5).

-   **[Banihashemi (2007)](banihashemi.md)**

    13-intersection sub-problem with full IHSDM Crash Prediction Module reconstruction. Demonstrates parametric crash prediction → cost → optimization end-to-end.

    Expected: structural match (Int 12:LTL most cost-effective).

</div>

## Reproducibility

Each instance is reproducible via four routes:

1. **Solver-direct** — open the `.lp` file in CPLEX, Gurobi, CBC, etc.
2. **AMPL** — `ampl <instance>.run` from `models/ampl/`
3. **GAMS** — `gams <instance>.gms` from `models/gams/`
4. **Python** — `python run_harwood_validation.py` or `python examples/banihashemi_intersections.py`

All four produce identical results to the cent.
