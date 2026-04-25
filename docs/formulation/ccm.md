# Corridor Condition Benefit (Eq 2.27)

The Corridor Condition Measures (CCM) capture multidisciplinary benefits beyond safety and operations: energy, emissions, accessibility, and resilience improvements.

!!! note "Implementation status"
    The CCM module is **in development**. The mathematical structure is locked (per Chapter 2 Section 2.5) but per-category monetization functions and the Python implementation `src/mcboms/benefits/ccm.py` are not yet complete.

## The equation

$$
B_{ij}^{\mathrm{corridor}} = \sum_{c \in C} \sum_{t=1}^{T} \Delta Q_{c,t} \cdot V_c \cdot DF_t
$$

Where:

- $C$ is the set of CCM categories
- $\Delta Q_{c,t}$ is the change in CCM quantity in year $t$ (e.g., kWh saved, tons CO₂ reduced)
- $V_c$ is the unit value for category $c$ (USDOT or FEMA standard)
- $DF_t$ is the year-$t$ discount factor

## CCM categories under consideration

| Category | Quantity | Unit value source |
|---|---|---|
| Energy reduction | kWh / year | USDOT BCA May 2025 |
| Emissions reduction | metric tons CO₂-equivalent | USDOT BCA May 2025, EPA SCC |
| Mobility & accessibility | trips, person-hours of access | USDOT BCA May 2025 |
| Resilience | avoided disaster damages, expected | FEMA Standard Economic Values v13 (2024) |
| Equity / underserved access | accessibility-weighted demand | TBD per agency policy |
| Pavement / asset condition | IRI improvement, infrastructure life | Agency-specific |

## Double-counting prevention

The framework includes mathematical protocols to prevent double-counting between CCM categories and the safety/operations modules. For example, mobility energy productivity (MEP) embeds travel-time components that overlap with operational benefits. The combined formulation enforces:

$$
B_{ij}^{\mathrm{operations}} \cap B_{ij}^{\mathrm{corridor, MEP}} = \emptyset
$$

This is documented in Chapter 2 Section 2.5.4.

## Implementations (planned)

When the CCM module is complete:

- **Python**: `src/mcboms/benefits/ccm.py` — modular per-category monetization functions
- **AMPL/GAMS**: parametric chain in instance files
- **LP**: evaluated coefficients

For the current validation instances (worked example, Harwood, Banihashemi), CCM benefits are zero because the source case studies do not include CCM data.
