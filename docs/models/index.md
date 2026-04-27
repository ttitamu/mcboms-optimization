# Mathematical Models

The `models/` directory contains the MCBOMs formulation in four representations: AMPL, GAMS, the LP file format, and Microsoft Excel workbooks. These files are the formal model definitions; the Python implementation in `src/mcboms/` is a parallel access path that calls the same mathematics through Gurobi.

Each format page below renders every file inline with a download button. The full source is visible without leaving the documentation site.

## File organization

Files use a numeric prefix to indicate the tier of the instance:

| Prefix | Instance |
|---|---|
| `00_` | Core MCBOMs MILP — the abstract optimization layer |
| `01_` | Worked example — single-segment safety benefit from raw inputs |
| `02_` | Harwood (2003) case study — paper-faithful aggregation |
| `03_` | Banihashemi (2007) intersection sub-problem — IHSDM Crash Prediction Module |

Files sharing a prefix belong to the same instance (for example, AMPL `02_harwood.mod` + `02_harwood_50m.dat` + `02_harwood_50m.run`).

## Four formats, one mathematics

<div class="grid cards" markdown>

-   **[AMPL](ampl.md)**

    Separate `.mod` (model), `.dat` (data), and `.run` (script) files. Algebraic expressions are written close to the form used in the methodology document, which makes the model structure directly inspectable.

-   **[GAMS](gams.md)**

    Single `.gms` file combining model and data declarations. Compatible with the GAMS commercial solver suite and widely used in transportation policy work.

-   **[LP Format](lp.md)**

    Solver-native flat text. No symbolic expressions; the constraint matrix is fully expanded into numeric coefficients. Compatible with CPLEX, Gurobi, CBC, and any solver that reads the standard LP format.

-   **[Excel Workbooks](excel/index.md)**

    Self-contained `.xlsx` files solved using Excel's built-in Solver add-in. Each workbook includes the input data, optimization model, and Solver setup on a single sheet.

</div>

## Validation

The LP files have been solved with CBC; objective values agree numerically with the Python implementation, the AMPL and GAMS counterparts, and the Excel workbooks.

| Instance | Optimal objective | Notes |
|---|---|---|
| `00_optimization` | $300 | Illustrative two-project example at $300K budget |
| `01_worked_example` | $1,493,914 | Net benefit at $1M budget |
| `02_harwood_50m` | $6,159,512 | Matches Harwood Table 4 within rounding tolerance |
| `02_harwood_10m` | $4,931,520 | 5.5% above the published Harwood value; the difference is attributable to the PNR mechanism, which is documented and explained |
| `03_banihashemi_intersections` | $5,177,251 | Net benefit at the unconstrained budget |

## Parametric depth across instances

The four tiers reach different levels of parametric detail, reflecting what the source literature publishes:

- **`01_worked_example`** is fully parametric. Annual crash count, severity distribution, CMF, unit costs, and discount parameters are declared as named inputs in the model file. The full safety-benefit chain is therefore visible directly from the model.
- **`03_banihashemi_intersections`** is fully parametric for the IHSDM Crash Prediction Module. Per-intersection ADTs, skew angles, traffic control, left-turn-lane and intersection-sight-distance attributes, and delay times appear as inputs; the model computes expected annual crashes per the published prediction equation. AMF values follow the standard IHSDM and Vogt-Bared (1998) tables, since the Banihashemi paper does not publish per-alternative AMF values.
- **`02_harwood_50m`** and **`02_harwood_10m`** use the per-site, per-alternative cost and benefit values published in Harwood (2003) Tables 2 and 3 directly. The original RSRAP tool computes PSB internally from per-severity AMFs, but only the aggregate values appear in the publication. The worked example tier provides a fully parametric demonstration of the safety chain that the Harwood instance does not require.
