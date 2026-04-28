# Overview

## What MCBOMs is

MCBOMs is a Mixed-Integer Linear Programming (MILP) framework for optimizing transportation infrastructure investment decisions. Given a portfolio of candidate projects (sites or intersections), each with multiple possible improvement alternatives, MCBOMs selects the combination that maximizes total societal benefit subject to a budget constraint.

The framework is developed at the **Texas A&M Transportation Institute**.

## What benefits the framework quantifies

- **Safety benefits** — reductions in expected crash costs, computed via the Highway Safety Manual (HSM) Crash Modification Factor (CMF) methodology
- **Operational benefits** — reductions in travel time and vehicle operating costs, valued at USDOT-recommended rates
- **Corridor condition benefits** — energy, environmental, accessibility, and resilience improvements

## Methodological foundation

MCBOMs builds directly on three established frameworks:

- **Harwood, Rabbani, and Richard (2003)** — developed the RSRAP optimization tool for safety improvements within Resurfacing, Restoration, and Rehabilitation (RRR) projects
- **Banihashemi (2007)** — extended that framework to include intersection-level optimization with the IHSDM Crash Prediction Module
- **AASHTO Highway Safety Manual (2010)** — provides Safety Performance Functions and Crash Modification Factors

Default unit costs and economic parameters come from **USDOT Benefit-Cost Analysis Guidance for Discretionary Grant Programs (May 2025)**.

## Validation summary

| Instance | Optimal objective | Status |
|---|---|---|
| Worked example | $1,493,914 | Matches Section 2.3.7 |
| Harwood $50M | $6,159,512 | Matches Harwood Table 4 within $5 |
| Harwood $10M | $4,931,520 | +5.5% above Harwood (no PNR; documented) |
| Banihashemi sub-problem | $5,177,251 | Structural validation passes |

Full details, including the explanation of the $10M divergence from Harwood's published value, are on the [Validation](validation/index.md) page.

## Repository structure

| Folder | What it contains |
|---|---|
| `docs/` | This documentation site, plus the MCBOMs Methodology PDF specification |
| `models/` | Solver-language models (AMPL, GAMS, LP) and Excel workbooks |
| `src/mcboms/` | Python implementation |
| `tests/` | Test suite (32 tests) |
| `examples/` | Reproducible Python examples |
| `notebooks/` | Jupyter notebooks |

The mathematical formulation is documented in detail in [MCBOMs Methodology](formulation/methodology.md).

## Institutional context

Texas A&M Transportation Institute, College Station, TX. Developed under FHWA Contract HRSO20240009PR.
