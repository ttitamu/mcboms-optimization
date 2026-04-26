"""
Tests for src/mcboms/benefits/ccm.py — Eq 2.27 implementation.

Covers:
- Per-category functions (energy, emissions, accessibility, resilience, pavement)
- CCMInputs aggregation
- Double-counting prevention against operations.py
- DataFrame batch interface
- Input validation
"""

import pandas as pd
import pytest

from mcboms.benefits.ccm import (
    DEFAULT_ACCESSIBILITY_VALUE_PER_TRIP,
    DEFAULT_ENERGY_VALUE_PER_KWH,
    DEFAULT_PAVEMENT_VALUE_PER_LANE_MILE_YEAR,
    DEFAULT_SCC_PER_TON_CO2,
    CCMInputs,
    compute_accessibility_benefit,
    compute_corridor_benefit,
    compute_corridor_benefits_df,
    compute_emissions_benefit,
    compute_energy_benefit,
    compute_pavement_benefit,
    compute_resilience_benefit,
)


# ============================================================
# Per-category function tests
# ============================================================


class TestEnergyBenefit:
    def test_zero_kwh_yields_zero(self):
        result = compute_energy_benefit(annual_kwh_saved=0)
        assert result["pv_total"] == 0.0
        assert result["category"] == "energy"

    def test_positive_savings_yields_positive_benefit(self):
        result = compute_energy_benefit(
            annual_kwh_saved=100_000, value_per_kwh=0.12
        )
        # Annual: 100,000 * 0.12 = $12,000
        assert result["annual_total"] == pytest.approx(12_000.0, rel=1e-9)
        # PV: $12,000 * 10.594
        assert result["pv_total"] == pytest.approx(12_000.0 * result["pwf"], rel=1e-9)

    def test_negative_kwh_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_energy_benefit(annual_kwh_saved=-100)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_energy_benefit(annual_kwh_saved=100, value_per_kwh=-1)


class TestEmissionsBenefit:
    def test_zero_co2_yields_zero(self):
        result = compute_emissions_benefit(annual_co2_tons_avoided=0)
        assert result["pv_total"] == 0.0

    def test_positive_co2_yields_positive_benefit(self):
        # 100 tons CO2 * $224/ton = $22,400 annually
        result = compute_emissions_benefit(annual_co2_tons_avoided=100)
        assert result["annual_total"] == pytest.approx(22_400.0, rel=1e-9)

    def test_custom_scc_overrides_default(self):
        result = compute_emissions_benefit(
            annual_co2_tons_avoided=100, scc_per_ton=300.0
        )
        assert result["annual_total"] == pytest.approx(30_000.0, rel=1e-9)

    def test_negative_co2_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_emissions_benefit(annual_co2_tons_avoided=-1)


class TestAccessibilityBenefit:
    def test_zero_trips_yields_zero(self):
        result = compute_accessibility_benefit(annual_trips_enabled=0)
        assert result["pv_total"] == 0.0

    def test_positive_trips_yields_positive(self):
        # 1000 trips/year * $12 = $12,000 annual
        result = compute_accessibility_benefit(annual_trips_enabled=1000)
        assert result["annual_total"] == pytest.approx(12_000.0, rel=1e-9)

    def test_negative_trips_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_accessibility_benefit(annual_trips_enabled=-1)


class TestResilienceBenefit:
    def test_zero_avoided_damages_yields_zero(self):
        result = compute_resilience_benefit(expected_avoided_damages=0)
        assert result["pv_total"] == 0.0

    def test_avoided_damages_correctly_aggregated(self):
        result = compute_resilience_benefit(expected_avoided_damages=50_000)
        assert result["annual_total"] == 50_000.0
        assert result["pv_total"] == pytest.approx(50_000.0 * result["pwf"], rel=1e-9)

    def test_negative_damages_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_resilience_benefit(expected_avoided_damages=-100)


class TestPavementBenefit:
    def test_zero_lane_miles_yields_zero(self):
        result = compute_pavement_benefit(lane_miles=0)
        assert result["pv_total"] == 0.0

    def test_positive_lane_miles_yields_positive(self):
        # 10 lane-miles * $5,000/lane-mile-year = $50,000 annual
        result = compute_pavement_benefit(lane_miles=10)
        assert result["annual_total"] == pytest.approx(50_000.0, rel=1e-9)

    def test_negative_lane_miles_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            compute_pavement_benefit(lane_miles=-1)


# ============================================================
# Aggregation (Eq 2.27 sum across categories)
# ============================================================


class TestCorridorBenefit:
    def test_empty_inputs_yields_zero_total(self):
        inputs = CCMInputs()
        result = compute_corridor_benefit(inputs)
        assert result["annual_total"] == 0.0
        assert result["pv_total"] == 0.0
        assert result["by_category"] == {}

    def test_single_category_aggregation(self):
        inputs = CCMInputs(energy_annual_kwh_saved=10_000)
        result = compute_corridor_benefit(inputs)
        assert "energy" in result["by_category"]
        # Other categories not included since they're zero
        assert "emissions" not in result["by_category"]

    def test_multi_category_aggregation(self):
        inputs = CCMInputs(
            energy_annual_kwh_saved=50_000,
            emissions_annual_co2_tons_avoided=200,
            pavement_lane_miles=10,
        )
        result = compute_corridor_benefit(inputs)
        assert len(result["by_category"]) == 3
        assert all(c in result["by_category"]
                   for c in ["energy", "emissions", "pavement"])

        # Total must equal sum of by-category
        cat_sum = sum(c["pv_total"] for c in result["by_category"].values())
        assert result["pv_total"] == pytest.approx(cat_sum, rel=1e-9)

    def test_pwf_consistent_across_categories(self):
        # All categories should use the same PWF when called together
        inputs = CCMInputs(
            energy_annual_kwh_saved=100,
            emissions_annual_co2_tons_avoided=10,
            pavement_lane_miles=5,
        )
        result = compute_corridor_benefit(
            inputs, discount_rate=0.04, analysis_horizon=15
        )
        pwfs = [c["pwf"] for c in result["by_category"].values()]
        assert len(set(pwfs)) == 1  # All PWFs identical
        assert result["pwf"] == pwfs[0]


