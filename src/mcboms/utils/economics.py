"""
Economic Utility Functions for MCBOMs.

This module provides functions for economic calculations including:
- Net Present Value (NPV)
- Discount factors
- Benefit-cost ratios
- Annualization
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)


def calculate_discount_factor(
    rate: float,
    year: int,
) -> float:
    """Calculate single-year discount factor.
    
    Args:
        rate: Annual discount rate (e.g., 0.07 for 7%)
        year: Year number (1-indexed)
    
    Returns:
        Discount factor for the specified year
    
    Formula:
        DF_t = 1 / (1 + r)^t
    
    Example:
        >>> calculate_discount_factor(0.07, 10)
        0.5083...
    """
    if rate < 0:
        raise ValueError(f"Discount rate must be non-negative, got {rate}")
    if year < 0:
        raise ValueError(f"Year must be non-negative, got {year}")
    
    return 1 / (1 + rate) ** year


def calculate_discount_factors(
    rate: float,
    horizon: int,
) -> np.ndarray:
    """Calculate discount factors for all years in analysis horizon.
    
    Args:
        rate: Annual discount rate
        horizon: Number of years
    
    Returns:
        Array of discount factors [DF_1, DF_2, ..., DF_T]
    
    Example:
        >>> factors = calculate_discount_factors(0.07, 20)
        >>> factors[0]  # Year 1
        0.9345...
        >>> factors[19]  # Year 20
        0.2584...
    """
    years = np.arange(1, horizon + 1)
    return 1 / (1 + rate) ** years


def calculate_present_worth_factor(
    rate: float,
    years: int,
) -> float:
    """Calculate uniform-series present worth factor (P/A).
    
    Used to convert uniform annual benefits to present value.
    
    Args:
        rate: Annual discount rate
        years: Number of years
    
    Returns:
        Present worth factor
    
    Formula:
        (P/A, i, n) = [(1+i)^n - 1] / [i * (1+i)^n]
    
    Example:
        >>> calculate_present_worth_factor(0.07, 20)
        10.594...
    """
    if rate == 0:
        return float(years)
    
    return ((1 + rate) ** years - 1) / (rate * (1 + rate) ** years)


def calculate_npv(
    cash_flows: Sequence[float],
    rate: float,
    initial_investment: float = 0,
) -> float:
    """Calculate Net Present Value of cash flows.
    
    Args:
        cash_flows: Sequence of annual cash flows (benefits - costs)
        rate: Annual discount rate
        initial_investment: Initial cost at year 0
    
    Returns:
        Net Present Value
    
    Example:
        >>> cash_flows = [100_000] * 20  # $100K annual benefit
        >>> npv = calculate_npv(cash_flows, 0.07, initial_investment=500_000)
    """
    factors = calculate_discount_factors(rate, len(cash_flows))
    pv_benefits = np.sum(np.array(cash_flows) * factors)
    return pv_benefits - initial_investment


def calculate_bcr(
    benefits: float,
    costs: float,
) -> float:
    """Calculate Benefit-Cost Ratio.
    
    Args:
        benefits: Total present value of benefits
        costs: Total present value of costs
    
    Returns:
        Benefit-cost ratio (or inf if costs are zero)
    """
    if costs == 0:
        return float('inf') if benefits > 0 else 0.0
    return benefits / costs


def annualize_value(
    present_value: float,
    rate: float,
    years: int,
) -> float:
    """Convert present value to equivalent uniform annual value.
    
    Args:
        present_value: Present value amount
        rate: Annual discount rate
        years: Number of years
    
    Returns:
        Equivalent uniform annual value
    
    Formula:
        A = P * [i * (1+i)^n] / [(1+i)^n - 1]
    """
    if rate == 0:
        return present_value / years
    
    pwf = calculate_present_worth_factor(rate, years)
    return present_value / pwf


# =====================================================================
# DEFAULT ECONOMIC PARAMETERS
# =====================================================================
# Discount rate and analysis horizon per USDOT BCA Guidance
# for Discretionary Grant Programs, May 2025, Section 4.3 (p. 12):
# "applicants should use a real discount rate of 7 percent per year"
# and Section 4.4 (p. 13-14): operating period commonly 20 years for
# capacity/operating improvements; up to 30 for full reconstruction.
DEFAULT_DISCOUNT_RATE = 0.07
DEFAULT_ANALYSIS_HORIZON = 20


# =====================================================================
# CRASH UNIT COSTS — FRAMEWORK DEFAULT
# =====================================================================
# Source: USDOT Benefit-Cost Analysis Guidance for Discretionary Grant
# Programs, May 2025, Appendix A, Table A-1 (page 39).
# Base year: 2023 dollars.
#
# These are the framework defaults. State DOTs applying MCBOMs may
# override with state-specific values (see FHWA-SA-25-021 Step 5 for
# the per-capita-income adjustment procedure).
#
# The USDOT BCA May 2025 values (KABCO) are also consistent with the
# discount rate (7%) used elsewhere in the framework, since both come
# from the same source document.
CRASH_COSTS_USDOT_BCA_MAY2025 = {
    "fatal":    13_200_000,   # K  - Killed
    "injury_a":  1_254_700,   # A  - Incapacitating (Suspected Serious)
    "injury_b":    246_900,   # B  - Non-incapacitating (Suspected Minor)
    "injury_c":    118_000,   # C  - Possible injury
    "pdo":           5_300,   # O  - Property damage only / No injury
}

# Alias for the framework default
CRASH_COSTS_DEFAULT = CRASH_COSTS_USDOT_BCA_MAY2025


# =====================================================================
# CRASH UNIT COSTS — ALTERNATIVE STANDARDS (documented for reference)
# =====================================================================
# FHWA-SA-25-021 "Updated Crash Costs for Highway Safety Analysis"
# (October 2025), Table 1. Base year: 2024 dollars.
# This is the HSIP-context standard. ~20-30% higher than USDOT BCA
# May 2025 values across the board because of different MAIS-to-KABCO
# translation assumptions and a newer base year.
# Use this set only when the application context explicitly calls for
# the FHWA highway-safety-specific values (e.g., HSIP BCA tool work).
CRASH_COSTS_FHWA_SA_25_021 = {
    "fatal":    15_988_000,   # K
    "injury_a":  1_705_100,   # A
    "injury_b":    384_000,   # B
    "injury_c":    204_600,   # C
    "pdo":          18_100,   # O
}

# Harwood (2003) crash costs (1994 FHWA values, as used in the
# original RSRAP paper). For Harwood validation reproduction ONLY —
# do not use for new analyses. In the Harwood case study the per-site
# benefit values from the paper's Tables 2 and 3 are used directly,
# so these aggregate unit costs are informational.
CRASH_COSTS_HARWOOD_2003 = {
    "fatal":     2_600_000,
    "injury_a":    180_000,
    "injury_b":     36_000,
    "injury_c":     19_000,
    "pdo":           2_000,
}


# =====================================================================
# VALUE OF TRAVEL TIME
# =====================================================================
# Source: USDOT BCA Guidance, May 2025, Appendix A, Table A-2 (page 40).
# Base year: 2023 dollars, per person-hour.
VOT_USDOT_BCA_MAY2025 = {
    "personal":       19.40,   # Local personal travel
    "business":       33.50,   # On-the-clock work travel
    "all_purposes":   21.10,   # Blended personal + business
    "walk_wait":      38.80,   # Walking/cycling/waiting/standing/transfer
    "truck_driver":   35.70,   # Commercial truck operator
    "bus_driver":     42.60,
    "transit_rail":   59.60,
    "locomotive":     52.90,
}

# Alias
VOT_DEFAULT = VOT_USDOT_BCA_MAY2025

# Harwood (2003) VOT, for reproduction only ($10/hr in 1994 dollars)
VOT_HARWOOD_2003 = {
    "all": 10.00,
}


# =====================================================================
# BACKWARD-COMPATIBILITY ALIASES
# =====================================================================
# The old names pointed to stale (pre-May-2025) values. We keep the
# old symbol names bound to the new canonical dicts so existing imports
# do not break, but new code should use CRASH_COSTS_DEFAULT and
# VOT_DEFAULT (or the explicit versioned names).
CRASH_COSTS_USDOT_2024 = CRASH_COSTS_USDOT_BCA_MAY2025
VOT_USDOT_2024 = VOT_USDOT_BCA_MAY2025
