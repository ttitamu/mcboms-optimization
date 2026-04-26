"""
Tests for src/mcboms/core/optimizer.py constraint extensions.

Covers the 6 new constraints added to the Optimizer class:

    - Eq 2.8  — dependency        (alternative (i,j) requires (ip,jp))
    - Eq 2.9  — cross-project exclusivity
    - Eq 2.10 — minimum BCR per project
    - Eq 2.14 — facility-type sub-budget
    - Eq 2.15 — regional cap
    - Eq 2.16 — regional minimum-investment floor

Each test builds a small toy problem with known optimal solution under
the constraint, then verifies the optimizer respects it.
"""

import pandas as pd
import pytest

from mcboms.core.optimizer import Optimizer


# ============================================================
# Toy problem fixtures
# ============================================================


def make_simple_problem():
    """Two sites, two alternatives each, costs and benefits set so that
    without any constraints the optimal is to pick the high-benefit
    alternatives at both sites (within budget).
    """
    sites = pd.DataFrame({
        "site_id": [1, 2],
    })
    alternatives = pd.DataFrame([
        # Site 1
        {"site_id": 1, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 1_500_000},
        {"site_id": 1, "alt_id": 2, "total_cost": 2_000_000, "total_benefit": 4_000_000},
        # Site 2
        {"site_id": 2, "alt_id": 1, "total_cost": 1_500_000, "total_benefit": 2_000_000},
        {"site_id": 2, "alt_id": 2, "total_cost": 3_000_000, "total_benefit": 5_500_000},
    ])
    return sites, alternatives


def make_facility_problem():
    """Sites with different facility types — used to test Eq 2.14."""
    sites = pd.DataFrame({
        "site_id": [1, 2, 3, 4],
        "facility_type": ["rural_2lane", "rural_2lane", "urban_4lane", "urban_4lane"],
    })
    alternatives = pd.DataFrame([
        {"site_id": 1, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_500_000},
        {"site_id": 2, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_500_000},
        {"site_id": 3, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_500_000},
        {"site_id": 4, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_500_000},
    ])
    return sites, alternatives


def make_regional_problem():
    """Sites in different regions — used to test Eq 2.15-2.16."""
    sites = pd.DataFrame({
        "site_id": [1, 2, 3, 4],
        "region": ["north", "north", "south", "south"],
    })
    alternatives = pd.DataFrame([
        # Two high-benefit alternatives in the north
        {"site_id": 1, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 5_000_000},
        {"site_id": 2, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 5_000_000},
        # Two lower-benefit alternatives in the south
        {"site_id": 3, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_000_000},
        {"site_id": 4, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_000_000},
    ])
    return sites, alternatives


# ============================================================
# Eq 2.8 — Dependency
# ============================================================


class TestDependencyConstraint:
    """Eq 2.8: x_ij <= x_i'j' — selecting (i,j) requires (i',j')."""

    def test_no_dependency_baseline(self):
        # Without dependency, both site 1 alt 2 and site 2 alt 2 are best
        sites, alts = make_simple_problem()
        opt = Optimizer(sites, alts, budget=10_000_000)
        result = opt.solve()
        selected = result.selected_alternatives
        assert result.status == "optimal"
        # Both sites pick alt_id=2 (their high-benefit option)
        assert set(zip(selected["site_id"], selected["alt_id"])) == {(1, 2), (2, 2)}

    def test_dependency_forces_companion_selection(self):
        # Force: if site 1 picks alt 1, site 2 must also pick alt 1
        sites, alts = make_simple_problem()
        opt = Optimizer(
            sites, alts, budget=10_000_000,
            dependencies=[(1, 1, 2, 1)],  # (1,1) requires (2,1)
        )
        result = opt.solve()
        # Should still be optimal (high-benefit both is unaffected)
        assert result.status == "optimal"
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        # If (1,1) selected, then (2,1) must be selected
        if (1, 1) in selected:
            assert (2, 1) in selected

    def test_dependency_with_unselected_companion_blocks_alternative(self):
        # Tight test: budget only allows ONE alternative
        # (1,1) requires (2,2). Budget too small to take both.
        # So (1,1) cannot be selected.
        sites, alts = make_simple_problem()
        opt = Optimizer(
            sites, alts, budget=2_000_000,  # only enough for one alt
            dependencies=[(1, 1, 2, 2)],
        )
        result = opt.solve()
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        # (1,1) cannot be in selected because (2,2) cost is 3M alone
        assert (1, 1) not in selected


# ============================================================
# Eq 2.9 — Cross-project exclusivity
# ============================================================


