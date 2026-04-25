"""
Banihashemi (2007) Intersection Sub-Problem Data

Reconstructs the 13-intersection portion of Banihashemi's Table 3 case study
for validation of the MCBOMs MILP optimizer.

Data sources:
- Banihashemi (2007), TRR 2019, Table 3 (p. 115): intersection characteristics
  and delay times for all improvement combinations
- Banihashemi (2007), p. 114: intersection improvement costs
- Banihashemi (2007), p. 109: unit delay cost $12.50/vehicle-hour
- Banihashemi (2007), p. 109: avg crash costs $55,239 (3-leg stop),
  $81,375 (4-leg stop), $31,665 (4-leg signalized)
- Banihashemi (2007), p. 113: IHSDM intersection CPM parameters
  3-leg stop:     α=-10.9,  β=0.79, γ=0.49, Ci=0.79
  4-leg stop:     α=-9.34,  β=0.60, γ=0.61, Ci=0.98
  4-leg signalized: α=-5.73, β=0.60, γ=0.20, Ci=0.94

Intersection type inference:
Banihashemi's Table 3 does not explicitly label each intersection as 3-leg
stop, 4-leg stop, or 4-leg signalized. The type is inferred from:
  - Whether the existing control is "Signalized" (→ 4-leg signalized)
  - Whether all-stop is one of the improvement options (→ 4-leg, since 3-leg
    intersections typically don't have all-stop as a practical option)
  - Default: 4-leg stop-controlled when ambiguous

Intersections 3 and 4 have Signalized as the improvement → 4-leg signalized or
4-leg stop-controlled baseline; we treat the existing as 4-leg stop (both have
minor-stop existing) and signalized as a different type after improvement.
Intersection 10 has Signalized existing + signalized alternative → 4-leg signalized.

Base AMFs from Banihashemi p. 112:
  AMF10 (skew angle): base = 0°
  AMF11 (traffic control): base = two-way stop (all-way stop has different value)
  AMF12 (left-turn lane): base = none
  AMF13 (right-turn lane): base = none
  AMF14 (sight distance limitation): base = none

AMF values for intersection improvements (from IHSDM and Vogt/Bared):
  Skew angle: AMF10 = exp(0.0054 × skew_degrees) for 4-leg stop; roughly
              linear in skew for small angles. For simplicity we use
              AMF10 = 1.0 for skew=0 (eliminated) and AMF10 scales linearly.
              Banihashemi uses IHSDM values; for our reproduction we apply
              a simple model: AMF10 = 1 + 0.0054*skew (consistent with
              Harwood/Bauer formulations).
  Traffic control: minor-stop base = 1.0; all-stop AMF11 ≈ 0.53 per
              FHWA safety research (Srinivasan et al., 2012). We use
              published IHSDM value of 0.70 for 4-leg stop → 4-leg all-stop.
              Signalization AMF11 (from 4-leg stop to 4-leg signalized) ≈ 0.56
              based on FHWA evaluation.
  Left-turn lane: AMF12 = 0.67 (major road LTL on 4-leg stop); AMF12 = 0.77
              on signalized
  Right-turn lane: AMF13 = 0.86 (not used in case study; all intersections
              show "No" for RTL)
  Sight distance: AMF14 = 1.42 with deficiency; 1.0 with deficiency removed.

These AMF values are needed for computing the IHSDM CPM expected crash
numbers. HOWEVER, Banihashemi's Table 3 provides the delay time directly for
each combination, and crash predictions are derived from the CPM. For the
intersection sub-problem we:
  1. Compute expected crashes per intersection-combination using the CPM
     with the specified α/β/γ/Ci parameters
  2. Multiply by the facility-type avg crash cost to get crash cost
  3. Add delay cost = delay_hours * $12.50
  4. Multiply by 20 years = Banihashemi's project lifetime
  5. Minimize total (crash + delay) cost subject to budget

NOTE ON AMFs: Because Banihashemi's AMF values for each alternative are not
published in his paper, we cannot compute the CPM results to exact numerical
match. For validation we check:
  - That the CPM formulation is correctly implemented
  - That the solution structure (which intersections get improved at each
    budget level) matches Banihashemi's Table 5
  - That the ordering of intersections by cost-effectiveness is consistent
"""

import math
import pandas as pd


# ---------------------------------------------------------------------------
# IHSDM CPM parameters (Banihashemi Eq. 15, p. 113)
# ---------------------------------------------------------------------------
INT_CPM = {
    "3leg_stop":    {"alpha": -10.9,  "beta": 0.79, "gamma": 0.49, "Ci": 0.79, "crash_cost": 55_239},
    "4leg_stop":    {"alpha":  -9.34, "beta": 0.60, "gamma": 0.61, "Ci": 0.98, "crash_cost": 81_375},
    "4leg_signal":  {"alpha":  -5.73, "beta": 0.60, "gamma": 0.20, "Ci": 0.94, "crash_cost": 31_665},
}


