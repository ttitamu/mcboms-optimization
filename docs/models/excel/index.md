# Excel Workbooks

The MCBOMs MILP — the Mixed-Integer Linear Program specified in [Chapter 2 of the Methodology](../../formulation/methodology.md) and implemented in [Python](../../python/index.md), [AMPL](../ampl.md), [GAMS](../gams.md), and [LP format](../lp.md) — is also available as four Excel workbooks. Each workbook is solved using the Solver add-in built into Microsoft Excel, requiring no external software, no Python installation, and no commercial solver license.

The workbooks are intended for reviewers, project managers, and analysts who want to inspect the model and rerun the validation in a familiar tool. They produce numerically identical results to the Python, AMPL, GAMS, and LP forms (subject to the documented PNR caveat for the Harwood $10M instance).

## The four workbooks

| Workbook | Validation case | Budget | Expected net benefit | File |
|---|---|---|---|---|
| Worked example | Methodology Section 2.3.7 (single segment) | $1,000,000 | $1,493,914 | [`01_worked_example.xlsx`](01_worked_example.xlsx) |
| Harwood $50M | Harwood (2003) 10-site, $50M budget | $50,000,000 | $6,159,512 | [`02_harwood_50m.xlsx`](02_harwood_50m.xlsx) |
| Harwood $10M | Harwood (2003) 10-site, $10M budget | $10,000,000 | $4,931,520 | [`02_harwood_10m.xlsx`](02_harwood_10m.xlsx) |
| Banihashemi | Banihashemi (2007) 13-intersection sub-problem | $12,000,000 | $5,177,251 | [`03_banihashemi_intersections.xlsx`](03_banihashemi_intersections.xlsx) |

Each workbook has a README sheet with the full validation context, a parametric Inputs sheet, an Optimization sheet (where the Solver MILP lives), and a Results sheet with a three-state match indicator that displays *Run Solver* (yellow) before Solver has been used, *PASS* (green) once the optimal answer is reached, or *FAIL* (red) if the answer does not match.

## What each workbook contains

Every workbook has the same logical structure:

- **README sheet** — purpose, problem statement, expected result table, how-to-run steps, references, and (where applicable) caveats specific to that validation case.
- **Inputs sheet** — cost and benefit values for every alternative. For Harwood, values come directly from Tables 2 and 3 of the published paper. For Banihashemi, values are computed parametrically using the IHSDM Crash Prediction Module. For the worked example, a separate **Calculation** sheet shows the per-severity benefit chain.
- **Optimization sheet** — the MILP itself. The right side of the sheet holds the alternatives table with binary decision variables (column "Fund? (0/1)", yellow cells), aggregate cells for total cost and net benefit, and per-site mutex constraint cells. The left side holds the mathematical formulation and the exact Solver dialog setup.
- **Results sheet** — the match indicator, summary of the Solver result vs the expected value, and a list of the alternatives selected by Solver.

## Running a workbook

The workflow for each workbook is the same:

1. Open the workbook in **Microsoft Excel (desktop)**. Excel for the web does not include the standard Solver add-in.
2. Enable the Solver add-in if it is not already visible on the Data tab. See "Enabling Solver" below.
3. Go to the **Optimization** sheet. Verify that the decision-variable cells (yellow column "Fund? (0/1)") are all 0.
4. Open the Solver dialog (Data → Solver). Configure the dialog using the Solver setup panel on the **left side** of the Optimization sheet, which lists the exact field values to enter.
5. Click **Solve**. When the Solver Results dialog appears, choose **Keep Solver Solution** and click **OK**.
6. Go to the **Results** sheet. The match indicator should display **PASS** (green) and the net benefit should match the expected value.

## Enabling Solver (one-time setup)

Skip this section if the **Solver** button is already visible on the Data tab.

1. **File** → **Options** → **Add-ins**.
2. At the bottom of the dialog, set **Manage** to *Excel Add-ins* and click **Go**.
3. Check the **Solver Add-in** box and click **OK**.
4. The Solver button now appears on the Data tab in the Analyze group.

This is a standard Microsoft Excel add-in. No license, registration, or download is required.

## A note on entering constraints

Each workbook requires a different number of constraints to be entered into the Solver dialog: 3 for the worked example, 12 for each Harwood instance, and 15 for Banihashemi. Each constraint is added by clicking **Add** in the Solver dialog and typing a cell reference, an operator, and a right-hand side.

The Solver setup panel on the Optimization sheet lists every constraint with the exact cell reference to type. **Type the cell reference exactly as shown.** A common error is misreading a column letter — for example, typing `$Q$37` when the panel says `$O$37`. Because the workbook has empty cells in those off-by-one positions, Solver will accept the constraint and report success, but the constraint is referencing an empty cell that is always 0, so it is trivially satisfied. The result is a Solver run that picks more than one alternative for some sites, producing an over-budget portfolio that looks plausible at first glance but violates the mutex constraints.

If the match indicator displays FAIL after a Solver run, the most likely cause is a constraint cell-reference typo. Re-open the Solver dialog (Data → Solver), compare each constraint line against the Solver setup panel on the Optimization sheet, and correct any mismatches. Then click Solve again.

## Relationship to the other model forms

The Excel workbooks are the same MILP as the [Python implementation](../../python/index.md), [AMPL files](../ampl.md), [GAMS file](../gams.md), and [LP files](../lp.md). The same decision variables, same objective, same constraints, same input data, and (apart from the documented PNR caveat for Harwood $10M) the same numerical results.

The workbooks differ from the other forms in three ways that are worth noting:

1. **Solver choice.** The Python implementation uses Gurobi by default with PuLP/CBC as a fallback. The AMPL and GAMS files target the AMPL and GAMS commercial environments. The LP files are read by CPLEX, Gurobi, CBC, or any solver that supports the standard LP format. The Excel workbooks use Microsoft's bundled Solver add-in, which uses Frontline Systems' Simplex LP method internally. All of these are valid MILP solvers and produce identical results on the validation instances.
2. **Constraint entry is manual.** The Python, AMPL, GAMS, and LP forms have constraints encoded in source files. The Excel form requires the user to enter constraints into the Solver dialog by hand. This is a one-time setup per workbook (constraints persist with the file once saved) but is the source of the cell-reference typo failure mode noted above.
3. **No Penalty for Not Resurfacing (PNR).** All five forms set PNR to zero in the Harwood instance because the per-site PNR values are not published in Harwood (2003) and the PNR mechanism requires pavement-deterioration data not standardized in current FHWA guidance. At the $50M budget this has no effect on the optimal selection (the budget is non-binding). At the $10M budget, MCBOMs's selection differs from Harwood's published portfolio by approximately 5.5%; the MCBOMs answer is mathematically optimal under the formulation we use.

## References

- Harwood, D.W., Rabbani, E.R.K., and Richard, K.R. (2003). Systemwide Optimization of Safety Improvements for Resurfacing, Restoration, or Rehabilitation Projects. *Transportation Research Record* 1840, pp. 148-157.
- Banihashemi, M. (2007). Optimization of highway safety and operation by using crash prediction models with accident modification factors. *Transportation Research Record* 2019(1), 111–117.
- [MCBOMs Methodology](../../formulation/methodology.md) — Section 2.3 (formulation), Section 2.7 (validation against Harwood).
- Microsoft. *Define and solve a problem by using Solver*. Office support documentation.
