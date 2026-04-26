"""
Tests for src/mcboms/benefits/operations.py — Eq 2.21 implementation.

Covers:
- Component functions (travel-time benefit, VOC benefit)
- Annual aggregation across vehicle classes
- PV conversion via PWF
- Convenience helpers
- DataFrame batch interface
- Input validation and edge cases
"""

import pandas as pd
import pytest

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


# ============================================================
# Component function tests
# ============================================================


class TestTravelTimeBenefit:
    """Tests for the first term of Eq 2.21: B_tt = delta_d * AADT * 365 * OCC * VOT"""

    def test_zero_delay_change_yields_zero_benefit(self):
        result = compute_travel_time_benefit(
            delta_d=0.0, aadt=10000, occupancy=1.5, vot=21.10
        )
        assert result == 0.0

    def test_positive_delay_reduction_yields_positive_benefit(self):
        # 5 minutes = 5/60 hours; 10000 AADT; 1.52 occupancy; $21.10 VOT
        result = compute_travel_time_benefit(
            delta_d=5 / 60, aadt=10000, occupancy=1.52, vot=21.10
        )
        # Expected: (5/60) * 10000 * 365 * 1.52 * 21.10
        expected = (5 / 60) * 10000 * 365 * 1.52 * 21.10
        assert result == pytest.approx(expected, rel=1e-9)

    def test_negative_delay_yields_negative_benefit(self):
        # If a treatment INCREASES delay, benefit is negative
        result = compute_travel_time_benefit(
            delta_d=-1 / 60, aadt=5000, occupancy=1.5, vot=20.0
        )
        assert result < 0

    def test_negative_aadt_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_travel_time_benefit(
                delta_d=0.1, aadt=-100, occupancy=1.5, vot=20.0
            )

    def test_negative_occupancy_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_travel_time_benefit(
                delta_d=0.1, aadt=1000, occupancy=-1.0, vot=20.0
            )

    def test_negative_vot_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_travel_time_benefit(
                delta_d=0.1, aadt=1000, occupancy=1.5, vot=-1.0
            )


class TestVOCBenefit:
    """Tests for the second term of Eq 2.21: B_voc = delta_VOC * VMT"""

    def test_zero_voc_change_yields_zero_benefit(self):
        result = compute_voc_benefit(delta_voc=0.0, vmt=1_000_000)
        assert result == 0.0

    def test_positive_voc_reduction_yields_positive_benefit(self):
        result = compute_voc_benefit(delta_voc=0.05, vmt=10_000_000)
        # Expected: 0.05 * 10M = $500,000
        assert result == pytest.approx(500_000.0, rel=1e-9)

    def test_negative_voc_change_yields_negative_benefit(self):
        result = compute_voc_benefit(delta_voc=-0.02, vmt=1_000_000)
        # Treatment increases per-mile cost
        assert result == pytest.approx(-20_000.0, rel=1e-9)

    def test_negative_vmt_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_voc_benefit(delta_voc=0.05, vmt=-1000)


# ============================================================
# Aggregation tests
# ============================================================


class TestAnnualAggregation:
    """Sum across vehicle classes per Eq 2.21."""

    def test_single_class_aggregation(self):
        vc = VehicleClassInputs(
            name="passenger",
            delta_d=5 / 60, aadt=8000, occupancy=1.52, vot=21.10,
            delta_voc=0.03, vmt=14_600_000,
        )
        result = compute_annual_operational_benefit([vc])

        # Manual computation
        tt = (5 / 60) * 8000 * 365 * 1.52 * 21.10
        voc = 0.03 * 14_600_000
        expected_total = tt + voc

        assert result["travel_time_total"] == pytest.approx(tt, rel=1e-9)
        assert result["voc_total"] == pytest.approx(voc, rel=1e-9)
        assert result["annual_total"] == pytest.approx(expected_total, rel=1e-9)
        assert "passenger" in result["by_class"]
        assert result["by_class"]["passenger"] == pytest.approx(tt + voc, rel=1e-9)

    def test_multi_class_sums_correctly(self):
        passenger = VehicleClassInputs(
            name="passenger",
            delta_d=5 / 60, aadt=8000, occupancy=1.52, vot=21.10,
            delta_voc=0.03, vmt=14_600_000,
        )
        truck = VehicleClassInputs(
            name="truck",
            delta_d=5 / 60, aadt=2000, occupancy=1.0, vot=33.50,
            delta_voc=0.05, vmt=3_650_000,
        )
        result = compute_annual_operational_benefit([passenger, truck])

        # Both classes contribute
        assert "passenger" in result["by_class"]
        assert "truck" in result["by_class"]

        # Total equals sum of by-class
        assert result["annual_total"] == pytest.approx(
            sum(result["by_class"].values()), rel=1e-9
        )

    def test_empty_vehicle_classes_yields_zero(self):
        result = compute_annual_operational_benefit([])
        assert result["annual_total"] == 0.0
        assert result["travel_time_total"] == 0.0
        assert result["voc_total"] == 0.0
        assert result["by_class"] == {}


