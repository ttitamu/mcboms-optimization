# Corridor Condition Benefit

The Corridor Condition Measures (CCM) capture multidisciplinary benefits beyond safety and operations: energy, emissions, accessibility, and resilience improvements.

!!! note "Scope of the current prototype"
    The mathematical structure is documented here and in Section 2.5 of the MCBOMs Methodology, and is implemented in `src/mcboms/benefits/ccm.py` (34 unit tests in `tests/test_ccm.py`). The Python module provides per-category monetization functions for energy, emissions, accessibility, resilience, and pavement, plus a top-level aggregator with explicit double-counting prevention against the operational benefit module.

    The validation instances (worked example, Harwood, Banihashemi) do not include CCM data, so this benefit is zero for those cases. The module is ready for use by an agency that supplies the per-category quantities (kWh saved, CO2 tons avoided, trips enabled, expected avoided damages, lane-miles improved).

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
| Underserved-area access | accessibility-weighted demand | Agency-specific |
| Pavement / asset condition | IRI improvement, infrastructure life | Agency-specific |

## Double-counting prevention

The framework includes mathematical protocols to prevent double-counting between CCM categories and the safety/operations modules. For example, mobility energy productivity (MEP) embeds travel-time components that overlap with operational benefits. The combined formulation enforces:

$$
B_{ij}^{\mathrm{operations}} \cap B_{ij}^{\mathrm{corridor, MEP}} = \emptyset
$$

This is documented in Section 2.5.4.

## Implementation

The Python module provides per-category monetization functions:

- **`compute_energy_benefit(annual_kwh_saved, value_per_kwh, ...)`** — energy category, default $0.12/kWh
- **`compute_emissions_benefit(annual_co2_tons_avoided, scc_per_ton, ...)`** — emissions category, default Social Cost of Carbon $224/metric-ton (USDOT BCA May 2025)
- **`compute_accessibility_benefit(annual_trips_enabled, value_per_trip, ...)`** — mobility/accessibility category, default $12/person-trip
- **`compute_resilience_benefit(expected_avoided_damages, ...)`** — resilience category, takes annualized expected-value avoided damages directly (FEMA Standard Economic Values v13 typically used for the input estimation)
- **`compute_pavement_benefit(lane_miles, ...)`** — pavement / asset condition category

Plus a top-level aggregator:

- **`compute_corridor_benefit(inputs: CCMInputs, operations_already_computed=False, ...)`** — sums all categories and enforces the double-counting check against operations.py
- **`compute_corridor_benefits_df(inputs_df)`** — DataFrame batch interface

The double-counting check raises `ValueError` if accessibility (trips enabled) is non-zero AND the operational benefit module is also being computed AND the user has not explicitly confirmed they have handled the overlap by setting `accessibility_overlaps_with_operations=True` on the `CCMInputs` dataclass.

For the current validation instances (worked example, Harwood, Banihashemi), CCM benefits are zero because the source case studies do not include CCM data.