def cpm_crashes(int_type: str, adt1: float, adt2: float, amf_product: float) -> float:
    """Expected crashes per year per Eq. 15 of Banihashemi (2007)."""
    p = INT_CPM[int_type]
    base = math.exp(p["alpha"] + p["beta"] * math.log(adt1) + p["gamma"] * math.log(adt2))
    return base * p["Ci"] * amf_product


# ---------------------------------------------------------------------------
# Economic parameters (Banihashemi p. 109)
# ---------------------------------------------------------------------------
UNIT_DELAY_COST = 12.50    # $ per vehicle-hour
PROJECT_LIFETIME = 20      # years


# ---------------------------------------------------------------------------
# AMF values for intersection features
# ---------------------------------------------------------------------------
# These are taken from IHSDM documentation (FHWA-RD-99-207) and consistent
# with Vogt/Bared base models. When Banihashemi's exact values differ, the
# CPM crash counts will differ by the ratio of AMFs — but relative ordering
# of alternatives should be preserved.
#
# Key rule: these are the multiplicative AMFs relative to the base (existing)
# condition. A smaller AMF = more crash reduction.

def amf_skew(skew_deg: float, int_type: str) -> float:
    """AMF for intersection skew angle. Base = 0 degrees, AMF = 1.0.
    For stop-controlled: AMF_skew = exp(0.0054 * skew)
    For signalized: skew has negligible effect, AMF ≈ 1.0"""
    if "signal" in int_type:
        return 1.0
    return math.exp(0.0054 * abs(skew_deg))


def amf_traffic_control(existing: str, new: str) -> float:
    """AMF for changing traffic control.
    From FHWA safety research (Srinivasan et al. 2012 and IHSDM):
    minor-stop → all-stop: AMF ≈ 0.70 (30% crash reduction)
    minor-stop → signalized: AMF ≈ 0.56 for 4-leg (44% reduction)
    """
    if existing == new:
        return 1.0
    # Standardize
    keymap = {"Minor stop": "minor_stop", "All stop": "all_stop", "Signalized": "signalized"}
    e = keymap.get(existing, existing.lower().replace(" ", "_"))
    n = keymap.get(new, new.lower().replace(" ", "_"))
    transitions = {
        ("minor_stop", "all_stop"): 0.70,
        ("minor_stop", "signalized"): 0.56,
        ("all_stop", "signalized"): 0.80,  # less common
    }
    return transitions.get((e, n), 1.0)


def amf_ltl(has_ltl: bool, is_signalized: bool) -> float:
    """AMF for left-turn lane. Base = no LTL (AMF=1.0).
    Adding LTL on major approach: AMF ≈ 0.67 stop-control; 0.77 signalized."""
    if not has_ltl:
        return 1.0
    return 0.77 if is_signalized else 0.67


def amf_sd(has_deficiency_existing: bool, has_deficiency_new: bool) -> float:
    """AMF for intersection sight distance.
    Base = no deficiency (AMF=1.0). With deficiency: AMF ≈ 1.42.
    So relative AMF = (new/existing)."""
    exist_amf = 1.42 if has_deficiency_existing else 1.0
    new_amf = 1.42 if has_deficiency_new else 1.0
    return new_amf / exist_amf


# ---------------------------------------------------------------------------
# Intersection table (Banihashemi Table 3, p. 115)
# ---------------------------------------------------------------------------
# For each intersection and each combination (numbered 0, 1, 2, ...), we
# record: ADT1, ADT2, skew angle, traffic control, LTL, ISD deficiency,
# delay (vehicle-hours/year).
#
# Intersection type inference from Table 3:
#   Intersections 1, 2, 5, 6:  4-leg stop (existing minor-stop, alternatives
#                              include all-stop as option 2)
#   Intersections 3, 4:        4-leg stop → 4-leg signalized (one signal alt)
#   Intersection 7:            4-leg stop with ISD issue; skew improvement
#                              option; assume 4-leg stop throughout
#   Intersection 8:            4-leg stop (minor-stop → all-stop only)
#   Intersection 9:            4-leg stop (like 1,2,5,6 pattern)
#   Intersection 10:           4-leg signalized (existing signalized)
#   Intersection 11:           4-leg stop (minor → all-stop only option)
#   Intersection 12:           4-leg stop (skew + LTL options)
#   Intersection 13:           4-leg stop (skew + LTL + ISD options)

