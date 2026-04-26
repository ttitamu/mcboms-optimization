"""
Operational Benefit Calculation Module for MCBOMs.

Implements Eq 2.21 of the MCBOMs Methodology document.

Core formulation (Eq 2.21):

    B_ij(operations,t) = sum_v [ delta_d_v * AADT * 365 * OCC_v * VOT_v
                                + delta_VOC_v * VMT_v ]

Where:
    v          = vehicle class (e.g., passenger, truck)
    delta_d_v  = change in per-vehicle delay (hours/vehicle)
    AADT       = annual average daily traffic (vehicles/day)
    OCC_v      = average vehicle occupancy (persons/vehicle)
    VOT_v      = value of time ($/person-hour)
    delta_VOC_v= change in vehicle operating cost ($/vehicle-mile)
    VMT_v      = vehicle miles traveled per year for class v

The first term monetizes travel-time savings (per-vehicle delay reduction
times annual vehicles times occupancy times time-value).
The second term monetizes vehicle operating cost reductions.

Annual benefit is converted to present value via the standard PWF:

    B_ij(operations,PV) = B_ij(operations,year) * PWF(r, T)

Default unit values come from USDOT Benefit-Cost Analysis Guidance for
Discretionary Grant Programs (May 2025), Tables A-2 through A-4.

References:
    - USDOT (2025). BCA Guidance for Discretionary Grant Programs, May 2025.
    - MCBOMs Methodology document, Section 2.4.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from mcboms.utils.economics import calculate_present_worth_factor as calculate_pwf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# USDOT BCA May 2025 default values (2023 dollars unless noted)
# ---------------------------------------------------------------------

DEFAULT_VOT = {
    "all_purposes": 21.10,   # $/person-hour, USDOT BCA Table A-2
    "personal":     19.40,
    "business":     33.50,
}

DEFAULT_OCC = {
    "passenger":    1.52,    # persons/vehicle, USDOT BCA Table A-3
    "truck":        1.00,
}

DEFAULT_VOC = {
    "passenger":    0.56,    # $/vehicle-mile, USDOT BCA Table A-4
    "truck":        1.10,
}


# ---------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------

@dataclass
class VehicleClassInputs:
    """Per-vehicle-class operational benefit inputs (Eq 2.21).
    
    Represents the inputs for one vehicle class v in the operational
    benefit equation. Either or both of the travel-time and VOC components
    can be zero (e.g., a treatment that only changes operating cost has
    delta_d = 0; a treatment that only reduces delay has delta_voc = 0).
    
    Attributes:
        name: Human-readable class name (e.g., "passenger", "truck")
        delta_d: Change in per-vehicle delay (hours/vehicle).
            Positive = delay reduction (benefit). Negative = delay increase.
        aadt: Annual average daily traffic for this class (vehicles/day).
        occupancy: Average vehicle occupancy (persons/vehicle).
        vot: Value of time ($/person-hour).
        delta_voc: Change in vehicle operating cost ($/vehicle-mile).
            Positive = cost reduction (benefit).
        vmt: Annual vehicle miles traveled for this class.
    """
    name: str
    delta_d: float = 0.0
    aadt: float = 0.0
    occupancy: float = 1.0
    vot: float = 0.0
    delta_voc: float = 0.0
    vmt: float = 0.0


# ---------------------------------------------------------------------
# Component functions (the building blocks of Eq 2.21)
# ---------------------------------------------------------------------

def compute_travel_time_benefit(
    delta_d: float,
    aadt: float,
    occupancy: float,
    vot: float,
) -> float:
    """Compute the annual travel-time savings benefit for one vehicle class.
    
    First term of Eq 2.21:
    
        B_tt = delta_d * AADT * 365 * OCC * VOT
    
    Args:
        delta_d: Change in per-vehicle delay (hours/vehicle).
            Positive = delay reduction.
        aadt: Annual average daily traffic (vehicles/day).
        occupancy: Average vehicle occupancy (persons/vehicle).
        vot: Value of time ($/person-hour).
    
    Returns:
        Annual travel-time benefit in dollars per year.
    
    Example:
        >>> # 5-min average delay reduction, 10000 AADT, 1.52 occupancy, $21.10 VOT
        >>> compute_travel_time_benefit(
        ...     delta_d=5/60, aadt=10000, occupancy=1.52, vot=21.10
        ... )
        9762962.0
    """
    if any(x < 0 for x in (aadt, occupancy, vot)):
        raise ValueError(
            f"AADT, occupancy, and VOT must be non-negative; "
            f"got aadt={aadt}, occupancy={occupancy}, vot={vot}"
        )
    return delta_d * aadt * 365 * occupancy * vot


def compute_voc_benefit(
    delta_voc: float,
    vmt: float,
) -> float:
    """Compute the annual vehicle operating cost reduction for one vehicle class.
    
    Second term of Eq 2.21:
    
        B_voc = delta_VOC * VMT
    
    Args:
        delta_voc: Change in vehicle operating cost ($/vehicle-mile).
            Positive = cost reduction.
        vmt: Annual vehicle miles traveled.
    
    Returns:
        Annual operating cost benefit in dollars per year.
    
    Example:
        >>> # $0.05/mi VOC reduction, 50M annual VMT
        >>> compute_voc_benefit(delta_voc=0.05, vmt=50_000_000)
        2500000.0
    """
    if vmt < 0:
        raise ValueError(f"VMT must be non-negative; got {vmt}")
    return delta_voc * vmt


def compute_annual_operational_benefit(
    vehicle_classes: Iterable[VehicleClassInputs],
) -> dict[str, float]:
    """Compute annual operational benefit summed over vehicle classes.
    
    Implements Eq 2.21 (annual form, before discounting):
    
        B_ij(operations,year) = sum_v [ travel_time_benefit_v + voc_benefit_v ]
    
    Args:
        vehicle_classes: Iterable of VehicleClassInputs for each vehicle class.
    
    Returns:
        Dictionary with keys:
            - 'travel_time_total': sum of travel-time benefits across classes
            - 'voc_total': sum of VOC benefits across classes
            - 'annual_total': sum of both
            - 'by_class': dict mapping class name to its annual contribution
    
    Example:
        >>> classes = [
        ...     VehicleClassInputs(name="passenger", delta_d=5/60,
        ...                        aadt=8000, occupancy=1.52, vot=21.10,
        ...                        delta_voc=0.03, vmt=14_600_000),
        ...     VehicleClassInputs(name="truck", delta_d=5/60,
        ...                        aadt=2000, occupancy=1.0, vot=33.50,
        ...                        delta_voc=0.05, vmt=3_650_000),
        ... ]
        >>> result = compute_annual_operational_benefit(classes)
        >>> result['annual_total'] > 0
        True
    """
    travel_time_total = 0.0
    voc_total = 0.0
    by_class = {}
    
    for vc in vehicle_classes:
        tt = compute_travel_time_benefit(
            delta_d=vc.delta_d,
            aadt=vc.aadt,
            occupancy=vc.occupancy,
            vot=vc.vot,
        )
        voc = compute_voc_benefit(
            delta_voc=vc.delta_voc,
            vmt=vc.vmt,
        )
        travel_time_total += tt
        voc_total += voc
        by_class[vc.name] = tt + voc
    
    annual_total = travel_time_total + voc_total
    
    return {
        "travel_time_total": travel_time_total,
        "voc_total": voc_total,
        "annual_total": annual_total,
        "by_class": by_class,
    }


# ---------------------------------------------------------------------
# Main entry point: present-value operational benefit
# ---------------------------------------------------------------------

def compute_operational_benefit(
    vehicle_classes: Iterable[VehicleClassInputs],
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Compute present-value operational benefit per Eq 2.21.
    
    Full Eq 2.21 with present-worth conversion:
    
        B_ij(operations,PV) = sum_v [ delta_d_v * AADT * 365 * OCC_v * VOT_v
                                     + delta_VOC_v * VMT_v ] * PWF(r, T)
    
    Assumes a uniform stream of equal annual benefits over T years discounted
    at rate r. Uses the standard Present Worth Factor formula.
    
    Args:
        vehicle_classes: Iterable of VehicleClassInputs for each vehicle class.
        discount_rate: Annual discount rate (default 0.07 per USDOT BCA).
        analysis_horizon: Analysis period in years (default 20 per USDOT BCA).
    
    Returns:
        Dictionary with all annual components plus:
            - 'pwf': Present Worth Factor used
            - 'pv_total': total present-value operational benefit
    
    Example:
        >>> classes = [
        ...     VehicleClassInputs(name="passenger", delta_d=5/60,
        ...                        aadt=8000, occupancy=1.52, vot=21.10,
        ...                        delta_voc=0.03, vmt=14_600_000),
        ... ]
        >>> result = compute_operational_benefit(classes)
        >>> 'pv_total' in result
        True
    """
    annual = compute_annual_operational_benefit(vehicle_classes)
    pwf = calculate_pwf(discount_rate, analysis_horizon)
    pv_total = annual["annual_total"] * pwf
    
    return {
        **annual,
        "pwf": pwf,
        "pv_total": pv_total,
    }


