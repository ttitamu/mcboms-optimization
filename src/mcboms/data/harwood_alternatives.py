"""
Harwood (2003) Alternatives Data - EXACT VALUES FROM PAPER

This module contains the data published in Harwood et al. (2003)
Tables 2 and 3, which give per-site cost and benefit values for the
10-site case study.

Harwood's Net Benefit Formula (paper's Equation 3):

  NBjk = PSBjk + PTOBjk + PNRjk - PRPjk - CCjk

Where:
  PSBjk  = Present value of safety benefits (from AMFs)      -> `safety_benefit`
  PTOBjk = Present value of travel time benefits             -> `ops_benefit`
  PNRjk  = Penalty for Not Resurfacing (do-nothing penalty)  -> `pnr_benefit`  [DISABLED]
  PRPjk  = Penalty for Resurfacing w/o safety improvements   -> `prp_penalty`  [DISABLED]
  CCjk   = Construction cost (safety improvement cost)       -> `safety_improvement_cost`

PNR/PRP ARE DISABLED IN THE PROTOTYPE (set to zero). Rationale, per the
MCBOMs Mathematical Formulation Specification, Section 7.3:

  - Per-site PNR values are NOT published in Harwood (2003). The paper
    reports only aggregate PNR ($5,576,145 across deferred sites 4, 6,
    9 in the $10M case) and the qualitative formula (a percentage of
    pavement-failure replacement cost). Calibrating per-site PNR values
    that reproduce Harwood's $10M solution is reverse-engineering, not
    validation.

  - The PNR formula requires per-site pavement condition and time-to-
    failure data not standardized in any current FHWA guidance and not
    present in our case study inputs.

  - Banihashemi (2007), our second benchmark, also does not use a
    deferral-penalty mechanism.

Consequence: MCBOMs reproduces Harwood's $50M case exactly (PNR doesn't
bind there) and finds a strictly net-benefit-superior solution at the
$10M budget because we don't penalize deferral of low-benefit sites.
Agencies wishing to incorporate pavement-deferral cost can add it to
the do-nothing alternative's cost term directly.

Reference:
  Harwood, D.W., Rabbani, E.R.K., and Richard, K.R. (2003).
  Systemwide Optimization of Safety Improvements for Resurfacing,
  Restoration, or Rehabilitation Projects.
  Transportation Research Record 1840, pp. 148-157.
"""

import pandas as pd


# =============================================================================
# PENALTY TERMS -- DISABLED IN PROTOTYPE
# =============================================================================
# See module docstring for rationale. The keys are kept for schema
# stability, but all values are zero. If a future revision adds a
# principled PNR/PRP mechanism (e.g., from HSIP pavement-condition data),
# these dictionaries are the correct place to wire it in.

PNR_BY_SITE = {i: 0 for i in range(1, 11)}  # All zero -- PNR disabled per spec 7.3
PRP_BY_SITE = {i: 0 for i in range(1, 11)}  # All zero -- PRP disabled per spec 7.3


