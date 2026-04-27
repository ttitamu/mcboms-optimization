# Excel Workbooks

Each workbook is a self-contained `.xlsx` file that solves the MCBOMs MILP using the Solver add-in built into Microsoft Excel. The workbooks are intended for reviewers and analysts who want to inspect and re-run the model in Excel without installing Python or a commercial solver. They produce numerically identical results to the AMPL, GAMS, LP, and Python forms.

This page lists every workbook in `docs/models/excel/`. Each file is downloadable directly. The workbook structure (README, Inputs, Optimization, Results sheets) is the same across all four; the Solver setup panel on the Optimization sheet lists the exact dialog entries.

---

## How to run

Open a workbook in Microsoft Excel (desktop). On the Data tab, click Solver. Configure the dialog using the setup panel on the Optimization sheet, then click Solve. The Results sheet displays a match indicator that shows PASS once the optimal answer is reached. Expected results are documented in [Validation](../../validation/index.md).

If Solver does not appear on the Data tab, enable it via File → Options → Add-ins → Manage Excel Add-ins → Go, then check Solver Add-in.

---

## 01_worked_example.xlsx

Single-segment worked example from Methodology Section 2.3.7. Lane widening (10 ft to 12 ft, CMF 0.88) at $1,000,000 budget. Expected net benefit $1,493,914.

[:material-download: Download `01_worked_example.xlsx`](https://github.com/ttitamu/mcboms-optimization/raw/main/docs/models/excel/01_worked_example.xlsx){ .md-button .file-button }

---

## 02_harwood_50m.xlsx

Harwood (2003) ten-site case study at the $50M budget. Cost and benefit values from Tables 2 and 3 of the paper. Expected net benefit $6,159,512, matching Harwood Table 4 within rounding tolerance.

[:material-download: Download `02_harwood_50m.xlsx`](https://github.com/ttitamu/mcboms-optimization/raw/main/docs/models/excel/02_harwood_50m.xlsx){ .md-button .file-button }

---

## 02_harwood_10m.xlsx

Same ten sites at the $10M budget. The MCBOMs optimal selection (sites 1, 4, 6, 8 do nothing) gives a net benefit of $4,931,520, approximately 5.5% above Harwood's published $4,675,033. The difference is attributable to the Penalty for Not Resurfacing (PNR) term, set to zero in this prototype because per-site PNR values are not published in the paper.

[:material-download: Download `02_harwood_10m.xlsx`](https://github.com/ttitamu/mcboms-optimization/raw/main/docs/models/excel/02_harwood_10m.xlsx){ .md-button .file-button }

---

## 03_banihashemi_intersections.xlsx

Banihashemi (2007) thirteen-intersection sub-problem at the $12M budget. Cost and benefit values are computed parametrically using the IHSDM Crash Prediction Module (Banihashemi Eq 15). Expected net benefit $5,177,251.

[:material-download: Download `03_banihashemi_intersections.xlsx`](https://github.com/ttitamu/mcboms-optimization/raw/main/docs/models/excel/03_banihashemi_intersections.xlsx){ .md-button .file-button }