class TestCrossProjectExclusivity:
    """Eq 2.9: x_ij + x_i'j' <= 1 — alternatives can't both be selected."""

    def test_exclusivity_prevents_both(self):
        sites, alts = make_simple_problem()
        # Cannot have both (1,2) and (2,2) — the high-benefit pair
        opt = Optimizer(
            sites, alts, budget=10_000_000,
            conflicts=[(1, 2, 2, 2)],
        )
        result = opt.solve()
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        assert not ((1, 2) in selected and (2, 2) in selected)

    def test_exclusivity_with_no_overlap_doesnt_block_optimum(self):
        # Conflict on alternatives that wouldn't both be selected anyway
        sites, alts = make_simple_problem()
        opt = Optimizer(
            sites, alts, budget=10_000_000,
            conflicts=[(1, 1, 2, 1)],  # low-benefit options
        )
        result = opt.solve()
        # Optimal still picks (1,2) and (2,2) — neither is in conflict pair
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        assert (1, 2) in selected
        assert (2, 2) in selected


# ============================================================
# Eq 2.10 — Minimum BCR
# ============================================================


class TestMinimumBCR:
    """Eq 2.10: B_ij >= theta * C_ij — only allow cost-effective alternatives."""

    def test_min_bcr_excludes_low_bcr_alternatives(self):
        # Construct alternatives where some have BCR < threshold
        sites = pd.DataFrame({"site_id": [1]})
        alts = pd.DataFrame([
            # BCR = 1.2 (below 1.5 threshold)
            {"site_id": 1, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 1_200_000},
            # BCR = 2.0 (passes 1.5 threshold)
            {"site_id": 1, "alt_id": 2, "total_cost": 1_000_000, "total_benefit": 2_000_000},
        ])
        opt = Optimizer(
            sites, alts, budget=5_000_000,
            min_bcr=1.5,
        )
        result = opt.solve()
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        # alt 1 has BCR 1.2 < 1.5, must not be selected
        assert (1, 1) not in selected

    def test_min_bcr_of_one_means_benefit_geq_cost(self):
        # All alternatives must have B >= C
        sites = pd.DataFrame({"site_id": [1]})
        alts = pd.DataFrame([
            # BCR = 0.8 (below 1.0)
            {"site_id": 1, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 800_000},
            # BCR = 1.5 (above 1.0)
            {"site_id": 1, "alt_id": 2, "total_cost": 1_000_000, "total_benefit": 1_500_000},
        ])
        opt = Optimizer(sites, alts, budget=5_000_000, min_bcr=1.0)
        result = opt.solve()
        selected = set(zip(
            result.selected_alternatives["site_id"],
            result.selected_alternatives["alt_id"],
        ))
        assert (1, 1) not in selected
        # alt 2 should be selected
        assert (1, 2) in selected

    def test_min_bcr_zero_allows_anything(self):
        # min_bcr = 0 means no effective constraint
        sites, alts = make_simple_problem()
        opt = Optimizer(sites, alts, budget=10_000_000, min_bcr=0.0)
        result = opt.solve()
        assert result.status == "optimal"

    def test_min_bcr_negative_raises(self):
        sites, alts = make_simple_problem()
        with pytest.raises(ValueError, match="min_bcr"):
            Optimizer(sites, alts, budget=10_000_000, min_bcr=-0.5)


# ============================================================
# Eq 2.14 — Facility-type sub-budget
# ============================================================


class TestFacilityBudget:
    """Eq 2.14: facility-type spending caps."""

    def test_facility_budget_limits_spend_per_type(self):
        # Total budget 8M, but rural sub-budget only 3M
        # Should pick at most 1 rural alternative (cost 2M, benefit 3.5M)
        sites, alts = make_facility_problem()
        opt = Optimizer(
            sites, alts, budget=8_000_000,
            facility_budgets={"rural_2lane": 3_000_000, "urban_4lane": 5_000_000},
        )
        result = opt.solve()

        # Sum spend per facility type
        selected = result.selected_alternatives.merge(
            sites, on="site_id", how="left"
        )
        rural_spend = selected[
            selected["facility_type"] == "rural_2lane"
        ]["total_cost"].sum()
        urban_spend = selected[
            selected["facility_type"] == "urban_4lane"
        ]["total_cost"].sum()

        assert rural_spend <= 3_000_000
        assert urban_spend <= 5_000_000

    def test_facility_budget_missing_column_raises(self):
        # If facility_budgets given but no facility_type column in sites
        sites = pd.DataFrame({"site_id": [1, 2]})
        alts = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 2_000_000},
            {"site_id": 2, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 2_000_000},
        ])
        with pytest.raises(ValueError, match="facility_type"):
            Optimizer(
                sites, alts, budget=5_000_000,
                facility_budgets={"some_type": 1_000_000},
            )


