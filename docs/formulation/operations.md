# Operational Benefit (Eq 2.21)

The operational benefit captures travel time savings and vehicle operating cost reductions from infrastructure improvements.

!!! note "Scope of the current prototype"
    The mathematical formulation of the operational benefit is documented in this work and in Section 2.4 of the MCBOMs Methodology. A standalone Python module that computes operational benefits from raw inputs is not part of the current prototype. For the validation instances:

    - The **Harwood (2003)** instance uses the paper's published PTOB aggregate values.
    - The **Banihashemi (2007)** intersection sub-problem uses delay-cost minimization.

    A future version of the framework will expose `src/mcboms/benefits/operations.py` for end-to-end parametric computation, in the same pattern as the existing `safety.py` module.

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

## Future implementation

A standalone parametric implementation will follow the same pattern as the existing safety module (`safety.py`):

- **Python**: `src/mcboms/benefits/operations.py` exposes `compute_operational_benefit()` taking $\Delta d$, AADT, OCC, VOT, $\Delta VOC$, and VMT as inputs and returning the present-value benefit
- **AMPL/GAMS**: parametric chain analogous to the worked example for safety, declared in the relevant instance files
- **LP**: evaluated coefficients with derivation in header comments