# ---------------------------------------------------------------------
# Convenience helpers for the common case (one passenger class)
# ---------------------------------------------------------------------

def compute_simple_operational_benefit(
    aadt: float,
    delay_reduction_minutes: float = 0.0,
    voc_reduction_per_mile: float = 0.0,
    segment_length_miles: float = 1.0,
    occupancy: float = DEFAULT_OCC["passenger"],
    vot: float = DEFAULT_VOT["all_purposes"],
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> dict[str, float]:
    """Convenience: compute operational benefit for a single passenger class.
    
    Useful for the common case of a rural two-lane segment with one
    homogeneous vehicle class. For multi-class problems (e.g., separate
    passenger and truck), use compute_operational_benefit() with explicit
    VehicleClassInputs objects.
    
    Args:
        aadt: Annual average daily traffic (vehicles/day).
        delay_reduction_minutes: Per-vehicle delay reduction in minutes
            (will be converted to hours internally). Positive = benefit.
        voc_reduction_per_mile: VOC reduction in $/vehicle-mile.
            Positive = benefit.
        segment_length_miles: Segment length in miles. Used to compute
            VMT = aadt * 365 * length.
        occupancy: Average vehicle occupancy (default 1.52).
        vot: Value of time ($/person-hour, default $21.10).
        discount_rate: Annual discount rate (default 0.07).
        analysis_horizon: Analysis period in years (default 20).
    
    Returns:
        Same dict structure as compute_operational_benefit().
    
    Example:
        >>> # Rural two-lane segment, 5000 AADT, 5-mile segment,
        >>> # 2-min delay reduction, $0.02/mi VOC reduction
        >>> result = compute_simple_operational_benefit(
        ...     aadt=5000,
        ...     delay_reduction_minutes=2.0,
        ...     voc_reduction_per_mile=0.02,
        ...     segment_length_miles=5.0,
        ... )
        >>> result['pv_total'] > 0
        True
    """
    delta_d_hours = delay_reduction_minutes / 60.0
    vmt_annual = aadt * 365 * segment_length_miles
    
    vc = VehicleClassInputs(
        name="passenger",
        delta_d=delta_d_hours,
        aadt=aadt,
        occupancy=occupancy,
        vot=vot,
        delta_voc=voc_reduction_per_mile,
        vmt=vmt_annual,
    )
    
    return compute_operational_benefit(
        [vc],
        discount_rate=discount_rate,
        analysis_horizon=analysis_horizon,
    )


# ---------------------------------------------------------------------
# DataFrame interface
# ---------------------------------------------------------------------

def compute_operational_benefits_df(
    inputs_df: pd.DataFrame,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> pd.DataFrame:
    """Compute operational benefits for many (site, alternative) pairs at once.
    
    Args:
        inputs_df: DataFrame with one row per (site_id, alt_id, vehicle_class)
            with columns: site_id, alt_id, vehicle_class_name, delta_d_hours,
            aadt, occupancy, vot, delta_voc, vmt.
        discount_rate: Annual discount rate.
        analysis_horizon: Analysis period in years.
    
    Returns:
        DataFrame with columns: site_id, alt_id, annual_total, pv_total,
        travel_time_total, voc_total. One row per (site_id, alt_id).
    
    Example:
        >>> df = pd.DataFrame([
        ...     {"site_id": 1, "alt_id": 1, "vehicle_class_name": "passenger",
        ...      "delta_d_hours": 5/60, "aadt": 8000, "occupancy": 1.52,
        ...      "vot": 21.10, "delta_voc": 0.03, "vmt": 14_600_000},
        ... ])
        >>> result = compute_operational_benefits_df(df)
        >>> 'pv_total' in result.columns
        True
    """
    required_cols = {
        "site_id", "alt_id", "vehicle_class_name",
        "delta_d_hours", "aadt", "occupancy", "vot",
        "delta_voc", "vmt",
    }
    missing = required_cols - set(inputs_df.columns)
    if missing:
        raise ValueError(f"inputs_df missing columns: {missing}")
    
    rows = []
    for (site_id, alt_id), group in inputs_df.groupby(["site_id", "alt_id"]):
        vehicle_classes = [
            VehicleClassInputs(
                name=row["vehicle_class_name"],
                delta_d=row["delta_d_hours"],
                aadt=row["aadt"],
                occupancy=row["occupancy"],
                vot=row["vot"],
                delta_voc=row["delta_voc"],
                vmt=row["vmt"],
            )
            for _, row in group.iterrows()
        ]
        result = compute_operational_benefit(
            vehicle_classes,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
        )
        rows.append({
            "site_id": site_id,
            "alt_id": alt_id,
            "annual_total": result["annual_total"],
            "travel_time_total": result["travel_time_total"],
            "voc_total": result["voc_total"],
            "pv_total": result["pv_total"],
        })
    
    return pd.DataFrame(rows)
