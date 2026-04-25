# Operational Benefit (Eq 2.21)

The operational benefit captures travel time savings and vehicle operating cost reductions from infrastructure improvements.

!!! note "Implementation status"
    The operational benefit module is **in development**. The mathematical formulation is locked (per Chapter 2 Section 2.4) but the Python implementation in `src/mcboms/benefits/operations.py` is not yet complete. The AMPL/GAMS/LP files in `models/` do not currently exercise this equation; the validation instances use either pre-computed PTOB values (Harwood) or delay-cost minimization (Banihashemi).

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

## Implementations (planned)

When the operations module is complete, it will follow the same preprocessing pattern as `safety.py`:

- **Python**: `src/mcboms/benefits/operations.py`
- **AMPL**: parametric chain in instance files (analogous to safety in `01_worked_example.mod`)
- **GAMS**: parallel implementation
- **LP**: evaluated coefficients with derivation in header comments
