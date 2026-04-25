"""
Tests for ``mcboms.benefits.safety`` — Report Section 3.2.1.

The central validation is the worked example in Report Section 3.2.1.3, which
yields a present-value safety benefit of ~$11.24M for a 10→12 ft lane widening
on a 5-mile rural two-lane segment. Reproducing this number (within
floating-point tolerance) confirms that ``safety.py`` implements Eq. 18
consistently with the Report.

Secondary tests cover:
  * multiplicative CMF combination (Report Eq. 19a)
  * severity-key aliasing (KABCO ⇄ canonical)
  * segment-aware aggregation (Report: projects contain k = 1..K_i segments)
  * time-varying ``safety_benefit_time_varying`` collapses to the simplified
    ``safety_benefit`` when E is constant across years.
"""

from __future__ import annotations

import numpy as np
import pytest

from mcboms.benefits.safety import (
    SEVERITY_ORDER,
    SafetySegment,
    combine_cmfs,
    compute_alternative_safety_benefit,
    safety_benefit,
    safety_benefit_time_varying,
)
from mcboms.utils.economics import calculate_present_worth_factor


# =============================================================================
# Report Section 3.2.1.3 worked example — the anchor test.
# =============================================================================


class TestReportWorkedExample:
    """Reproduce the Report's Section 3.2.1.3 worked example numerically.

    Report inputs:
        segment length = 5.0 mi,  AADT = 5,000
        EB-adjusted E_nobuild = 6.0 crashes/year:
            fatal = 0.65, injury (A/B/C combined) = 1.4, PDO = 4.0
        CMF (10→12 ft lane widening) = 0.88 for all severities
        unit costs (as used in the Report's Step 3):
            fatal = $12,650,000; injury (average of A/B/C) = $400,000;
            PDO = $15,000
        discount rate = 7%; horizon = 20 yr  → PWF = 10.594

    Report's Step 3 annual benefit:
        fatal:  0.078 × $12.65M = $986,700
        injury: 0.168 × $400K   =  $67,200
        PDO:    0.48  × $15K    =   $7,200
        total annual                 = $1,061,100
    Report's Step 4 total:
        $1,061,100 × 10.594 ≈ $11,243,000
    """

    # The Report's worked example collapses A/B/C into one "injury" bin with
    # $400K average cost. To reproduce it exactly we split the 1.4 injuries
    # and the $400K cost evenly across A/B/C — arithmetically equivalent to
    # the Report's three-bin computation.
    REPORT_E_NOBUILD = {
        "fatal": 0.65,
        "injury_a": 1.4 / 3,
        "injury_b": 1.4 / 3,
        "injury_c": 1.4 / 3,
        "pdo": 4.0,
    }
    REPORT_UNIT_COSTS = {
        "fatal": 12_650_000,
        "injury_a": 400_000,
        "injury_b": 400_000,
        "injury_c": 400_000,
        "pdo": 15_000,
    }
    REPORT_CMF = 0.88
    REPORT_EXPECTED_ANNUAL = 1_061_100.0
    REPORT_EXPECTED_TOTAL = 11_243_000.0  # Report rounds PWF-product to this

    def test_annual_benefit_matches_report_step3(self) -> None:
        """Step-3 undiscounted annual benefit should match ~$1,061,100."""
        # One-year equivalent via horizon=1 with discount_rate=0 gives the
        # undiscounted annual figure.
        annual = safety_benefit(
            E_nobuild=self.REPORT_E_NOBUILD,
            cmf=self.REPORT_CMF,
            discount_rate=0.0,
            analysis_horizon=1,
            unit_costs=self.REPORT_UNIT_COSTS,
        )
        # Tolerance reflects Report's rounding of intermediate products.
        assert annual == pytest.approx(self.REPORT_EXPECTED_ANNUAL, rel=1e-4)

    def test_present_value_matches_report_step4(self) -> None:
        """Step-4 present-value total should match ~$11.24M at 7%/20 yr."""
        total = safety_benefit(
            E_nobuild=self.REPORT_E_NOBUILD,
            cmf=self.REPORT_CMF,
            discount_rate=0.07,
            analysis_horizon=20,
            unit_costs=self.REPORT_UNIT_COSTS,
        )
        # Report rounds to the nearest $1K; allow 0.5% relative tolerance.
        assert total == pytest.approx(self.REPORT_EXPECTED_TOTAL, rel=5e-3)

    def test_present_value_equals_annual_times_pwf(self) -> None:
        """The simplification B = (annual ΔE·UC) × PWF must hold exactly."""
        annual = safety_benefit(
            E_nobuild=self.REPORT_E_NOBUILD,
            cmf=self.REPORT_CMF,
            discount_rate=0.0,
            analysis_horizon=1,
            unit_costs=self.REPORT_UNIT_COSTS,
        )
        total = safety_benefit(
            E_nobuild=self.REPORT_E_NOBUILD,
            cmf=self.REPORT_CMF,
            discount_rate=0.07,
            analysis_horizon=20,
            unit_costs=self.REPORT_UNIT_COSTS,
        )
        pwf = calculate_present_worth_factor(0.07, 20)
        assert total == pytest.approx(annual * pwf, rel=1e-12)


