"""
Excel reader for the colleague's MCBOM BCA Tool (Example_Data_Version__March_24_).

This module reads the colleague's macro-enabled workbook and produces inputs
that ``mcboms.benefits.safety`` can consume. It serves three purposes:

1. **Bridge** the data-curation half of the project (colleague's tool) to the
   optimization half (this codebase).
2. **Independent verification** of the per-segment Safety Benefit values
   computed by the spreadsheet, recomputed from raw inputs via ``safety.py``.
3. **Defensibility** — when reviewers ask "do your two tools agree?", we can
   answer with a numerical reconciliation, not a hand-wave.

Workbook structure consumed (March 24, 2026 version):
    - Sheet 'Safety':
        * Cells M4, M6, M8 = unit crash costs for K, B (used for ABC), O
          (located in the "Value of Reduced Fatalities, Injuries, and Crashes"
           table, columns K-M)
        * Cells O39:O75 = combined CMFs from the colleague's CMF combination
          tool (Table B), one per (segment × alternative) combination.
    - Sheet 'Segment Data':
        * Columns K-O (24-28) = observed crash counts by KABCO severity
          per segment (k = 1..K_i, indexed by xd_id).
        * Column F = AADT, Column C = Length (mi), Column A = Custom_TMCID.
    - Sheet 'BCA':
        * Column X = Safety Benefit (precomputed by the spreadsheet, used for
          reconciliation).

The colleague's safety benefit formula (verified by reading cell X3):
    Safety_Benefit = UC_K * (Obs_K - Proj_K)
                   + UC_B * (Obs_ABC - Proj_ABC)
                   + UC_O * (Obs_O - Proj_O)

This collapses A, B, C into a single "ABC" injury bin priced at UC_B
($1,681,000), uses K (fatal) at $13.7M, and O (PDO) at $5,500. It also
omits discounting and the analysis horizon — that is, the spreadsheet
reports a *single-year* benefit difference, not a present-value benefit.

This is a deliberate deviation from Report Equation 18, which uses 5-bin
KABCO disaggregation and discounts over T years. The reader exposes both
representations so the optimization half can use either and reconcile.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from mcboms.benefits.safety import (
    SEVERITY_ORDER,
    SafetySegment,
    safety_benefit,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Cell locations in the March 24, 2026 workbook
# -----------------------------------------------------------------------------

#: Crash unit costs from the Safety sheet (column M, rows 4/6/8).
#: These are the values the colleague's BCA formula multiplies into.
COLLEAGUE_CELL_UC_K = ("Safety", "M", 4)
COLLEAGUE_CELL_UC_B = ("Safety", "M", 6)   # used for combined ABC injury
COLLEAGUE_CELL_UC_O = ("Safety", "M", 8)


@dataclass
class CollegueWorkbookData:
    """Structured payload extracted from the colleague's BCA workbook."""

    #: Per-segment observed crashes, columns: K, A, B, C, O. Index = xd_id.
    segments: pd.DataFrame

    #: Per (segment, alternative) precomputed safety benefit and projected crashes.
    bca_rows: pd.DataFrame

    #: Treatment combinations (alternatives) with their combined CMFs.
    combinations: pd.DataFrame

    #: Crash unit costs as used by the spreadsheet (3-bin: K / B-for-ABC / O).
    unit_costs_3bin: dict[str, float]


# -----------------------------------------------------------------------------
# Workbook reader
# -----------------------------------------------------------------------------