INTERSECTIONS = {
    1: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            # (combo_id, skew, control, ltl, isd_deficiency, delay_hr_yr, cost)
            (0, 4.75, "Minor stop", False, False, 3039,     0),       # existing
            (1, 4.75, "Minor stop", True,  False, 3039,     300_000), # + LTL
            (2, 4.75, "All stop",   False, False, 14852,    0),       # all-stop
            (3, 4.75, "All stop",   True,  False, 9151,     300_000), # all-stop + LTL
        ],
    },
    2: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            (0, 0.00, "Minor stop", False, False, 3039,     0),
            (1, 0.00, "Minor stop", True,  False, 3039,     300_000),
            (2, 0.00, "All stop",   False, False, 14852,    0),
            (3, 0.00, "All stop",   True,  False, 9151,     300_000),
        ],
    },
    3: {
        "type": "4leg_stop",  # signalized alternative = treated as type change
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            (0, 9.00, "Minor stop",  False, False, 6078,     0),
            (1, 9.00, "Signalized",  False, False, 98165,    0),   # control change; signal cost negligible per paper
        ],
    },
    4: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            (0, 3.77, "Minor stop",  False, False, 6078,     0),
            (1, 3.77, "Signalized",  False, False, 72450,    0),
        ],
    },
    5: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            (0, 4.11, "Minor stop", False, False, 3039,     0),
            (1, 4.11, "Minor stop", True,  False, 3039,     400_000),  # cost = $400k for int 5,6
            (2, 4.11, "All stop",   False, False, 14852,    0),
            (3, 4.11, "All stop",   True,  False, 9151,     400_000),
        ],
    },
    6: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 2500,
        "combinations": [
            (0, 1.89, "Minor stop", False, False, 3039,     0),
            (1, 1.89, "Minor stop", True,  False, 3039,     400_000),
            (2, 1.89, "All stop",   False, False, 14852,    0),
            (3, 1.89, "All stop",   True,  False, 9151,     400_000),
        ],
    },
    7: {
        "type": "4leg_stop",
        "adt1": 7100, "adt2": 5000,
        "combinations": [
            (0, 43.14, "Minor stop", False, True,  67698,    0),          # existing: high skew + ISD
            (1, 43.14, "Minor stop", False, False, 67698,    500_000),    # remove ISD (note: cost $500k per paper)
            (2, 0.00,  "Minor stop", False, True,  67698,    600_000),    # remove skew
            (3, 0.00,  "Minor stop", False, False, 67698,    1_100_000),  # remove both (skew + ISD)
        ],
    },
    8: {
        "type": "4leg_stop",
        "adt1": 9000, "adt2": 2500,
        "combinations": [
            (0, 23.25, "Minor stop", False, False, 5438,     0),
            (1, 23.25, "All stop",   False, False, 66412,    0),
        ],
    },
    9: {
        "type": "4leg_stop",
        "adt1": 9000, "adt2": 2500,
        "combinations": [
            (0, 6.75, "Minor stop", False, False, 5438,     0),
            (1, 6.75, "Minor stop", True,  False, 5438,     600_000),  # LTL cost $600k for int 9
            (2, 6.75, "All stop",   False, False, 66412,    0),
            (3, 6.75, "All stop",   True,  False, 21645,    600_000),
        ],
    },
    10: {
        "type": "4leg_signal",
        "adt1": 7975, "adt2": 2500,
        "combinations": [
            (0, 13.25, "Signalized", False, False, 81607,    0),
            (1, 13.25, "Signalized", True,  False, 83030,    600_000),  # LTL on signal $600k
        ],
    },
    11: {
        "type": "4leg_stop",
        "adt1": 6950, "adt2": 2500,
        "combinations": [
            (0, 17.50, "Minor stop", False, False, 2935,     0),
            (1, 17.50, "All stop",   False, False, 8994,     0),
        ],
    },
    12: {
        "type": "4leg_stop",
        "adt1": 6950, "adt2": 2500,
        "combinations": [
            (0, 7.00, "Minor stop", False, False, 5870,     0),
            (1, 7.00, "Minor stop", True,  False, 5870,     100_000),   # LTL $100k for int 12
            (2, 0.00, "Minor stop", False, False, 5870,     600_000),   # skew $600k for int 12
            (3, 0.00, "Minor stop", True,  False, 5870,     700_000),   # both
        ],
    },
    13: {
        "type": "4leg_stop",
        "adt1": 6950, "adt2": 2500,
        "combinations": [
            (0, 8.00, "Minor stop", False, True,  5870,     0),          # existing: skew + ISD
            (1, 8.00, "Minor stop", False, False, 5870,     600_000),    # remove ISD
            (2, 8.00, "Minor stop", True,  True,  5870,     600_000),    # LTL (int 13 LTL $600k)
            (3, 0.00, "Minor stop", True,  True,  5870,     1_200_000),  # remove skew + LTL
            (4, 8.00, "Minor stop", True,  False, 5870,     1_200_000),  # LTL + remove ISD
        ],
    },
}


