"""
Corridor Condition Benefit Calculation Module for MCBOMs.

Implements Eq 2.27 of the MCBOMs Methodology document.

Core formulation (Eq 2.27):

    B_ij(corridor) = sum_c sum_t [ delta_Q_c,t * V_c * DF_t ]

Where:
    c           = CCM category (energy, emissions, mobility/access, resilience)
    t           = analysis year
    delta_Q_c,t = change in CCM quantity in year t for category c
    V_c         = unit value for category c
    DF_t        = discount factor for year t

This module organizes the CCM categories into separate functions, then
provides a top-level aggregator. Each category has its own monetization
logic and unit-value source.

The framework enforces explicit double-counting prevention with
operations.py — when both modules are called for the same project,
the user must declare via a flag that they have handled the overlap.
This is because the MEP (Mobility Energy Productivity) component of
CCM has travel-time elements that overlap with operational benefits.

References:
    - USDOT (2025). BCA Guidance for Discretionary Grant Programs, May 2025.
    - FEMA Standard Economic Values v13 (2024).
    - EPA Social Cost of Carbon (current values).
    - MCBOMs Methodology document, Section 2.5.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd

from mcboms.utils.economics import calculate_present_worth_factor as calculate_pwf
from mcboms.utils.economics import calculate_discount_factors

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Default unit values (2023 dollars unless noted)
# ---------------------------------------------------------------------

# Energy: per-kWh value reflects damages avoided. Wide range in literature;
# we use a conservative residential-supply equivalent.
DEFAULT_ENERGY_VALUE_PER_KWH = 0.12         # $/kWh

# Emissions: EPA Social Cost of Carbon, 3% discount rate central estimate
# for 2025 (USDOT BCA May 2025 Section 4.5).
DEFAULT_SCC_PER_TON_CO2 = 224.0             # $/metric-ton CO2-equivalent

# Mobility / accessibility: per-trip value (USDOT BCA May 2025 Table A-2,
# applies VOT to person-trips). Conservative single-trip equivalent.
DEFAULT_ACCESSIBILITY_VALUE_PER_TRIP = 12.0  # $/person-trip

# Resilience: avoided-damages dollar value used as the input directly
# (no per-event multiplier). FEMA Standard Economic Values v13 are
# applied externally; this module just sums the dollar values.

# Pavement / asset condition: $/lane-mile-year for IRI-based serviceability
# improvement. Wide variation by agency; default is illustrative only.
DEFAULT_PAVEMENT_VALUE_PER_LANE_MILE_YEAR = 5_000.0  # $/lane-mile/year


# ---------------------------------------------------------------------
# Per-category benefit functions (the building blocks of Eq 2.27)
# ---------------------------------------------------------------------

def compute_energy_benefit(
    annual_kwh_saved: float,
    value_per_kwh: float = DEFAULT_ENERGY_VALUE_PER_KWH,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value energy benefit (Eq 2.27, energy category).
    
    Annual benefit = annual_kwh_saved * value_per_kwh
    PV = annual benefit * PWF(r, T)
    
    Args:
        annual_kwh_saved: Annual electricity saved (kWh/year). Positive = benefit.
        value_per_kwh: Unit value ($/kWh). Default $0.12.
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Dict with 'annual_total', 'pwf', 'pv_total', 'category'.
    """
    if annual_kwh_saved < 0:
        raise ValueError(f"annual_kwh_saved must be non-negative; got {annual_kwh_saved}")
    if value_per_kwh < 0:
        raise ValueError(f"value_per_kwh must be non-negative; got {value_per_kwh}")
    
    annual = annual_kwh_saved * value_per_kwh
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    return {
        "category": "energy",
        "annual_total": annual,
        "pwf": pwf,
        "pv_total": annual * pwf,
    }


