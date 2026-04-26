# Operational Benefit

The operational benefit captures travel time savings and vehicle operating cost reductions from infrastructure improvements.

!!! note "Scope of the current prototype"
    The mathematical formulation is documented here and in Section 2.4 of the MCBOMs Methodology, and is implemented in `src/mcboms/benefits/operations.py` (26 unit tests in `tests/test_operations.py`). The Python module computes the present-value operational benefit from raw inputs (delay change, AADT, occupancy, VOT, VOC change, VMT) using USDOT BCA May 2025 default unit values, and exposes both single-class and DataFrame-batch interfaces.

    The validation instances do not exercise this module:

    - The **Harwood (2003)** instance uses the paper's published PTOB aggregate values rather than recomputing from raw delay inputs (the paper does not publish per-segment $\Delta d$ values).
    - The **Banihashemi (2007)** intersection sub-problem uses delay-cost minimization at intersections; the inputs differ from the segment-level form of the operational benefit equation.

    The module is ready for use by an agency that supplies the per-segment operational inputs.

## The equation

The annual operational benefit aggregates over vehicle classes $v$:

$$
B_{ij,t}^{\mathrm{operations}} = \sum_{v} \left[ \Delta d_v \cdot AADT \cdot 365 \cdot OCC_v \cdot VOT_v + \Delta VOC_v \cdot VMT_v \right]
$$

Where:

- $\Delta d_v$ — change in per-vehicle delay (hours), computed from before/after travel time
- $AADT$ — Annual Average Daily Traffic (vehicles per day)
- $OCC_v$ — average vehicle occupancy for class $v$ (persons per vehicle)
- $VOT_v$ — value of time for class $v$ ($/person-hour)
- $\Delta VOC_v$ — change in vehicle operating cost ($/vehicle-mile)
- $VMT_v$ — annual Vehicle Miles Traveled for class $v$

The first term monetizes travel time savings; the second monetizes operating cost savings (fuel, maintenance, tires).

## Annual to present value

Same as for safety benefit:

$$
B_{ij}^{\mathrm{operations, PV}} = B_{ij}^{\mathrm{operations, year}} \cdot \mathrm{PWF}(r, T)
$$

## Default values

USDOT BCA Guidance May 2025 default values (2023 dollars):

| Parameter | Value |
|---|---|
| VOT (all-purposes) | $21.10 / person-hour |
| VOT (personal) | $19.40 / person-hour |
| VOT (business) | $33.50 / person-hour |
| Average vehicle occupancy (passenger) | 1.52 |
| VOC (light-duty vehicle) | $0.56 / vehicle-mile |

See [Default Parameters](../reference/parameters.md) for the full table with sources.

## Implementation

The Python module exposes the equation through several entry points:

- **`compute_travel_time_benefit(delta_d, aadt, occupancy, vot)`** — the travel-time savings term
- **`compute_voc_benefit(delta_voc, vmt)`** — the second term
- **`compute_operational_benefit(vehicle_classes, discount_rate, analysis_horizon)`** — the full present-value form aggregated across vehicle classes
- **`compute_simple_operational_benefit(...)`** — convenience wrapper for the single passenger-class case (typical rural two-lane analysis)
- **`compute_operational_benefits_df(inputs_df)`** — DataFrame batch interface for many (site, alternative) pairs at once

Default unit values follow USDOT BCA Guidance May 2025: VOT $21.10/person-hour (all purposes), occupancy 1.52 (passenger), VOC $0.56/vehicle-mile (light-duty).

The AMPL and GAMS solver-language files declare the same equation in parametric form. The LP files have evaluated coefficients with the derivation in header comments.
