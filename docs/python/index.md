# Python Implementation

The Python implementation in `src/mcboms/` is one of three access methods to the framework. It's intended for users who want to integrate MCBOMs into a larger Python pipeline, automate runs, or extend the framework with new benefit categories.

For users who run MILP problems in commercial solvers (CPLEX, Gurobi, GAMS), the [solver-language models](../models/index.md) are an alternative entry point that does not require Python.

## Sections

<div class="grid cards" markdown>

-   **[Installation](installation.md)**

    Set up Python, the package, and an optional Gurobi backend.

-   **[Architecture](architecture.md)**

    How the Python code is organized — `core`, `benefits`, `io`, `utils`, `data`, `tests`.

-   **[Extending the Framework](extending.md)**

    How to add new benefit modules, validation cases, and constraints.

</div>

## At a glance

```python
from mcboms.core import Optimizer
from mcboms.data.harwood_alternatives import get_harwood_alternatives
import pandas as pd

alternatives = get_harwood_alternatives()
sites = pd.DataFrame({"site_id": sorted(alternatives["site_id"].unique())})

optimizer = Optimizer(
    sites=sites,
    alternatives=alternatives,
    budget=50_000_000,
    discount_rate=0.04,
    analysis_horizon=20,
)
result = optimizer.solve()
print(f"Net benefit: ${result.net_benefit:,.0f}")
print(f"Total cost:  ${result.total_cost:,.0f}")
```

Output:

```
Net benefit: $6,159,512
Total cost:  $16,271,247
```