def build_alternatives_dataframe() -> pd.DataFrame:
    """Build a DataFrame of intersection alternatives suitable for the MCBOMs
    optimizer: columns site_id, alt_id, total_cost, total_benefit.
    
    Benefit = reduction in (crash + delay) cost over 20 years vs do-nothing.
    For a MINIMIZATION-of-total-cost framing, we need to convert to MCBOMs
    maximization-of-benefit-minus-cost. Benefit = (existing_total_cost -
    alternative_total_cost).
    """
    rows = []
    for site_id, data in INTERSECTIONS.items():
        int_type = data["type"]
        adt1, adt2 = data["adt1"], data["adt2"]
        
        # Baseline (existing) combination is combo_id 0
        existing = data["combinations"][0]
        _, skew_e, control_e, ltl_e, isd_e, delay_e, _ = existing
        
        # Compute base AMF product for existing
        amf_e = (amf_skew(skew_e, int_type)
                 * amf_traffic_control(control_e, control_e)  # 1.0 since same
                 * amf_ltl(ltl_e, "signal" in int_type)
                 * amf_sd(isd_e, isd_e))  # 1.0 since same
        # Expected crashes per year for existing
        crashes_e = cpm_crashes(int_type, adt1, adt2, amf_e)
        crash_cost_e_annual = crashes_e * INT_CPM[int_type]["crash_cost"]
        delay_cost_e_annual = delay_e * UNIT_DELAY_COST
        total_cost_existing_annual = crash_cost_e_annual + delay_cost_e_annual
        total_cost_existing_20yr = total_cost_existing_annual * PROJECT_LIFETIME
        
        for combo in data["combinations"]:
            alt_id, skew, control, ltl, isd, delay, improvement_cost = combo
            
            # Compute AMF product relative to BASE condition (IHSDM base
            # conditions: skew=0, two-way stop, no LTL, no ISD deficiency).
            # Here we compute absolute AMFs (vs base), then the CPM gives
            # actual expected crashes.
            # But for intersection type stays the same (4-leg stop or signal),
            # we use type-appropriate base models.
            #
            # When control changes (e.g., stop → signalized), we switch CPM
            # type between baseline and this alternative.
            
            # Determine effective type for THIS alternative
            if control == "Signalized":
                eff_type = "4leg_signal"
            else:
                eff_type = "4leg_stop"  # covers minor-stop and all-stop
            
            # Compute AMFs for this alternative (vs base conditions: skew=0,
            # minor-stop, no LTL, no ISD deficiency)
            amf_skew_a = amf_skew(skew, eff_type)
            # Traffic control: base is minor-stop, so if this alt is all-stop
            # we apply the transition AMF; for signalized type the "base" is
            # already signalized
            if eff_type == "4leg_stop":
                if control == "All stop":
                    amf_tc = amf_traffic_control("Minor stop", "All stop")
                else:
                    amf_tc = 1.0
            else:
                amf_tc = 1.0  # signal is its own base
            amf_ltl_a = amf_ltl(ltl, "signal" in eff_type)
            amf_sd_a = 1.42 if isd else 1.0
            
            amf_product_a = amf_skew_a * amf_tc * amf_ltl_a * amf_sd_a
            
            crashes_a = cpm_crashes(eff_type, adt1, adt2, amf_product_a)
            crash_cost_a_annual = crashes_a * INT_CPM[eff_type]["crash_cost"]
            delay_cost_a_annual = delay * UNIT_DELAY_COST
            total_cost_a_annual = crash_cost_a_annual + delay_cost_a_annual
            total_cost_a_20yr = total_cost_a_annual * PROJECT_LIFETIME
            
            # For MCBOMs framework (maximize Σ (B - C) x), benefit of choosing
            # this alternative vs existing is the AVOIDED crash+delay cost
            benefit = total_cost_existing_20yr - total_cost_a_20yr
            cost = improvement_cost
            
            rows.append({
                "site_id": site_id,
                "alt_id": alt_id,
                "description": f"Int {site_id} combo {alt_id}",
                "int_type": eff_type,
                "skew_deg": skew,
                "control": control,
                "ltl": ltl,
                "isd_deficiency": isd,
                "delay_hr_yr": delay,
                "crashes_per_year": crashes_a,
                "crash_cost_20yr": crash_cost_a_annual * PROJECT_LIFETIME,
                "delay_cost_20yr": delay_cost_a_annual * PROJECT_LIFETIME,
                "total_cost_20yr": total_cost_a_20yr,
                "improvement_cost": cost,
                "total_benefit": benefit,  # MCBOMs benefit
                "total_cost": cost,        # MCBOMs cost (improvement cost only)
            })
    
    return pd.DataFrame(rows)
