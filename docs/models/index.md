# Mathematical Models

The `models/` folder in the repository contains the formal mathematical models for MCBOMs in three industry-standard MILP modeling languages. These are the primary models — the equations from the MCBOMs Methodology document rendered in solver-readable form. The Python implementation is one access method; the AMPL, GAMS, and LP files are another.

Each format page below shows the **full source of every file inline** (click "View source" on any file to expand its content) and provides a **download button** for each file. No need to leave the documentation site to read or save the models.

## File organization

Files are named with a numeric prefix indicating their tier:

| Prefix | What |
|---|---|
| `00_` | Core MCBOMs MILP (Section 2.2 — abstract framework) |
| `01_` | Worked example (Section 2.3.7 — Eq 2.18 from raw inputs) |
| `02_` | Harwood (2003) case study — paper-faithful aggregation |
| `03_` | Banihashemi (2007) intersection sub-problem — full IHSDM CPM parametric |

Same prefix groups files that belong together (e.g., AMPL `02_harwood.mod` + `02_harwood_50m.dat` + `02_harwood_50m.run`).

## Three formats — same mathematics

<div class="grid cards" markdown>

-   **[AMPL](ampl.md)**

    `.mod` model + `.dat` data + `.run` script. Strongest semantic structure; the math is most readable directly from the file.

-   **[GAMS](gams.md)**

    `.gms` combined model and data, single-file. Common in policy and economics modeling.

-   **[LP Format](lp.md)**

    Solver-native, fully self-contained. Numeric form, no symbolic expressions. Drop into any MILP solver.

</div>

## Validation results

All five LP files have been validated by solving with CBC; objectives match the Python implementation and the AMPL/GAMS counterparts to the cent.

| Instance | Optimal Z | Notes |
|---|---|---|
| `00_optimization` | $300 | Illustrative 2-project example, $300K budget |
| `01_worked_example` | $1,493,914 | Net benefit at $1M budget |
| `02_harwood_50m` | $6,159,512 | Matches Harwood Table 4 within $5 |
| `02_harwood_10m` | $4,931,520 | +5.5% above Harwood (no PNR; documented) |
| `03_banihashemi_intersections` | $5,177,251 | Net benefit at $12M unconstrained |

## Honest data scope disclosure

The four numbered tiers do not all reach the same level of parametric detail:

- **`01_worked_example`** is fully parametric end-to-end. All raw inputs (annual crash count, severity distribution, CMF, unit costs, discount parameters) are declared in the model file. Use this instance to demonstrate Eq 2.18 to a reviewer who wants to see the full chain.
- **`03_banihashemi_intersections`** is fully parametric for the IHSDM crash prediction module. Per-intersection ADTs, skew angles, traffic control, LTL/ISD attributes, and delay times are inputs; the model computes crashes/year via Banihashemi Eq 15. The AMF values used are standard IHSDM/Vogt-Bared values; Banihashemi did not publish his exact AMFs.
- **`02_harwood_50m`** and **`02_harwood_10m`** use Harwood's published per-site, per-alternative values from Tables 2 and 3 directly. Harwood's RSRAP computes PSB internally from per-severity AMFs but only the aggregate values are published. Reconstructing his per-severity inputs would require fabricating data; the worked example demonstrates the full Eq 2.18 chain instead.
