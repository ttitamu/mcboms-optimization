"""
Safety Benefit Calculation Module for MCBOMs.

Implements Section 3.2.1 of the MCBOMs Task 4 Model Development report.

Core formulation (Report Equation 18):

    B_ij(safety) = Σ_t Σ_k Σ_s [ E_ikst(no-build) − E_ijkst(build) ] · UC_s · DF_t

    E_ijkst(build) = E_ikst(no-build) · CMF_ijs                      (Report Eq. 19)

    CMF_ij(combined) = CMF_1 · CMF_2 · ... · CMF_n                   (multiplicative, HSM)

Index definitions (Report Section 3.2.1):
    i : project
    j : alternative (treatment combination)
    k : homogeneous segment or intersection within project i, k ∈ {1, ..., K_i}
    s : crash severity ∈ {Fatal (K), Injury A, Injury B, Injury C, PDO}
    t : year, t ∈ {1, ..., T}  (T = 20 default)
    DF_t = 1 / (1 + r)^t        (r is configurable; report uses 7%)

Design notes:
    - This module computes B_ij(safety) for a single (i, j) pair. The optimizer
      calls it once per alternative during preprocessing. Gating by the binary
      variable x_ij happens in the objective function (Report Section 3.1.2,
      Eq. 4), not here.
    - Empirical Bayes adjustment to produce E(no-build) is handled upstream
      (HSM Part C procedure). This module accepts E(no-build) as an input so
      that SPF/EB concerns remain isolated in a dedicated module.
    - CMFs for multi-treatment alternatives are combined multiplicatively via
      combine_cmfs() before being passed in.
    - The default assumes constant annual expected crashes across the analysis
      horizon — the simplification used in the Report's worked example
      (Section 3.2.1.3). For time-varying crash expectations (e.g., to reflect
      traffic growth or treatment-effectiveness decay), use
      safety_benefit_time_varying().

References:
    - MCBOMs Task 4 Report, Section 3.2.1, Equations 18-20.
    - AASHTO (2010), Highway Safety Manual, 1st edition.
    - Harwood, Rabbani, Richard (2003), TRR 1840, pp. 148-157.
    - USDOT (2025), Benefit-Cost Analysis Guidance for Discretionary Grants.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

import numpy as np

from mcboms.utils.economics import (
    CRASH_COSTS_USDOT_2024,
    calculate_discount_factors,
    calculate_present_worth_factor,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Severity handling
# -----------------------------------------------------------------------------

#: Canonical severity order. Matches the keys used in ``economics.py`` and the
#: KABCO classification (Fatal, Incapacitating, Non-incapacitating, Possible,
#: Property Damage Only). All arrays in this module are ordered per this tuple.
SEVERITY_ORDER: tuple[str, ...] = ("fatal", "injury_a", "injury_b", "injury_c", "pdo")

#: User-friendly aliases mapping to canonical severity keys. Supports KABCO
#: single-letter codes ("K", "A", "B", "C", "O") and the common spellings.
SEVERITY_ALIASES: dict[str, str] = {
    "fatal": "fatal", "Fatal": "fatal", "K": "fatal", "k": "fatal",
    "injury_a": "injury_a", "Injury A": "injury_a", "A": "injury_a", "a": "injury_a",
    "injury_b": "injury_b", "Injury B": "injury_b", "B": "injury_b", "b": "injury_b",
    "injury_c": "injury_c", "Injury C": "injury_c", "C": "injury_c", "c": "injury_c",
    "pdo": "pdo", "PDO": "pdo", "O": "pdo", "o": "pdo",
}


def _normalize_severity_key(key: str) -> str:
    """Map a user-provided severity label to the canonical key in SEVERITY_ORDER."""
    if key in SEVERITY_ALIASES:
        return SEVERITY_ALIASES[key]
    raise ValueError(
        f"Unknown severity key {key!r}. Expected one of {SEVERITY_ORDER} "
        f"or a KABCO alias (K/A/B/C/O/PDO)."
    )


def _dict_to_severity_array(d: Mapping[str, float]) -> np.ndarray:
    """Convert a severity-keyed dict to an array ordered per SEVERITY_ORDER.

    Raises:
        ValueError: If any canonical severity is missing.
    """
    normalized = {_normalize_severity_key(k): float(v) for k, v in d.items()}
    missing = [s for s in SEVERITY_ORDER if s not in normalized]
    if missing:
        raise ValueError(
            f"Severity dict is missing required keys: {missing}. "
            f"Must provide values for all of {SEVERITY_ORDER}."
        )
    return np.array([normalized[s] for s in SEVERITY_ORDER], dtype=float)


# -----------------------------------------------------------------------------
# CMF handling
# -----------------------------------------------------------------------------


def combine_cmfs(cmfs: Iterable[float]) -> float:
    """Combine multiple CMFs multiplicatively per HSM methodology.

    Implements the combination rule stated in the Report Section 3.2.1::

        CMF_combined = CMF_1 × CMF_2 × ... × CMF_n

    Example (from the Report)::

        >>> combine_cmfs([0.88, 0.82])  # lane widening + shoulder widening
        0.7216

    Args:
        cmfs: Iterable of individual CMF values.

    Returns:
        Combined CMF. Returns ``1.0`` if no CMFs are provided (do-nothing).

    Raises:
        ValueError: If any CMF is non-positive.
    """
    result = 1.0
    for cmf in cmfs:
        if cmf <= 0:
            raise ValueError(f"CMF must be positive, got {cmf}.")
        result *= float(cmf)
    return result


def _broadcast_cmf(cmf, n_segments: int, n_severities: int) -> np.ndarray:
    """Broadcast a user-supplied CMF specification to shape (K, S).

    Accepted inputs:
        - scalar                                   → same CMF everywhere
        - array shape (S,)                         → varies by severity only
        - array shape (K,)                         → varies by segment only
          (only unambiguous when K != S; otherwise pass (K, S) explicitly)
        - array shape (K, S)                       → fully specified
        - dict {severity: cmf}                     → per-severity, broadcast over K
    """
    if isinstance(cmf, Mapping):
        arr_s = _dict_to_severity_array(cmf)
        return np.broadcast_to(arr_s, (n_segments, n_severities)).copy()

    cmf_arr = np.asarray(cmf, dtype=float)

    if cmf_arr.ndim == 0:
        return np.full((n_segments, n_severities), float(cmf_arr))

    if cmf_arr.ndim == 1:
        if cmf_arr.shape[0] == n_severities:
            return np.broadcast_to(cmf_arr, (n_segments, n_severities)).copy()
        if cmf_arr.shape[0] == n_segments and n_segments != n_severities:
            return np.broadcast_to(cmf_arr[:, None], (n_segments, n_severities)).copy()
        raise ValueError(
            f"1-D CMF has length {cmf_arr.shape[0]}; expected {n_severities} "
            f"(severities) or {n_segments} (segments). "
            f"If K == S, pass a 2-D (K, S) array to disambiguate."
        )

    if cmf_arr.ndim == 2:
        if cmf_arr.shape != (n_segments, n_severities):
            raise ValueError(
                f"2-D CMF has shape {cmf_arr.shape}; "
                f"expected ({n_segments}, {n_severities})."
            )
        return cmf_arr.copy()

    raise ValueError(f"CMF has unsupported shape {cmf_arr.shape}.")


def _coerce_nobuild(E_nobuild, n_severities: int) -> np.ndarray:
    """Coerce E_nobuild into a (K, S) array.

    Accepted inputs:
        - dict {severity: crashes}                       → single segment, K = 1
        - array shape (S,)                               → single segment
        - array shape (K, S)                             → as-is
        - sequence of dicts [{severity: crashes}, ...]   → one per segment
    """
    if isinstance(E_nobuild, Mapping):
        return _dict_to_severity_array(E_nobuild).reshape(1, n_severities)

    if isinstance(E_nobuild, (list, tuple)) and E_nobuild and isinstance(E_nobuild[0], Mapping):
        rows = [_dict_to_severity_array(d) for d in E_nobuild]
        return np.vstack(rows)

    arr = np.asarray(E_nobuild, dtype=float)
    if arr.ndim == 1:
        if arr.shape[0] != n_severities:
            raise ValueError(
                f"1-D E_nobuild has length {arr.shape[0]}; expected {n_severities}."
            )
        return arr.reshape(1, n_severities)
    if arr.ndim == 2:
        if arr.shape[1] != n_severities:
            raise ValueError(
                f"2-D E_nobuild has shape {arr.shape}; expected (K, {n_severities})."
            )
        return arr

    raise ValueError(f"E_nobuild has unsupported shape {arr.shape}.")


def _coerce_unit_costs(unit_costs) -> np.ndarray:
    """Coerce unit crash costs into a (S,) array ordered per SEVERITY_ORDER."""
    if unit_costs is None:
        return _dict_to_severity_array(CRASH_COSTS_USDOT_2024)
    if isinstance(unit_costs, Mapping):
        return _dict_to_severity_array(unit_costs)
    arr = np.asarray(unit_costs, dtype=float)
    if arr.ndim != 1 or arr.shape[0] != len(SEVERITY_ORDER):
        raise ValueError(
            f"unit_costs must be length-{len(SEVERITY_ORDER)} vector "
            f"ordered per SEVERITY_ORDER; got shape {arr.shape}."
        )
    return arr


# -----------------------------------------------------------------------------
# Core calculations
# -----------------------------------------------------------------------------


def expected_crashes_build(E_nobuild: np.ndarray, cmf: np.ndarray) -> np.ndarray:
    """Compute build-condition expected crashes per Report Eq. 19.

        E_ijkst(build) = E_ikst(no-build) · CMF_ijs

    Args:
        E_nobuild: shape (K, S) array of no-build annual crashes.
        cmf:       shape (K, S) array of crash modification factors.

    Returns:
        shape (K, S) array of build-condition annual crashes.
    """
    E = np.asarray(E_nobuild, dtype=float)
    C = np.asarray(cmf, dtype=float)
    if E.shape != C.shape:
        raise ValueError(
            f"E_nobuild shape {E.shape} must equal CMF shape {C.shape}."
        )
    return E * C


def annual_crash_reductions(E_nobuild: np.ndarray, cmf: np.ndarray) -> np.ndarray:
    """Compute ΔE = E(no-build) − E(build), shape (K, S).

    This is the integrand of Report Eq. 18 for a single year, before
    monetization by UC_s and discounting by DF_t.
    """
    return np.asarray(E_nobuild, dtype=float) - expected_crashes_build(E_nobuild, cmf)


# -----------------------------------------------------------------------------
# Top-level public API
# -----------------------------------------------------------------------------


def safety_benefit(
    E_nobuild,
    cmf,
    discount_rate: float,
    analysis_horizon: int = 20,
    unit_costs=None,
) -> float:
    """Compute present-value safety benefit B_ij(safety) — Report Eq. 18.

    Uses the constant-annual-crashes simplification (the assumption in the
    Report's Section 3.2.1.3 worked example)::

        B_ij(safety) = [ Σ_k Σ_s (E_ikst(no-build) − E_ijkst(build)) · UC_s ] · PWF(r, T)

    where ``PWF(r, T) = Σ_{t=1}^T 1/(1+r)^t`` is the uniform-series present-worth
    factor. For time-varying expected crashes, use
    :func:`safety_benefit_time_varying`.

    Args:
        E_nobuild: Expected annual no-build crashes. Accepts:
            - dict ``{severity: crashes}`` — single-segment project.
            - sequence of dicts — one per segment.
            - ndarray shape ``(K, S)`` — K segments, S severities.
            - ndarray shape ``(S,)`` — single segment.
            Severities ordered per :data:`SEVERITY_ORDER`.
        cmf: Crash modification factor. Accepts scalar, 1-D ``(S,)`` or
            ``(K,)``, 2-D ``(K, S)``, or a severity-keyed dict. For multi-
            treatment alternatives, combine with :func:`combine_cmfs` first.
        discount_rate: Annual real discount rate (required, e.g. 0.07 for 7%,
            0.04 for the Harwood 2003 validation context).
        analysis_horizon: Analysis period T in years. Default 20.
        unit_costs: ``$/crash`` by severity. Accepts a length-S array ordered
            per :data:`SEVERITY_ORDER`, or a severity-keyed dict. Defaults to
            :data:`CRASH_COSTS_USDOT_2024` from ``utils.economics``.

    Returns:
        Present-value total safety benefit in dollars for this alternative.

    Raises:
        ValueError: On shape mismatches or non-positive CMFs.

    Example:
        Report Section 3.2.1.3 worked example (rural two-lane, 10→12 ft lanes)::

            >>> # EB-adjusted no-build crashes by severity (report values)
            >>> E_nobuild = {"fatal": 0.65, "injury_a": 0.467, "injury_b": 0.467,
            ...              "injury_c": 0.467, "pdo": 4.0}  # 1.4 injuries avg
            >>> # Lane widening 10→12 ft: CMF = 0.88 for all severities
            >>> benefit = safety_benefit(E_nobuild, cmf=0.88,
            ...                          discount_rate=0.07, analysis_horizon=20)
    """
    if discount_rate < 0 or discount_rate >= 1:
        raise ValueError(
            f"discount_rate must be in [0, 1); got {discount_rate}."
        )
    if analysis_horizon <= 0:
        raise ValueError(
            f"analysis_horizon must be positive; got {analysis_horizon}."
        )

    S = len(SEVERITY_ORDER)
    E = _coerce_nobuild(E_nobuild, n_severities=S)      # (K, S)
    K = E.shape[0]
    C = _broadcast_cmf(cmf, n_segments=K, n_severities=S)  # (K, S)
    UC = _coerce_unit_costs(unit_costs)                    # (S,)

    delta_E = E - E * C                                   # (K, S)  ΔE per year
    annual_dollars = float(np.sum(delta_E * UC[np.newaxis, :]))
    pwf = calculate_present_worth_factor(discount_rate, analysis_horizon)
    return annual_dollars * pwf


def safety_benefit_time_varying(
    E_nobuild_t,
    cmf,
    discount_rate: float,
    unit_costs=None,
) -> float:
    """Compute PV safety benefit with year-varying no-build crashes — full Eq. 18.

    Use this when expected crashes vary across the analysis horizon (e.g., due
    to traffic growth or treatment-effectiveness decay). The CMF is still
    assumed constant over time (standard HSM practice); vary ``E_nobuild_t``
    across years to reflect temporal effects.

    Args:
        E_nobuild_t: Shape ``(T, K, S)`` array of expected no-build crashes by
            year, segment, severity. ``T`` is inferred from the first axis.
        cmf: As in :func:`safety_benefit`; broadcast to ``(K, S)`` (constant
            across years).
        discount_rate: Annual real discount rate.
        unit_costs: ``$/crash`` by severity, ordered per :data:`SEVERITY_ORDER`.
            Defaults to :data:`CRASH_COSTS_USDOT_2024`.

    Returns:
        Present-value total safety benefit in dollars.
    """
    if discount_rate < 0 or discount_rate >= 1:
        raise ValueError(f"discount_rate must be in [0, 1); got {discount_rate}.")

    arr = np.asarray(E_nobuild_t, dtype=float)
    if arr.ndim != 3:
        raise ValueError(
            f"E_nobuild_t must be 3-D (T, K, S); got shape {arr.shape}."
        )
    T, K, S = arr.shape
    if S != len(SEVERITY_ORDER):
        raise ValueError(
            f"E_nobuild_t last axis must have length {len(SEVERITY_ORDER)}; "
            f"got {S}."
        )

    C = _broadcast_cmf(cmf, n_segments=K, n_severities=S)   # (K, S)
    UC = _coerce_unit_costs(unit_costs)                     # (S,)
    DF = calculate_discount_factors(discount_rate, T)       # (T,)

    delta_E = arr - arr * C[np.newaxis, :, :]               # (T, K, S)
    dollars_per_year = np.sum(delta_E * UC[np.newaxis, np.newaxis, :], axis=(1, 2))
    return float(np.sum(dollars_per_year * DF))


# -----------------------------------------------------------------------------
# Segment-aware high-level helpers
# -----------------------------------------------------------------------------


@dataclass
class SafetySegment:
    """One homogeneous segment or intersection within a project (index k).

    Attributes:
        segment_id: Identifier within the parent project.
        length_mi: Segment length in miles (0 for intersections).
        aadt: Average daily traffic (informational; unused in safety math).
        E_nobuild: Annual no-build expected crashes, either as a dict keyed by
            severity or as a length-S array ordered per SEVERITY_ORDER.
            Typically produced upstream via HSM SPF + Empirical Bayes.
    """
    segment_id: int | str
    length_mi: float
    aadt: float
    E_nobuild: Mapping[str, float] | Sequence[float]

    def E_nobuild_array(self) -> np.ndarray:
        """Return no-build crashes as a length-S array ordered per SEVERITY_ORDER."""
        if isinstance(self.E_nobuild, Mapping):
            return _dict_to_severity_array(self.E_nobuild)
        arr = np.asarray(self.E_nobuild, dtype=float)
        if arr.shape != (len(SEVERITY_ORDER),):
            raise ValueError(
                f"Segment {self.segment_id}: E_nobuild must be length "
                f"{len(SEVERITY_ORDER)}; got shape {arr.shape}."
            )
        return arr


def compute_alternative_safety_benefit(
    segments: Sequence[SafetySegment],
    cmfs_per_segment: Sequence[Iterable[float]] | Iterable[float],
    discount_rate: float,
    analysis_horizon: int = 20,
    unit_costs=None,
) -> float:
    """Compute B_ij(safety) for one alternative applied to a multi-segment project.

    This is the segment-aware entry point intended for use by the alternative
    enumerator. It assembles the ``(K, S)`` arrays from a list of
    :class:`SafetySegment` objects and delegates to :func:`safety_benefit`.

    Args:
        segments: Segments k = 1..K that make up the project.
        cmfs_per_segment: Either:
            - A sequence of iterables, one per segment, each containing the
              CMFs to be combined multiplicatively for that segment (useful
              for partial-length treatments where some segments receive
              treatment and others do not — pass ``[1.0]`` for untreated).
            - A single iterable of CMFs, applied uniformly across all segments
              (combined multiplicatively).
        discount_rate: Annual real discount rate.
        analysis_horizon: Analysis period in years.
        unit_costs: ``$/crash`` by severity; defaults to USDOT 2024 values.

    Returns:
        Present-value total safety benefit across all segments.
    """
    if not segments:
        return 0.0

    # Build (K, S) no-build matrix
    E_matrix = np.vstack([seg.E_nobuild_array() for seg in segments])

    # Build (K,) combined-CMF vector and broadcast over severities
    cmf_list = list(cmfs_per_segment)
    is_per_segment = bool(cmf_list) and isinstance(cmf_list[0], (list, tuple))
    if is_per_segment:
        if len(cmf_list) != len(segments):
            raise ValueError(
                f"cmfs_per_segment has {len(cmf_list)} entries but there are "
                f"{len(segments)} segments."
            )
        combined_per_seg = np.array(
            [combine_cmfs(seg_cmfs) for seg_cmfs in cmf_list], dtype=float
        )
    else:
        uniform_cmf = combine_cmfs(cmf_list)
        combined_per_seg = np.full(len(segments), uniform_cmf)

    # Broadcast per-segment scalar CMF to (K, S) (same CMF across severities)
    cmf_matrix = np.broadcast_to(
        combined_per_seg[:, None], (len(segments), len(SEVERITY_ORDER))
    )

    return safety_benefit(
        E_nobuild=E_matrix,
        cmf=cmf_matrix,
        discount_rate=discount_rate,
        analysis_horizon=analysis_horizon,
        unit_costs=unit_costs,
    )


__all__ = [
    "SEVERITY_ORDER",
    "SEVERITY_ALIASES",
    "combine_cmfs",
    "expected_crashes_build",
    "annual_crash_reductions",
    "safety_benefit",
    "safety_benefit_time_varying",
    "SafetySegment",
    "compute_alternative_safety_benefit",
]