# =============================================================================
# CMF combination (Report Eq. 19a)
# =============================================================================


class TestCombineCMFs:
    def test_two_cmfs_multiplicative(self) -> None:
        """Lane widening + shoulder widening example from the Report."""
        assert combine_cmfs([0.88, 0.82]) == pytest.approx(0.7216, abs=1e-12)

    def test_empty_returns_one(self) -> None:
        """Do-nothing alternative has no CMFs → combined = 1.0."""
        assert combine_cmfs([]) == 1.0

    def test_single_cmf_returns_itself(self) -> None:
        assert combine_cmfs([0.75]) == 0.75

    def test_non_positive_cmf_raises(self) -> None:
        with pytest.raises(ValueError):
            combine_cmfs([0.0])
        with pytest.raises(ValueError):
            combine_cmfs([-0.5])


# =============================================================================
# Severity aliasing
# =============================================================================


class TestSeverityHandling:
    def test_kabco_aliases_accepted(self) -> None:
        """Passing KABCO single-letter codes should work identically to canonical keys."""
        canonical = {
            "fatal": 0.5, "injury_a": 0.3, "injury_b": 0.4,
            "injury_c": 0.5, "pdo": 3.0,
        }
        kabco = {"K": 0.5, "A": 0.3, "B": 0.4, "C": 0.5, "PDO": 3.0}

        b_canonical = safety_benefit(
            E_nobuild=canonical, cmf=0.9, discount_rate=0.07
        )
        b_kabco = safety_benefit(
            E_nobuild=kabco, cmf=0.9, discount_rate=0.07
        )
        assert b_canonical == pytest.approx(b_kabco, rel=1e-12)

    def test_missing_severity_raises(self) -> None:
        with pytest.raises(ValueError, match="missing required keys"):
            safety_benefit(
                E_nobuild={"fatal": 0.1, "pdo": 1.0},  # A, B, C missing
                cmf=0.9,
                discount_rate=0.07,
            )

    def test_unknown_severity_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown severity"):
            safety_benefit(
                E_nobuild={
                    "K": 0.1, "A": 0.1, "B": 0.1, "C": 0.1, "PDO": 1.0,
                    "X_BOGUS": 99,
                },
                cmf=0.9,
                discount_rate=0.07,
            )


# =============================================================================
# Segment-aware aggregation (Report's K_i segments per project)
# =============================================================================