def get_harwood_alternatives() -> pd.DataFrame:
    """
    Get Harwood alternatives with EXACT values from Tables 2 and 3,
    plus penalty terms (PNR, PRP) from the Harwood formulation.
    
    Returns DataFrame with columns:
        site_id, alt_id, description, resurfacing_cost, safety_improvement_cost,
        safety_benefit, ops_benefit, pnr_benefit, prp_penalty,
        total_cost, total_benefit, net_benefit
    """
    
    alternatives = []
    
    # =========================================================================
    # SITE 1: Rural 2-lane, 9ft lanes, 2ft turf shoulders
    # Table 2 & Table 3: Resurface only
    # PNR applies to do-nothing, PRP applies to resurface-only (no safety improvements)
    # =========================================================================
    # Alt 0: Do nothing - gets PNR penalty (as benefit to make do-nothing worse)
    alternatives.append({
        "site_id": 1, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[1],  # Negative = penalty for not resurfacing
        "prp_penalty": 0,
    })
    # Alt 1: Resurface only (from Table 2) - gets PRP penalty (narrow lanes/shoulders)
    alternatives.append({
        "site_id": 1, "alt_id": 1, 
        "description": "Resurface only",
        "resurfacing_cost": 528803, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 35107,
        "pnr_benefit": 0,
        "prp_penalty": PRP_BY_SITE.get(1, 0),  # PRP for resurfacing without safety improvements
    })
    
    # =========================================================================
    # SITE 2: Rural 2-lane, 10ft lanes, 4ft composite shoulders
    # Table 2 & Table 3: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.append({
        "site_id": 2, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[2],
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 2, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 519763, 
        "safety_improvement_cost": 120000,
        "safety_benefit": 328176, 
        "ops_benefit": 71580,
        "pnr_benefit": 0,
        "prp_penalty": 0,  # Has safety improvements, no PRP
    })
    
    # =========================================================================
    # SITE 3: Rural 2-lane, 11ft lanes, 4ft paved shoulders
    # Table 2 & Table 3: Resurface + Turn-lane + Roadside + User-defined #2
    # =========================================================================
    alternatives.append({
        "site_id": 3, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[3],
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 3, "alt_id": 1, 
        "description": "Resurface + Turn-lane + Roadside + User-defined #2",
        "resurfacing_cost": 821621, 
        "safety_improvement_cost": 560000,
        "safety_benefit": 1094909, 
        "ops_benefit": 93697,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 4: Urban 2-lane divided, 10ft lanes, 4ft paved shoulders
    # Table 2: Resurface + Lane widen (10→11) + Shoulder widen (4→6)
    # Table 3: DO NOTHING
    # =========================================================================
    alternatives.append({
        "site_id": 4, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[4],  # Lower penalty - can be skipped
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 4, "alt_id": 1, 
        "description": "Resurface + Widen lanes 10-11ft + Widen shoulders 4-6ft",
        "resurfacing_cost": 475200, 
        "safety_improvement_cost": 572616,
        "safety_benefit": 775629, 
        "ops_benefit": 58379,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 5: Rural 4-lane undivided, 10ft lanes, 4ft gravel shoulders
    # Table 2 & Table 3: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.append({
        "site_id": 5, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[5],
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 5, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 1180017, 
        "safety_improvement_cost": 240000,
        "safety_benefit": 1355589, 
        "ops_benefit": 53029,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 6: Urban 4-lane undivided, 11ft lanes, 6ft paved shoulders
    # Table 2: Resurface + Turn-lane improvements
    # Table 3: DO NOTHING
    # =========================================================================
    alternatives.append({
        "site_id": 6, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[6],  # Lower penalty - can be skipped
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 6, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 2508549, 
        "safety_improvement_cost": 560000,
        "safety_benefit": 808637, 
        "ops_benefit": 92800,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 7: Rural 4-lane divided, 11ft lanes, 4ft paved shoulders
    # Table 2 & Table 3: Resurface + Turn-lane improvements
    # =========================================================================
    alternatives.append({
        "site_id": 7, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[7],
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 7, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 1503237, 
        "safety_improvement_cost": 360000,
        "safety_benefit": 947234, 
        "ops_benefit": 93407,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 8: Rural 4-lane divided, 12ft lanes, 8ft paved shoulders
    # Table 2: Resurface + Turn-lane + User-defined #2 (safety cost $680,000)
    # Table 3: Resurface + Turn-lane ONLY (safety cost $180,000) - DIFFERENT!
    # =========================================================================
    alternatives.append({
        "site_id": 8, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[8],
        "prp_penalty": 0,
    })
    # Alt 1: Turn-lane only (selected at $10M) - from Table 3
    alternatives.append({
        "site_id": 8, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 1398989, 
        "safety_improvement_cost": 180000,
        "safety_benefit": 555526, 
        "ops_benefit": 150118,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    # Alt 2: Turn-lane + User-defined #2 (selected at $50M) - from Table 2
    alternatives.append({
        "site_id": 8, "alt_id": 2, 
        "description": "Resurface + Turn-lane + User-defined #2",
        "resurfacing_cost": 1398989, 
        "safety_improvement_cost": 680000,
        "safety_benefit": 1119938, 
        "ops_benefit": 150118,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 9: Urban 4-lane undivided, 10ft lanes, 2ft paved shoulders
    # Table 2: Resurface + Turn-lane improvements
    # Table 3: DO NOTHING
    # =========================================================================
    alternatives.append({
        "site_id": 9, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[9],  # Lower penalty - can be skipped
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 9, "alt_id": 1, 
        "description": "Resurface + Turn-lane improvements",
        "resurfacing_cost": 1365302, 
        "safety_improvement_cost": 336000,
        "safety_benefit": 1071895, 
        "ops_benefit": 81343,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # SITE 10: Urban 6-lane divided, 11ft lanes, 4ft paved shoulders
    # Table 2 & Table 3: Resurface + Shoulder widen + Horiz curve + Turn-lane
    # =========================================================================
    alternatives.append({
        "site_id": 10, "alt_id": 0, 
        "description": "Do nothing",
        "resurfacing_cost": 0, 
        "safety_improvement_cost": 0,
        "safety_benefit": 0, 
        "ops_benefit": 0,
        "pnr_benefit": -PNR_BY_SITE[10],
        "prp_penalty": 0,
    })
    alternatives.append({
        "site_id": 10, "alt_id": 1, 
        "description": "Resurface + Widen shoulders 4-6ft + Horiz curve + Turn-lane",
        "resurfacing_cost": 1488369, 
        "safety_improvement_cost": 1052781,
        "safety_benefit": 2329256, 
        "ops_benefit": 80186,
        "pnr_benefit": 0,
        "prp_penalty": 0,
    })
    
    # =========================================================================
    # Convert to DataFrame and calculate derived columns
    # =========================================================================
    df = pd.DataFrame(alternatives)
    
    # Total cost = resurfacing + safety improvement (used in budget constraint)
    df["total_cost"] = df["resurfacing_cost"] + df["safety_improvement_cost"]
    
    # Total benefit (reported) = safety benefit + operations benefit (excludes penalties)
    df["total_benefit"] = df["safety_benefit"] + df["ops_benefit"]
    
    # Net benefit (reported) = total_benefit - safety_improvement_cost
    # This is what gets reported in Table 4 as "Net Benefits"
    df["net_benefit"] = df["total_benefit"] - df["safety_improvement_cost"]
    
    # Objective value (for optimization) = includes penalty terms
    # NBjk = PSBjk + PTOBjk + PNRjk - PRPjk - CCjk
    # PNR: penalty for not resurfacing (negative for do-nothing, makes it less attractive)
    # PRP: penalty for resurfacing without safety improvements (subtracted)
    df["objective_value"] = (
        df["safety_benefit"] + 
        df["ops_benefit"] + 
        df["pnr_benefit"] -  # pnr_benefit is negative for do-nothing
        df["prp_penalty"] - 
        df["safety_improvement_cost"]
    )
    
    return df


def get_expected_solution_50m() -> dict:
    """
    Expected optimal solution for $50M budget (Table 2).
    All sites receive improvements (unconstrained budget).
    """
    return {
        "budget": 50_000_000,
        "selected_alternatives": {
            1: 1,   # Resurface only
            2: 1,   # Resurface + Turn-lane
            3: 1,   # Resurface + Turn-lane + Roadside + User#2
            4: 1,   # Resurface + Lane widen + Shoulder widen
            5: 1,   # Resurface + Turn-lane
            6: 1,   # Resurface + Turn-lane
            7: 1,   # Resurface + Turn-lane
            8: 2,   # Resurface + Turn-lane + User#2 (alt_id=2)
            9: 1,   # Resurface + Turn-lane
            10: 1,  # Resurface + Shoulder + Curve + Turn-lane
        },
        "total_resurfacing_cost": 11_789_849,
        "total_safety_cost": 4_481_397,
        "total_cost": 16_271_246,  # 11,789,849 + 4,481,397
        "total_safety_benefit": 9_831_263,
        "total_ops_benefit": 809_651,
        "total_benefit": 10_640_914,
        "net_benefit": 6_159_517,  # 10,640,914 - 4,481,397
        "do_nothing_sites": [],
    }


def get_expected_solution_10m() -> dict:
    """
    Expected optimal solution for $10M budget (Table 3).
    Sites 4, 6, 9 receive do-nothing. Site 8 gets smaller improvement.
    """
    return {
        "budget": 10_000_000,
        "selected_alternatives": {
            1: 1,   # Resurface only
            2: 1,   # Resurface + Turn-lane
            3: 1,   # Resurface + Turn-lane + Roadside + User#2
            4: 0,   # DO NOTHING
            5: 1,   # Resurface + Turn-lane
            6: 0,   # DO NOTHING
            7: 1,   # Resurface + Turn-lane
            8: 1,   # Resurface + Turn-lane ONLY (alt_id=1, NOT alt_id=2)
            9: 0,   # DO NOTHING
            10: 1,  # Resurface + Shoulder + Curve + Turn-lane
        },
        "total_resurfacing_cost": 7_440_798,
        "total_safety_cost": 2_512_781,
        "total_cost": 9_953_579,  # 7,440,798 + 2,512,781
        "total_safety_benefit": 6_610_690,
        "total_ops_benefit": 577_124,
        "total_benefit": 7_187_814,
        "net_benefit": 4_675_033,  # 7,187,814 - 2,512,781
        "do_nothing_sites": [4, 6, 9],
    }


def verify_data_integrity():
    """Verify the data matches Harwood's published totals."""
    df = get_harwood_alternatives()
    exp_50m = get_expected_solution_50m()
    exp_10m = get_expected_solution_10m()
    
    print("DATA INTEGRITY CHECK")
    print("=" * 60)
    
    # Check $50M totals
    selected_50m = []
    for site_id, alt_id in exp_50m["selected_alternatives"].items():
        row = df[(df["site_id"] == site_id) & (df["alt_id"] == alt_id)].iloc[0]
        selected_50m.append(row)
    
    df_50m = pd.DataFrame(selected_50m)
    
    print("\n$50M Budget Verification:")
    print(f"  Resurfacing cost: ${df_50m['resurfacing_cost'].sum():,.0f} (expected ${exp_50m['total_resurfacing_cost']:,})")
    print(f"  Safety cost:      ${df_50m['safety_improvement_cost'].sum():,.0f} (expected ${exp_50m['total_safety_cost']:,})")
    print(f"  Total cost:       ${df_50m['total_cost'].sum():,.0f} (expected ${exp_50m['total_cost']:,})")
    print(f"  Safety benefit:   ${df_50m['safety_benefit'].sum():,.0f} (expected ${exp_50m['total_safety_benefit']:,})")
    print(f"  Ops benefit:      ${df_50m['ops_benefit'].sum():,.0f} (expected ${exp_50m['total_ops_benefit']:,})")
    print(f"  Total benefit:    ${df_50m['total_benefit'].sum():,.0f} (expected ${exp_50m['total_benefit']:,})")
    
    # Check $10M totals
    selected_10m = []
    for site_id, alt_id in exp_10m["selected_alternatives"].items():
        row = df[(df["site_id"] == site_id) & (df["alt_id"] == alt_id)].iloc[0]
        selected_10m.append(row)
    
    df_10m = pd.DataFrame(selected_10m)
    
    print("\n$10M Budget Verification:")
    print(f"  Resurfacing cost: ${df_10m['resurfacing_cost'].sum():,.0f} (expected ${exp_10m['total_resurfacing_cost']:,})")
    print(f"  Safety cost:      ${df_10m['safety_improvement_cost'].sum():,.0f} (expected ${exp_10m['total_safety_cost']:,})")
    print(f"  Total cost:       ${df_10m['total_cost'].sum():,.0f} (expected ${exp_10m['total_cost']:,})")
    print(f"  Safety benefit:   ${df_10m['safety_benefit'].sum():,.0f} (expected ${exp_10m['total_safety_benefit']:,})")
    print(f"  Ops benefit:      ${df_10m['ops_benefit'].sum():,.0f} (expected ${exp_10m['total_ops_benefit']:,})")
    print(f"  Total benefit:    ${df_10m['total_benefit'].sum():,.0f} (expected ${exp_10m['total_benefit']:,})")


if __name__ == "__main__":
    verify_data_integrity()
