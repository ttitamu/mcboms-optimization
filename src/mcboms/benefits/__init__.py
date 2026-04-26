"""
Benefit Calculation Modules for MCBOMs.

This sub-package implements the three benefit components from the MCBOMs
Methodology document (Sections 2.3, 2.4, 2.5):

    - safety      (Section 2.3, Eq 2.18): Crash reduction monetized via
                  HSM CMFs and USDOT crash unit costs.
    - operations  (Section 2.4, Eq 2.21): Travel time savings and VOC
                  reductions, valued at USDOT-recommended rates.
    - ccm         (Section 2.5, Eq 2.27): Corridor Condition Measures —
                  energy, emissions, accessibility, resilience, pavement.

Each module computes independently, then results are summed to produce
the total per-alternative benefit B_ij(total) consumed by the optimizer.

The framework enforces explicit double-counting prevention between
operations and ccm.accessibility — see ccm.compute_corridor_benefit().
"""

from mcboms.benefits import ccm, operations, safety
from mcboms.benefits.ccm import (
    CCMInputs,
    compute_accessibility_benefit,
    compute_corridor_benefit,
    compute_corridor_benefits_df,
    compute_emissions_benefit,
    compute_energy_benefit,
    compute_pavement_benefit,
    compute_resilience_benefit,
)
from mcboms.benefits.operations import (
    DEFAULT_OCC,
    DEFAULT_VOC,
    DEFAULT_VOT,
    VehicleClassInputs,
    compute_annual_operational_benefit,
    compute_operational_benefit,
    compute_operational_benefits_df,
    compute_simple_operational_benefit,
    compute_travel_time_benefit,
    compute_voc_benefit,
)
from mcboms.benefits.safety import (
    SEVERITY_ORDER,
    SafetySegment,
    combine_cmfs,
    compute_alternative_safety_benefit,
    safety_benefit,
    safety_benefit_time_varying,
)

__all__ = [
    "safety",
    "operations",
    "ccm",
    "SEVERITY_ORDER",
    "SafetySegment",
    "combine_cmfs",
    "compute_alternative_safety_benefit",
    "safety_benefit",
    "safety_benefit_time_varying",
    "VehicleClassInputs",
    "compute_travel_time_benefit",
    "compute_voc_benefit",
    "compute_annual_operational_benefit",
    "compute_operational_benefit",
    "compute_simple_operational_benefit",
    "compute_operational_benefits_df",
    "DEFAULT_VOT",
    "DEFAULT_OCC",
    "DEFAULT_VOC",
    "CCMInputs",
    "compute_energy_benefit",
    "compute_emissions_benefit",
    "compute_accessibility_benefit",
    "compute_resilience_benefit",
    "compute_pavement_benefit",
    "compute_corridor_benefit",
    "compute_corridor_benefits_df",
]
