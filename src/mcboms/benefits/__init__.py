"""
Benefit Calculation Modules for MCBOMs.

This sub-package implements the benefit-estimation framework described in
Section 3.2 of the Task 4 report:

    - safety     (Section 3.2.1): Crash reduction monetized via HSM CMFs and VSL.
    - operations (Section 3.2.2): Travel time savings and VOC reductions.   [TBD]
    - ccm        (Section 3.2.3): Corridor Condition Measures.              [TBD]

Each component is computed independently, then summed to produce the total
per-alternative benefit B_ij(total) consumed by the optimizer (Section 3.1.2).
"""

from mcboms.benefits import safety
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
    "SEVERITY_ORDER",
    "SafetySegment",
    "combine_cmfs",
    "compute_alternative_safety_benefit",
    "safety_benefit",
    "safety_benefit_time_varying",
]