# ============================================================
# Double-counting prevention (the critical safety feature)
# ============================================================


class TestDoubleCountingPrevention:
    """Critical test: accessibility CCM and operations Eq 2.21 can overlap."""

    def test_accessibility_alone_no_error(self):
        # Accessibility used WITHOUT operations being computed — fine
        inputs = CCMInputs(accessibility_annual_trips_enabled=500)
        result = compute_corridor_benefit(inputs, operations_already_computed=False)
        assert result["pv_total"] > 0

    def test_accessibility_and_operations_without_acknowledgment_raises(self):
        # Accessibility AND operations — must raise unless user acknowledges
        inputs = CCMInputs(accessibility_annual_trips_enabled=500)
        with pytest.raises(ValueError, match="Double-counting risk"):
            compute_corridor_benefit(inputs, operations_already_computed=True)

    def test_accessibility_and_operations_with_acknowledgment_proceeds(self):
        # User explicitly confirms they handled the overlap
        inputs = CCMInputs(
            accessibility_annual_trips_enabled=500,
            accessibility_overlaps_with_operations=True,
        )
        result = compute_corridor_benefit(inputs, operations_already_computed=True)
        assert result["pv_total"] > 0
        assert "accessibility" in result["by_category"]

    def test_operations_with_no_accessibility_no_error(self):
        # operations being computed but no accessibility category — fine
        inputs = CCMInputs(energy_annual_kwh_saved=100_000)
        result = compute_corridor_benefit(inputs, operations_already_computed=True)
        assert "energy" in result["by_category"]
        assert "accessibility" not in result["by_category"]


# ============================================================
# DataFrame interface tests
# ============================================================


class TestDataFrameInterface:
    def test_dataframe_single_row(self):
        df = pd.DataFrame([{
            "site_id": 1, "alt_id": 1,
            "energy_annual_kwh_saved": 10_000,
            "emissions_annual_co2_tons_avoided": 50,
        }])
        result = compute_corridor_benefits_df(df)
        assert len(result) == 1
        assert result.iloc[0]["pv_total"] > 0
        assert result.iloc[0]["energy_pv"] > 0
        assert result.iloc[0]["emissions_pv"] > 0

    def test_dataframe_with_zero_categories(self):
        # Row with all zeros
        df = pd.DataFrame([{"site_id": 1, "alt_id": 1}])
        result = compute_corridor_benefits_df(df)
        assert len(result) == 1
        assert result.iloc[0]["pv_total"] == 0.0

    def test_dataframe_multiple_alternatives(self):
        df = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "energy_annual_kwh_saved": 10_000},
            {"site_id": 1, "alt_id": 2, "energy_annual_kwh_saved": 20_000},
            {"site_id": 2, "alt_id": 1, "emissions_annual_co2_tons_avoided": 100},
        ])
        result = compute_corridor_benefits_df(df)
        assert len(result) == 3
        # Larger energy savings should give larger PV
        site1_alt1 = result[(result["site_id"] == 1) & (result["alt_id"] == 1)].iloc[0]
        site1_alt2 = result[(result["site_id"] == 1) & (result["alt_id"] == 2)].iloc[0]
        assert site1_alt2["pv_total"] > site1_alt1["pv_total"]

    def test_dataframe_missing_required_columns_raises(self):
        # Missing site_id
        df = pd.DataFrame([{"alt_id": 1, "energy_annual_kwh_saved": 100}])
        with pytest.raises(ValueError, match="missing columns"):
            compute_corridor_benefits_df(df)

    def test_dataframe_double_counting_with_operations_acknowledged(self):
        df = pd.DataFrame([{
            "site_id": 1, "alt_id": 1,
            "accessibility_annual_trips_enabled": 1000,
            "accessibility_overlaps_with_operations": True,
            "operations_also_computed": True,
        }])
        # Should not raise
        result = compute_corridor_benefits_df(df)
        assert len(result) == 1
        assert result.iloc[0]["accessibility_pv"] > 0


# ============================================================
# Default values
# ============================================================


class TestDefaultValues:
    def test_default_energy_value(self):
        assert DEFAULT_ENERGY_VALUE_PER_KWH == 0.12

    def test_default_scc(self):
        assert DEFAULT_SCC_PER_TON_CO2 == 224.0

    def test_default_accessibility_value(self):
        assert DEFAULT_ACCESSIBILITY_VALUE_PER_TRIP == 12.0

    def test_default_pavement_value(self):
        assert DEFAULT_PAVEMENT_VALUE_PER_LANE_MILE_YEAR == 5_000.0
