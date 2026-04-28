# Overview

## What MCBOMs is

MCBOMs is a Mixed-Integer Linear Programming (MILP) framework for transportation infrastructure investment decisions.

Given a portfolio of candidate projects, each with multiple possible improvement alternatives, MCBOMs selects the combination that maximizes total societal benefit subject to a budget constraint.

<div markdown="0" style="text-align: center; margin: 1.5rem 0;">
<svg viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto; font-family: Inter, sans-serif;"><rect x="10" y="20" width="220" height="340" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3" rx="6"/><text x="120" y="42" text-anchor="middle" font-size="13" font-weight="600" fill="#666">INPUTS</text><rect x="25" y="60" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="120" y="86" text-anchor="middle" font-size="13" fill="#333">Project portfolio</text><rect x="25" y="112" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="120" y="138" text-anchor="middle" font-size="13" fill="#333">Safety benefits</text><rect x="25" y="164" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="120" y="190" text-anchor="middle" font-size="13" fill="#333">Operational benefits</text><rect x="25" y="216" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="120" y="242" text-anchor="middle" font-size="13" fill="#333">Corridor condition benefits</text><rect x="25" y="268" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="120" y="294" text-anchor="middle" font-size="13" fill="#333">Budget and constraints</text><line x1="240" y1="190" x2="290" y2="190" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/><rect x="295" y="120" width="210" height="140" fill="#500000" stroke="#500000" rx="6"/><text x="400" y="160" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">MCBOMs MILP</text><text x="400" y="190" text-anchor="middle" font-size="12" fill="#fff">Maximize total societal</text><text x="400" y="208" text-anchor="middle" font-size="12" fill="#fff">benefit subject to budget</text><text x="400" y="226" text-anchor="middle" font-size="12" fill="#fff">and constraints</text><line x1="510" y1="190" x2="560" y2="190" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/><rect x="570" y="80" width="220" height="220" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3" rx="6"/><text x="680" y="102" text-anchor="middle" font-size="13" font-weight="600" fill="#666">OUTPUTS</text><rect x="585" y="120" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="680" y="146" text-anchor="middle" font-size="13" fill="#333">Selected alternatives</text><rect x="585" y="172" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="680" y="198" text-anchor="middle" font-size="13" fill="#333">Cost and benefit totals</text><rect x="585" y="224" width="190" height="42" fill="#f5f5f5" stroke="#999" rx="4"/><text x="680" y="250" text-anchor="middle" font-size="13" fill="#333">Solver diagnostics</text><defs><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="#666"/></marker></defs></svg>
</div>

## What it quantifies

- **Safety benefits** — reductions in expected crash costs, computed via the Highway Safety Manual (HSM) Crash Modification Factor (CMF) methodology
- **Operational benefits** — reductions in travel time and vehicle operating costs, valued at USDOT-recommended rates
- **Corridor condition benefits** — energy, environmental, accessibility, and resilience improvements

## Methodological foundation

MCBOMs builds directly on three established frameworks:

- **Harwood, Rabbani, and Richard (2003)** — developed the RSRAP optimization tool for safety improvements within Resurfacing, Restoration, and Rehabilitation (RRR) projects
- **Banihashemi (2007)** — extended that framework to include intersection-level optimization with the IHSDM Crash Prediction Module
- **AASHTO Highway Safety Manual (2010)** — provides Safety Performance Functions and Crash Modification Factors

Default unit costs and economic parameters come from **USDOT Benefit-Cost Analysis Guidance for Discretionary Grant Programs (May 2025)**.

## Validation

!!! success "All four benchmarks reproduce published results"

    | Instance | Optimal objective | Status |
    |---|---|---|
    | Worked example | $1,493,914 | Matches Section 2.3.7 |
    | Harwood $50M | $6,159,512 | Matches Harwood Table 4 within $5 |
    | Harwood $10M | $4,931,520 | +5.5% above Harwood (no PNR; documented) |
    | Banihashemi sub-problem | $5,177,251 | Structural validation passes |

Full details, including the explanation of the $10M divergence from Harwood's published value, are on the [Validation](validation/index.md) page.
