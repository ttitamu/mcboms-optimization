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

## Repository structure

| Folder | What it contains |
|---|---|
| `docs/` | This documentation site, plus the MCBOMs Methodology PDF specification |
| `models/` | Solver-language mathematical models (AMPL, GAMS, LP) |
| `src/mcboms/` | Python implementation |
| `tests/` | Test suite (32 tests) |
| `examples/` | Reproducible Python examples |
| `notebooks/` | Jupyter notebooks |

The mathematical formulation is documented in detail in [MCBOMs Methodology](formulation/methodology.md).

## Validation status

The framework reproduces:

- **Worked example** (Section 2.3.7): $1,493,914 net benefit at $1M budget — matches the manual arithmetic to within numerical precision
- **Harwood (2003) at $50M**: $6,159,512 net benefit — matches Harwood Table 4 within $5 rounding, all 10 site selections match exactly
- **Harwood (2003) at $10M**: $4,931,520 — 5.5% higher than Harwood's published $4,675,033 because the MCBOMs prototype does not implement the Penalty for Not Resurfacing (PNR) mechanism. Harwood does not publish per-site PNR values, and Banihashemi (2007) also omits PNR. Documented in Section 2.7.3.
- **Banihashemi (2007) intersection sub-problem**: structural validation. Int 12:LTL identified as most cost-effective (B/C ≈ 11.5), signalization at Int 3 and Int 4 correctly rejected, rank ordering of LTL improvements consistent with Banihashemi Table 5.

See [Scope of this prototype](reference/status.md) for the validated benchmarks and the framework features ready for agency-specific use cases.

## Who maintains this

Texas A&M Transportation Institute, College Station, TX. For questions about MCBOMs methodology or implementation, contact TTI directly. For bugs or feature requests, [open a GitHub issue](https://github.com/ttitamu/mcboms-optimization/issues).