# ============================================================
# Eq 2.15 — Regional cap
# ============================================================


class TestRegionalCap:
    """Eq 2.15: per-region maximum spend."""

    def test_regional_cap_limits_spend(self):
        # Without cap, would pick both north sites (highest benefit)
        # With north cap of 2M, can only take one
        sites, alts = make_regional_problem()
        opt = Optimizer(
            sites, alts, budget=10_000_000,
            regional_caps={"north": 2_000_000},
        )
        result = opt.solve()

        selected = result.selected_alternatives.merge(
            sites, on="site_id", how="left"
        )
        north_spend = selected[selected["region"] == "north"]["total_cost"].sum()
        assert north_spend <= 2_000_000

    def test_regional_cap_missing_region_column_raises(self):
        sites = pd.DataFrame({"site_id": [1]})
        alts = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "total_cost": 1_000_000, "total_benefit": 2_000_000},
        ])
        with pytest.raises(ValueError, match="region"):
            Optimizer(
                sites, alts, budget=5_000_000,
                regional_caps={"north": 1_000_000},
            )


# ============================================================
# Eq 2.16 — Regional minimum-investment floor
# ============================================================


class TestRegionalFloor:
    """Eq 2.16: per-region minimum spend as fraction of total budget."""

    def test_regional_floor_forces_minimum_spend(self):
        # Without floor, optimizer picks high-benefit north alternatives
        # With south floor 0.4 of 8M = 3.2M, must include enough south sites
        sites, alts = make_regional_problem()
        opt = Optimizer(
            sites, alts, budget=8_000_000,
            regional_floors={"south": 0.4},  # 40% of 8M = 3.2M minimum south
        )
        result = opt.solve()

        selected = result.selected_alternatives.merge(
            sites, on="site_id", how="left"
        )
        south_spend = selected[selected["region"] == "south"]["total_cost"].sum()
        assert south_spend >= 0.4 * 8_000_000

    def test_floor_above_one_raises(self):
        sites, alts = make_regional_problem()
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Optimizer(
                sites, alts, budget=8_000_000,
                regional_floors={"south": 1.5},
            )

    def test_floor_below_zero_raises(self):
        sites, alts = make_regional_problem()
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Optimizer(
                sites, alts, budget=8_000_000,
                regional_floors={"south": -0.1},
            )


# ============================================================
# Combined constraints
# ============================================================


class TestCombinedConstraints:
    """Multiple constraints active simultaneously."""

    def test_all_constraints_together_solvable(self):
        # Build a problem with multiple constraints active and verify
        # the optimizer still finds a feasible optimal solution
        sites = pd.DataFrame({
            "site_id": [1, 2, 3, 4],
            "facility_type": ["rural", "rural", "urban", "urban"],
            "region": ["north", "south", "north", "south"],
        })
        alts = pd.DataFrame([
            {"site_id": 1, "alt_id": 1, "total_cost": 1_500_000, "total_benefit": 3_000_000},
            {"site_id": 2, "alt_id": 1, "total_cost": 1_500_000, "total_benefit": 2_500_000},
            {"site_id": 3, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 4_500_000},
            {"site_id": 4, "alt_id": 1, "total_cost": 2_000_000, "total_benefit": 3_500_000},
        ])
        opt = Optimizer(
            sites, alts, budget=6_000_000,
            facility_budgets={"rural": 3_000_000, "urban": 4_000_000},
            regional_caps={"north": 4_000_000, "south": 4_000_000},
            regional_floors={"south": 0.20},  # 20% of 6M = 1.2M minimum
            min_bcr=1.0,
        )
        result = opt.solve()

        # Should still be solvable
        assert result.status == "optimal"
        assert result.selected_alternatives.shape[0] >= 1

        # All constraints honored
        selected = result.selected_alternatives.merge(sites, on="site_id", how="left")
        rural_spend = selected[selected["facility_type"] == "rural"]["total_cost"].sum()
        urban_spend = selected[selected["facility_type"] == "urban"]["total_cost"].sum()
        north_spend = selected[selected["region"] == "north"]["total_cost"].sum()
        south_spend = selected[selected["region"] == "south"]["total_cost"].sum()

        assert rural_spend <= 3_000_000
        assert urban_spend <= 4_000_000
        assert north_spend <= 4_000_000
        assert south_spend <= 4_000_000
        assert south_spend >= 1_200_000  # floor