class TestSegmentAwareAggregation:
    def test_two_segments_sum_equals_parts(self) -> None:
        """A two-segment project's benefit must equal the sum of per-segment benefits."""
        seg1_E = {"fatal": 0.2, "injury_a": 0.1, "injury_b": 0.1,
                  "injury_c": 0.1, "pdo": 1.0}
        seg2_E = {"fatal": 0.4, "injury_a": 0.2, "injury_b": 0.2,
                  "injury_c": 0.2, "pdo": 2.0}

        b1 = safety_benefit(seg1_E, cmf=0.85, discount_rate=0.07)
        b2 = safety_benefit(seg2_E, cmf=0.85, discount_rate=0.07)

        segs = [
            SafetySegment(segment_id=1, length_mi=2.0, aadt=3000, E_nobuild=seg1_E),
            SafetySegment(segment_id=2, length_mi=3.0, aadt=5000, E_nobuild=seg2_E),
        ]
        b_combined = compute_alternative_safety_benefit(
            segments=segs,
            cmfs_per_segment=[0.85],  # uniform CMF across both segments
            discount_rate=0.07,
        )
        assert b_combined == pytest.approx(b1 + b2, rel=1e-12)

    def test_partial_length_with_per_segment_cmfs(self) -> None:
        """Partial-length treatment: only segment 1 receives the CMF."""
        seg_E = {"fatal": 0.2, "injury_a": 0.1, "injury_b": 0.1,
                 "injury_c": 0.1, "pdo": 1.0}
        segs = [
            SafetySegment(segment_id=1, length_mi=2.0, aadt=3000, E_nobuild=seg_E),
            SafetySegment(segment_id=2, length_mi=2.0, aadt=3000, E_nobuild=seg_E),
        ]
        b = compute_alternative_safety_benefit(
            segments=segs,
            cmfs_per_segment=[[0.80], [1.00]],  # seg1 treated, seg2 untreated
            discount_rate=0.07,
        )
        # Must equal benefit from treating seg1 alone
        b_expected = safety_benefit(seg_E, cmf=0.80, discount_rate=0.07)
        assert b == pytest.approx(b_expected, rel=1e-12)


# =============================================================================
# Time-varying ↔ simplified consistency
# =============================================================================


class TestTimeVaryingEquivalence:
    def test_constant_E_matches_simplified(self) -> None:
        """If E is constant across T years, time-varying = simplified formula."""
        E = {"fatal": 0.5, "injury_a": 0.3, "injury_b": 0.4,
             "injury_c": 0.5, "pdo": 3.0}
        # Build (T, K=1, S) array with E repeated each year
        E_array = np.array([[[0.5, 0.3, 0.4, 0.5, 3.0]]] * 20)  # (T=20, K=1, S=5)
        b_simple = safety_benefit(E, cmf=0.85, discount_rate=0.07, analysis_horizon=20)
        b_varying = safety_benefit_time_varying(E_array, cmf=0.85, discount_rate=0.07)
        assert b_simple == pytest.approx(b_varying, rel=1e-12)


# =============================================================================
# Input validation
# =============================================================================


class TestInputValidation:
    def test_negative_discount_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="discount_rate"):
            safety_benefit({"fatal": 0.1, "injury_a": 0, "injury_b": 0,
                            "injury_c": 0, "pdo": 0}, cmf=0.9, discount_rate=-0.01)

    def test_zero_horizon_raises(self) -> None:
        with pytest.raises(ValueError, match="analysis_horizon"):
            safety_benefit({"fatal": 0.1, "injury_a": 0, "injury_b": 0,
                            "injury_c": 0, "pdo": 0}, cmf=0.9,
                           discount_rate=0.07, analysis_horizon=0)

    def test_do_nothing_alternative_zero_benefit(self) -> None:
        """CMF = 1.0 (do nothing) must yield exactly zero benefit."""
        E = {"fatal": 0.5, "injury_a": 0.3, "injury_b": 0.4,
             "injury_c": 0.5, "pdo": 3.0}
        assert safety_benefit(E, cmf=1.0, discount_rate=0.07) == 0.0