# ============================================================
# Present-value tests
# ============================================================


class TestPresentValueOperational:
    """Eq 2.21 with PWF conversion."""

    def test_pwf_matches_methodology_default(self):
        vc = VehicleClassInputs(
            name="passenger", delta_d=1 / 60, aadt=1000,
            occupancy=1.5, vot=20.0, delta_voc=0.0, vmt=0,
        )
        result = compute_operational_benefit(
            [vc], discount_rate=0.07, analysis_horizon=20
        )
        # PWF(0.07, 20) = 10.594 per the methodology
        assert result["pwf"] == pytest.approx(10.594, abs=0.01)

    def test_pv_equals_annual_times_pwf(self):
        vc = VehicleClassInputs(
            name="passenger", delta_d=1 / 60, aadt=5000,
            occupancy=1.5, vot=20.0, delta_voc=0.02, vmt=1_000_000,
        )
        result = compute_operational_benefit(
            [vc], discount_rate=0.07, analysis_horizon=20
        )
        assert result["pv_total"] == pytest.approx(
            result["annual_total"] * result["pwf"], rel=1e-9
        )

    def test_higher_discount_rate_yields_lower_pv(self):
        vc = VehicleClassInputs(
            name="passenger", delta_d=1 / 60, aadt=5000,
            occupancy=1.5, vot=20.0, delta_voc=0.0, vmt=0,
        )
        pv_low = compute_operational_benefit(
            [vc], discount_rate=0.03, analysis_horizon=20
        )["pv_total"]
        pv_high = compute_operational_benefit(
            [vc], discount_rate=0.10, analysis_horizon=20
        )["pv_total"]
        assert pv_low > pv_high


# ============================================================
# Convenience helper tests
# ============================================================


class TestSimpleHelper:
    """compute_simple_operational_benefit() convenience function."""

    def test_simple_helper_matches_explicit_construction(self):
        # Explicit construction
        vc = VehicleClassInputs(
            name="passenger",
            delta_d=2 / 60,
            aadt=5000,
            occupancy=DEFAULT_OCC["passenger"],
            vot=DEFAULT_VOT["all_purposes"],
            delta_voc=0.02,
            vmt=5000 * 365 * 5.0,  # aadt * 365 * length
        )
        explicit = compute_operational_benefit([vc])

        # Simple helper
        simple = compute_simple_operational_benefit(
            aadt=5000,
            delay_reduction_minutes=2.0,
            voc_reduction_per_mile=0.02,
            segment_length_miles=5.0,
        )

        assert simple["pv_total"] == pytest.approx(explicit["pv_total"], rel=1e-9)
        assert simple["annual_total"] == pytest.approx(
            explicit["annual_total"], rel=1e-9
        )

    def test_simple_with_no_voc_reduction_only_travel_time(self):
        result = compute_simple_operational_benefit(
            aadt=5000,
            delay_reduction_minutes=3.0,
            voc_reduction_per_mile=0.0,
            segment_length_miles=2.0,
        )
        assert result["voc_total"] == 0.0
        assert result["travel_time_total"] > 0.0

    def test_simple_with_no_delay_reduction_only_voc(self):
        result = compute_simple_operational_benefit(
            aadt=5000,
            delay_reduction_minutes=0.0,
            voc_reduction_per_mile=0.05,
            segment_length_miles=2.0,
        )
        assert result["travel_time_total"] == 0.0
        assert result["voc_total"] > 0.0