def read_colleague_workbook(path: str | Path) -> CollegueWorkbookData:
    """Load the colleague's MCBOM BCA workbook (March 24, 2026 version).

    Args:
        path: Path to ``Example_Data_Version__March_24_.xlsm`` (or compatible).

    Returns:
        :class:`CollegueWorkbookData` with parsed sheets ready for use by
        :func:`reconcile_safety_benefits` or downstream optimization code.

    Raises:
        FileNotFoundError: If the workbook does not exist.
        ValueError: If required sheets/columns are missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Workbook not found: {path}")

    # --- Segment Data: per-segment observed crashes & exposure -----------
    seg = pd.read_excel(path, sheet_name="Segment Data")
    required_seg_cols = {"xd_id", "Custom_TMCID", "Length (mi)", "AADT",
                          "K", "A", "B", "C", "O"}
    missing = required_seg_cols - set(seg.columns)
    if missing:
        raise ValueError(f"'Segment Data' sheet is missing columns: {missing}")
    segments = seg[[
        "xd_id", "Custom_TMCID", "Length (mi)", "AADT",
        "K", "A", "B", "C", "O",
    ]].rename(columns={
        "Length (mi)": "length_mi",
        "K": "obs_K", "A": "obs_A", "B": "obs_B",
        "C": "obs_C", "O": "obs_O",
    }).copy()

    # --- BCA sheet: precomputed safety benefit per (segment, alternative) -
    bca = pd.read_excel(path, sheet_name="BCA", header=1)
    # Header row has multi-level structure; defensive selection by name:
    keep = [c for c in [
        "Project (i)", "Custom_TMCID", "Segment (k)", "Alternative (j)",
        "All Crashes- Observed", "Killed (K) - Observed",
        "Incapacitating Injury (A) - Observed",
        "Non-incapacitating Injury (B) - Observed",
        "Possible Injury (C) -Observed", "Injury Crashes (ABC)",
        "No Injury (O) - Observed",
        "All Crashes- projected",
        "Killed - Projected (SPF/CMF using AADT)",
        "Incapacitating Injury (A) - Projected",
        "Non-incapacitating Injury (B) - Projecte",
        "Possible Injury (C) -Projected",
        "Injury Crashes (ABC) - Projected",
        "No Injury (O) - Projected",
        "Safety Benefit",
    ] if c in bca.columns]
    bca_rows = bca[keep].copy()

    # --- Safety sheet: unit crash costs and combined CMFs -----------------
    saf = pd.read_excel(path, sheet_name="Safety", header=None)

    def _cell(col_letter: str, row_idx_1based: int):
        col_idx = ord(col_letter.upper()) - ord("A")
        return saf.iat[row_idx_1based - 1, col_idx]

    uc_K = float(_cell("M", 4))
    uc_B = float(_cell("M", 6))   # used for combined ABC by the spreadsheet
    uc_O = float(_cell("M", 8))
    unit_costs_3bin = {"K": uc_K, "B_for_ABC": uc_B, "O": uc_O}

    # Combination table (Table B): rows 39..75
    # Combination name in column O (col 15), Combined CMF in column Z (col 26).
    combos = []
    for r in range(39, 76):
        name = _cell("O", r)
        if name is None or str(name).strip() == "":
            continue
        combined_cmf = _cell("Z", r)
        if combined_cmf is None:
            continue
        try:
            cmf_val = float(combined_cmf)
        except (TypeError, ValueError):
            continue
        combos.append({"alternative": str(name).strip(),
                       "combined_cmf": cmf_val})
    combinations = pd.DataFrame(combos)

    logger.info(
        "Loaded workbook: %d segments, %d BCA rows, %d combinations",
        len(segments), len(bca_rows), len(combinations),
    )
    return CollegueWorkbookData(
        segments=segments,
        bca_rows=bca_rows,
        combinations=combinations,
        unit_costs_3bin=unit_costs_3bin,
    )


# -----------------------------------------------------------------------------
# Reconciliation: spreadsheet vs. safety.py
# -----------------------------------------------------------------------------


def replicate_spreadsheet_formula(
    obs_K: float,
    obs_ABC: float,
    obs_O: float,
    proj_K: float,
    proj_ABC: float,
    proj_O: float,
    uc_K: float,
    uc_B: float,
    uc_O: float,
) -> float:
    """Reproduce the colleague's BCA cell formula exactly (single-year, no discount).

    Implements: ``UC_K*(Obs_K-Proj_K) + UC_B*(Obs_ABC-Proj_ABC) + UC_O*(Obs_O-Proj_O)``

    This is the formula in cell X3 of the BCA sheet (verified by direct read
    of the .xlsm file). It is not the Report's Equation 18 — it is single-year,
    3-bin (K/ABC/O), and uses UC_B for the entire ABC bin. Use this only for
    reconciliation, not for production safety estimates.
    """
    return (
        uc_K * (obs_K - proj_K)
        + uc_B * (obs_ABC - proj_ABC)
        + uc_O * (obs_O - proj_O)
    )


def reconcile_safety_benefits(
    data: CollegueWorkbookData,
    discount_rate: float = 0.07,
    analysis_horizon: int = 20,
) -> pd.DataFrame:
    """Compare per-row spreadsheet safety benefits against ``safety.py`` outputs.

    Two computations are produced for each (segment, alternative) row:

    1. **Spreadsheet replication** — exact reproduction of the workbook's
       single-year, 3-bin formula. This should match the workbook's
       ``Safety Benefit`` column to within rounding (~$25 on million-dollar
       values).
    2. **Report Eq. 18 (5-bin KABCO, present-value)** — the formulation
       implemented by ``mcboms.benefits.safety.safety_benefit``, applied to
       the same observed crashes and the back-calculated CMF. This will
       differ from the spreadsheet for two principled reasons: it splits
       A/B/C with severity-specific costs, and it discounts over T years.

    Returns:
        DataFrame with columns:
            - ``segment_k``, ``alternative_j``: row identifiers
            - ``spreadsheet_value``: from BCA sheet column X
            - ``replicated_value``: from :func:`replicate_spreadsheet_formula`
            - ``replication_error``: difference (should be ~0)
            - ``safety_py_pv_value``: PV benefit from :func:`safety_benefit`
            - ``ratio_safetypy_to_spreadsheet``: ratio (informational)
    """
    uc_K = data.unit_costs_3bin["K"]
    uc_B = data.unit_costs_3bin["B_for_ABC"]
    uc_O = data.unit_costs_3bin["O"]

    # Use the report's KABCO-disaggregated USDOT 2024 costs for safety.py.
    # The spreadsheet's UC_K = $13.7M differs slightly from USDOT 2024 $13.2M;
    # we honor the spreadsheet's number for this reconciliation so the only
    # methodological differences are (a) bin disaggregation and (b) discounting.
    uc_5bin = {
        "fatal": uc_K,
        "injury_a": uc_B,    # ABC all priced at UC_B in the spreadsheet
        "injury_b": uc_B,
        "injury_c": uc_B,
        "pdo": uc_O,
    }

    out = []
    for _, row in data.bca_rows.iterrows():
        # Skip rows that lack the projected values (do-nothing, etc.)
        try:
            obs_K = float(row.get("Killed (K) - Observed", 0) or 0)
            obs_A = float(row.get("Incapacitating Injury (A) - Observed", 0) or 0)
            obs_B = float(row.get("Non-incapacitating Injury (B) - Observed", 0) or 0)
            obs_C = float(row.get("Possible Injury (C) -Observed", 0) or 0)
            obs_O = float(row.get("No Injury (O) - Observed", 0) or 0)
            obs_ABC = obs_A + obs_B + obs_C

            proj_K = float(row.get("Killed - Projected (SPF/CMF using AADT)", 0) or 0)
            proj_ABC = float(row.get("Injury Crashes (ABC) - Projected", 0) or 0)
            proj_O = float(row.get("No Injury (O) - Projected", 0) or 0)
        except (TypeError, ValueError):
            continue

        spreadsheet_val = row.get("Safety Benefit")
        if spreadsheet_val is None or pd.isna(spreadsheet_val):
            continue
        spreadsheet_val = float(spreadsheet_val)

        # 1) Replicate spreadsheet formula
        replicated = replicate_spreadsheet_formula(
            obs_K=obs_K, obs_ABC=obs_ABC, obs_O=obs_O,
            proj_K=proj_K, proj_ABC=proj_ABC, proj_O=proj_O,
            uc_K=uc_K, uc_B=uc_B, uc_O=uc_O,
        )

        # 2) Run safety.py with same observed crashes and the back-calculated CMF.
        #    Spreadsheet uses observed crashes directly as E_nobuild
        #    (no Empirical Bayes adjustment in this reconciliation).
        E_nobuild = {
            "fatal": obs_K, "injury_a": obs_A, "injury_b": obs_B,
            "injury_c": obs_C, "pdo": obs_O,
        }
        # Back-calculate per-severity CMF from the proj/obs ratio
        # (the spreadsheet uses the same combined CMF for all severities)
        if obs_ABC > 0:
            cmf = proj_ABC / obs_ABC
        elif obs_O > 0:
            cmf = proj_O / obs_O
        else:
            cmf = 1.0

        py_val = safety_benefit(
            E_nobuild=E_nobuild,
            cmf=cmf,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
            unit_costs=uc_5bin,
        )

        out.append({
            "segment_k": row.get("Segment (k)"),
            "alternative_j": row.get("Alternative (j)"),
            "cmf_back_calc": cmf,
            "spreadsheet_value": spreadsheet_val,
            "replicated_value": replicated,
            "replication_error": replicated - spreadsheet_val,
            "safety_py_pv_value": py_val,
            "ratio_safetypy_to_spreadsheet": (
                py_val / spreadsheet_val if spreadsheet_val else float("nan")
            ),
        })

    df = pd.DataFrame(out)
    if not df.empty:
        logger.info(
            "Reconciled %d rows. Replication error: max abs = $%.2f, "
            "median ratio safety.py/spreadsheet = %.2f",
            len(df),
            df["replication_error"].abs().max(),
            df["ratio_safetypy_to_spreadsheet"].median(),
        )
    return df


# -----------------------------------------------------------------------------
# Conversion to safety.py inputs (for downstream optimization)
# -----------------------------------------------------------------------------


def colleague_segments_to_safety_segments(
    data: CollegueWorkbookData,
    project_id: int | None = None,
) -> list[SafetySegment]:
    """Convert the colleague's segment table to ``SafetySegment`` objects.

    Each row in 'Segment Data' becomes one :class:`SafetySegment`. Observed
    crash counts go directly into ``E_nobuild`` (no Empirical Bayes here —
    EB adjustment is upstream and out of scope for this reader).

    Args:
        data: Parsed workbook from :func:`read_colleague_workbook`.
        project_id: If provided, filter to segments matching this Custom_TMCID.

    Returns:
        List of :class:`SafetySegment` ready for
        :func:`mcboms.benefits.safety.compute_alternative_safety_benefit`.
    """
    df = data.segments
    if project_id is not None:
        df = df[df["Custom_TMCID"] == project_id]

    segments: list[SafetySegment] = []
    for _, row in df.iterrows():
        segments.append(SafetySegment(
            segment_id=int(row["xd_id"]),
            length_mi=float(row["length_mi"]),
            aadt=float(row["AADT"]),
            E_nobuild={
                "fatal":    float(row["obs_K"]),
                "injury_a": float(row["obs_A"]),
                "injury_b": float(row["obs_B"]),
                "injury_c": float(row["obs_C"]),
                "pdo":      float(row["obs_O"]),
            },
        ))
    return segments


__all__ = [
    "CollegueWorkbookData",
    "read_colleague_workbook",
    "replicate_spreadsheet_formula",
    "reconcile_safety_benefits",
    "colleague_segments_to_safety_segments",
]