def compute_emissions_benefit(
    annual_co2_tons_avoided: float,
    scc_per_ton: float = DEFAULT_SCC_PER_TON_CO2,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value emissions benefit (Eq 2.27, emissions category).
    
    Annual benefit = annual_co2_tons_avoided * scc_per_ton
    PV = annual benefit * PWF(r, T)
    
    Uses the EPA Social Cost of Carbon valuation.
    
    Args:
        annual_co2_tons_avoided: Annual CO2-equivalent tons avoided. Positive = benefit.
        scc_per_ton: Social cost of carbon ($/metric-ton CO2-equivalent).
            Default $224 from USDOT BCA May 2025.
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Dict with 'annual_total', 'pwf', 'pv_total', 'category'.
    """
    if annual_co2_tons_avoided < 0:
        raise ValueError(
            f"annual_co2_tons_avoided must be non-negative; got {annual_co2_tons_avoided}"
        )
    if scc_per_ton < 0:
        raise ValueError(f"scc_per_ton must be non-negative; got {scc_per_ton}")
    
    annual = annual_co2_tons_avoided * scc_per_ton
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    return {
        "category": "emissions",
        "annual_total": annual,
        "pwf": pwf,
        "pv_total": annual * pwf,
    }


def compute_accessibility_benefit(
    annual_trips_enabled: float,
    value_per_trip: float = DEFAULT_ACCESSIBILITY_VALUE_PER_TRIP,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value accessibility benefit (Eq 2.27, mobility category).
    
    NOTE: This is the category that overlaps with operations.py. If you
    are also computing operational benefit (Eq 2.21) for the same project,
    you must explicitly handle the overlap before aggregating. Use
    compute_corridor_benefit() with handle_overlap=True if both are present.
    
    Annual benefit = annual_trips_enabled * value_per_trip
    PV = annual benefit * PWF(r, T)
    
    Args:
        annual_trips_enabled: Additional person-trips enabled per year by the
            improvement. Positive = benefit.
        value_per_trip: Unit value ($/person-trip). Default $12.
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Dict with 'annual_total', 'pwf', 'pv_total', 'category'.
    """
    if annual_trips_enabled < 0:
        raise ValueError(
            f"annual_trips_enabled must be non-negative; got {annual_trips_enabled}"
        )
    if value_per_trip < 0:
        raise ValueError(f"value_per_trip must be non-negative; got {value_per_trip}")
    
    annual = annual_trips_enabled * value_per_trip
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    return {
        "category": "accessibility",
        "annual_total": annual,
        "pwf": pwf,
        "pv_total": annual * pwf,
    }


def compute_resilience_benefit(
    expected_avoided_damages: float,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value resilience benefit (Eq 2.27, resilience category).
    
    Resilience benefits are typically computed externally as expected-value
    avoided damages (probability of disaster event * cost of damages avoided).
    The FEMA Standard Economic Values v13 (2024) provide guidance on
    monetizing physical damages, casualties, and service disruption.
    
    This function takes the expected-value avoided damages as a single
    annualized dollar amount and converts to present value via PWF.
    
    Args:
        expected_avoided_damages: Annual expected-value avoided damages ($).
            Positive = benefit.
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Dict with 'annual_total', 'pwf', 'pv_total', 'category'.
    """
    if expected_avoided_damages < 0:
        raise ValueError(
            f"expected_avoided_damages must be non-negative; got {expected_avoided_damages}"
        )
    
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    return {
        "category": "resilience",
        "annual_total": expected_avoided_damages,
        "pwf": pwf,
        "pv_total": expected_avoided_damages * pwf,
    }


def compute_pavement_benefit(
    lane_miles: float,
    annual_value_per_lane_mile: float = DEFAULT_PAVEMENT_VALUE_PER_LANE_MILE_YEAR,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value pavement / asset condition benefit.
    
    Annual benefit = lane_miles * annual_value_per_lane_mile
    PV = annual benefit * PWF(r, T)
    
    Args:
        lane_miles: Lane-miles of improved pavement.
        annual_value_per_lane_mile: Per-lane-mile-per-year value ($).
            Default $5,000 (illustrative; agencies should use local values).
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Dict with 'annual_total', 'pwf', 'pv_total', 'category'.
    """
    if lane_miles < 0:
        raise ValueError(f"lane_miles must be non-negative; got {lane_miles}")
    if annual_value_per_lane_mile < 0:
        raise ValueError(
            f"annual_value_per_lane_mile must be non-negative; "
            f"got {annual_value_per_lane_mile}"
        )
    
    annual = lane_miles * annual_value_per_lane_mile
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    return {
        "category": "pavement",
        "annual_total": annual,
        "pwf": pwf,
        "pv_total": annual * pwf,
    }


# ---------------------------------------------------------------------
# Aggregator with double-counting prevention
# ---------------------------------------------------------------------

@dataclass
class CCMInputs:
    """Inputs for the corridor condition benefit (Eq 2.27) for one alternative.
    
    Each field is optional; categories with None/0 contribute zero benefit
    and are silently omitted from the aggregation.
    
    Attributes:
        energy_annual_kwh_saved: Annual electricity saved (kWh).
        emissions_annual_co2_tons_avoided: Annual CO2-equivalent tons avoided.
        accessibility_annual_trips_enabled: Additional person-trips per year.
            NOTE: overlaps with operational benefits — see warning below.
        resilience_expected_avoided_damages: Annualized expected-value avoided
            damages ($).
        pavement_lane_miles: Lane-miles of pavement improvement.
        accessibility_overlaps_with_operations: If True, the user has
            confirmed they understand the overlap between accessibility
            and operations.py (Eq 2.21) and have handled it (e.g., by
            computing operational benefit only OR accessibility, not both
            for the same trips).
            If both modules are used for the same project and this flag is
            False, compute_corridor_benefit() raises ValueError.
    """
    energy_annual_kwh_saved: float = 0.0
    emissions_annual_co2_tons_avoided: float = 0.0
    accessibility_annual_trips_enabled: float = 0.0
    resilience_expected_avoided_damages: float = 0.0
    pavement_lane_miles: float = 0.0
    accessibility_overlaps_with_operations: bool = False


def compute_corridor_benefit(
    inputs: CCMInputs,
    operations_already_computed: bool = False,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
    energy_value_per_kwh: float = DEFAULT_ENERGY_VALUE_PER_KWH,
    scc_per_ton: float = DEFAULT_SCC_PER_TON_CO2,
    value_per_trip: float = DEFAULT_ACCESSIBILITY_VALUE_PER_TRIP,
    pavement_value_per_lane_mile_year: float = DEFAULT_PAVEMENT_VALUE_PER_LANE_MILE_YEAR,
) -> dict[str, float]:
    """Compute total present-value corridor condition benefit (Eq 2.27).
    
    Aggregates across all CCM categories. Enforces double-counting
    prevention against operations.py (Eq 2.21) for the accessibility
    category.
    
    Double-counting check: if operations_already_computed=True AND
    inputs.accessibility_annual_trips_enabled > 0, the function will
    raise unless inputs.accessibility_overlaps_with_operations=True
    (the user has explicitly confirmed they handled the overlap).
    
    Args:
        inputs: CCMInputs with quantities for each category.
        operations_already_computed: True if operations.py (Eq 2.21) has
            also been computed for this same project.
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
        energy_value_per_kwh, scc_per_ton, value_per_trip,
        pavement_value_per_lane_mile_year: Override default unit values.
    
    Returns:
        Dict with:
            - 'by_category': dict mapping category name to its full result dict
            - 'annual_total': sum of annual benefits across categories
            - 'pv_total': sum of PV benefits across categories
            - 'pwf': common PWF used
    
    Raises:
        ValueError: If accessibility is non-zero AND operations is also
            being computed AND the user has not confirmed overlap handling.
    
    Example:
        >>> inputs = CCMInputs(
        ...     energy_annual_kwh_saved=50_000,
        ...     emissions_annual_co2_tons_avoided=200,
        ... )
        >>> result = compute_corridor_benefit(inputs)
        >>> result['pv_total'] > 0
        True
    """
    # Double-counting check: accessibility vs operations
    if (
        operations_already_computed
        and inputs.accessibility_annual_trips_enabled > 0
        and not inputs.accessibility_overlaps_with_operations
    ):
        raise ValueError(
            "Double-counting risk: operations.py (Eq 2.21) is being computed "
            "and accessibility CCM (Eq 2.27 mobility category) has non-zero "
            "annual trips. These can overlap because Eq 2.21 already monetizes "
            "travel-time savings for trips that already occur, and accessibility "
            "monetizes additional trips enabled by the improvement. To proceed, "
            "either: (a) verify that operations.py inputs cover only existing "
            "trips and accessibility inputs cover only NEW trips, then set "
            "inputs.accessibility_overlaps_with_operations=True; or (b) zero "
            "out one of the two modules. See MCBOMs Methodology Section 2.5.4."
        )
    
    by_category = {}
    annual_total = 0.0
    pv_total = 0.0
    
    if inputs.energy_annual_kwh_saved > 0:
        r = compute_energy_benefit(
            inputs.energy_annual_kwh_saved,
            value_per_kwh=energy_value_per_kwh,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        by_category["energy"] = r
        annual_total += r["annual_total"]
        pv_total += r["pv_total"]
    
    if inputs.emissions_annual_co2_tons_avoided > 0:
        r = compute_emissions_benefit(
            inputs.emissions_annual_co2_tons_avoided,
            scc_per_ton=scc_per_ton,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        by_category["emissions"] = r
        annual_total += r["annual_total"]
        pv_total += r["pv_total"]
    
    if inputs.accessibility_annual_trips_enabled > 0:
        r = compute_accessibility_benefit(
            inputs.accessibility_annual_trips_enabled,
            value_per_trip=value_per_trip,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        by_category["accessibility"] = r
        annual_total += r["annual_total"]
        pv_total += r["pv_total"]
    
    if inputs.resilience_expected_avoided_damages > 0:
        r = compute_resilience_benefit(
            inputs.resilience_expected_avoided_damages,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        by_category["resilience"] = r
        annual_total += r["annual_total"]
        pv_total += r["pv_total"]
    
    if inputs.pavement_lane_miles > 0:
        r = compute_pavement_benefit(
            inputs.pavement_lane_miles,
            annual_value_per_lane_mile=pavement_value_per_lane_mile_year,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        by_category["pavement"] = r
        annual_total += r["annual_total"]
        pv_total += r["pv_total"]
    
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    
    return {
        "by_category": by_category,
        "annual_total": annual_total,
        "pv_total": pv_total,
        "pwf": pwf,
    }


# ---------------------------------------------------------------------
# DataFrame interface
# ---------------------------------------------------------------------

def compute_corridor_benefits_df(
    inputs_df: pd.DataFrame,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> pd.DataFrame:
    """Compute corridor benefits for many (site, alternative) pairs at once.
    
    Args:
        inputs_df: DataFrame with one row per (site_id, alt_id), columns:
            energy_annual_kwh_saved, emissions_annual_co2_tons_avoided,
            accessibility_annual_trips_enabled,
            resilience_expected_avoided_damages, pavement_lane_miles,
            and optionally accessibility_overlaps_with_operations,
            operations_also_computed (per row).
        discount_rate: Annual discount rate.
        analysis_horizon: Analysis period in years.
    
    Returns:
        DataFrame with columns: site_id, alt_id, annual_total, pv_total,
        plus per-category PV columns. One row per (site_id, alt_id).
    """
    required_cols = {"site_id", "alt_id"}
    missing = required_cols - set(inputs_df.columns)
    if missing:
        raise ValueError(f"inputs_df missing columns: {missing}")
    
    rows = []
    for _, row in inputs_df.iterrows():
        ccm_inputs = CCMInputs(
            energy_annual_kwh_saved=row.get("energy_annual_kwh_saved", 0.0),
            emissions_annual_co2_tons_avoided=row.get(
                "emissions_annual_co2_tons_avoided", 0.0),
            accessibility_annual_trips_enabled=row.get(
                "accessibility_annual_trips_enabled", 0.0),
            resilience_expected_avoided_damages=row.get(
                "resilience_expected_avoided_damages", 0.0),
            pavement_lane_miles=row.get("pavement_lane_miles", 0.0),
            accessibility_overlaps_with_operations=row.get(
                "accessibility_overlaps_with_operations", False),
        )
        ops_computed = row.get("operations_also_computed", False)
        result = compute_corridor_benefit(
            ccm_inputs,
            operations_already_computed=ops_computed,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        out_row = {
            "site_id": row["site_id"],
            "alt_id": row["alt_id"],
            "annual_total": result["annual_total"],
            "pv_total": result["pv_total"],
        }
        # Per-category columns
        for cat in ["energy", "emissions", "accessibility", "resilience", "pavement"]:
            cat_result = result["by_category"].get(cat, {})
            out_row[f"{cat}_pv"] = cat_result.get("pv_total", 0.0)
        rows.append(out_row)
    
    return pd.DataFrame(rows)