# ============================================================
# DataFrame interface tests
# ============================================================


class TestDataFrameInterface:
    """compute_operational_benefits_df() batch processing."""

    def test_dataframe_single_row(self):
        df = pd.DataFrame([{
            "site_id": 1, "alt_id": 1, "vehicle_class_name": "passenger",
            "delta_d_hours": 5 / 60, "aadt": 8000,
            "occupancy": 1.52, "vot": 21.10,
            "delta_voc": 0.03, "vmt": 14_600_000,
        }])
        result = compute_operational_benefits_df(df)
        assert len(result) == 1
        assert result.iloc[0]["site_id"] == 1
        assert result.iloc[0]["pv_total"] > 0

    def test_dataframe_multi_class_per_alt(self):
        # Two vehicle classes for the same (site, alt)
        df = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "vehicle_class_name": "passenger",
             "delta_d_hours": 5 / 60, "aadt": 8000,
             "occupancy": 1.52, "vot": 21.10,
             "delta_voc": 0.03, "vmt": 14_600_000},
            {"site_id": 1, "alt_id": 1, "vehicle_class_name": "truck",
             "delta_d_hours": 5 / 60, "aadt": 2000,
             "occupancy": 1.0, "vot": 33.50,
             "delta_voc": 0.05, "vmt": 3_650_000},
        ])
        result = compute_operational_benefits_df(df)
        # Should have ONE row for (site=1, alt=1) summing both classes
        assert len(result) == 1
        assert result.iloc[0]["site_id"] == 1
        assert result.iloc[0]["alt_id"] == 1

    def test_dataframe_multiple_alternatives(self):
        df = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "vehicle_class_name": "passenger",
             "delta_d_hours": 1 / 60, "aadt": 5000,
             "occupancy": 1.52, "vot": 21.10,
             "delta_voc": 0.01, "vmt": 5_000_000},
            {"site_id": 1, "alt_id": 2, "vehicle_class_name": "passenger",
             "delta_d_hours": 3 / 60, "aadt": 5000,
             "occupancy": 1.52, "vot": 21.10,
             "delta_voc": 0.04, "vmt": 5_000_000},
            {"site_id": 2, "alt_id": 1, "vehicle_class_name": "passenger",
             "delta_d_hours": 2 / 60, "aadt": 8000,
             "occupancy": 1.52, "vot": 21.10,
             "delta_voc": 0.02, "vmt": 8_000_000},
        ])
        result = compute_operational_benefits_df(df)
        assert len(result) == 3
        # Higher delay reduction should give higher benefit
        site1_alt1 = result[(result["site_id"] == 1) & (result["alt_id"] == 1)].iloc[0]
        site1_alt2 = result[(result["site_id"] == 1) & (result["alt_id"] == 2)].iloc[0]
        assert site1_alt2["pv_total"] > site1_alt1["pv_total"]

    def test_dataframe_missing_columns_raises(self):
        # Missing 'vmt' column
        df = pd.DataFrame([{
            "site_id": 1, "alt_id": 1, "vehicle_class_name": "passenger",
            "delta_d_hours": 0.1, "aadt": 1000,
            "occupancy": 1.5, "vot": 20.0, "delta_voc": 0.0,
        }])
        with pytest.raises(ValueError, match="missing columns"):
            compute_operational_benefits_df(df)


# ============================================================
# Default-values tests
# ============================================================


class TestDefaultValues:
    """USDOT BCA May 2025 defaults are correctly embedded."""

    def test_default_vot_values(self):
        assert DEFAULT_VOT["all_purposes"] == 21.10
        assert DEFAULT_VOT["personal"] == 19.40
        assert DEFAULT_VOT["business"] == 33.50

    def test_default_passenger_occupancy(self):
        assert DEFAULT_OCC["passenger"] == 1.52

    def test_default_passenger_voc(self):
        assert DEFAULT_VOC["passenger"] == 0.56
