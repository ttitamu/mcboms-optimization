"""
Core MILP Optimizer for MCBOMs.

This module implements the Mixed-Integer Linear Programming (MILP) formulation
for optimizing transportation infrastructure investment decisions.

Mathematical Formulation:
    
    Objective:
        max Σᵢ Σⱼ (Bᵢⱼ - Cᵢⱼ) × xᵢⱼ
    
    Subject to:
        Σⱼ xᵢⱼ ≤ 1           ∀i  (mutual exclusivity)
        Σᵢ Σⱼ Cᵢⱼ × xᵢⱼ ≤ B      (budget constraint)
        xᵢⱼ ∈ {0, 1}         ∀i,j (binary)

References:
    - Harwood et al. (2003). Systemwide optimization of safety improvements
      for resurfacing, restoration, or rehabilitation projects.
    - Banihashemi (2007). Optimization of highway safety and operation by
      using crash prediction models with accident modification factors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import gurobipy as gp

from mcboms.utils.economics import calculate_discount_factors

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Container for optimization results.
    
    Attributes:
        status: Solver status (optimal, infeasible, etc.)
        objective_value: Optimal objective function value
        net_benefit: Total net benefit (benefits - costs)
        total_cost: Total cost of selected alternatives
        total_benefit: Total benefit of selected alternatives
        selected_alternatives: DataFrame of selected alternatives by site
        budget_utilization: Fraction of budget used
        solve_time: Solver time in seconds
        gap: Optimality gap (for MIP)
    """
    status: str
    objective_value: float
    net_benefit: float
    total_cost: float
    total_benefit: float
    selected_alternatives: pd.DataFrame
    budget_utilization: float
    solve_time: float
    gap: float = 0.0
    sites_improved: int = 0
    sites_deferred: int = 0
    
    def __repr__(self) -> str:
        return (
            f"OptimizationResult(\n"
            f"  status='{self.status}',\n"
            f"  net_benefit=${self.net_benefit:,.0f},\n"
            f"  total_cost=${self.total_cost:,.0f},\n"
            f"  budget_utilization={self.budget_utilization:.1%},\n"
            f"  sites_improved={self.sites_improved},\n"
            f"  solve_time={self.solve_time:.3f}s\n"
            f")"
        )
    
    def summary(self) -> str:
        """Generate a summary report of optimization results."""
        lines = [
            "=" * 60,
            "MCBOMs OPTIMIZATION RESULTS",
            "=" * 60,
            f"Status: {self.status}",
            f"Solve Time: {self.solve_time:.3f} seconds",
            f"Optimality Gap: {self.gap:.4%}",
            "",
            "FINANCIAL SUMMARY",
            "-" * 40,
            f"Total Cost:        ${self.total_cost:>15,.0f}",
            f"Total Benefit:     ${self.total_benefit:>15,.0f}",
            f"Net Benefit:       ${self.net_benefit:>15,.0f}",
            f"Budget Utilization: {self.budget_utilization:>14.1%}",
            "",
            "PROJECT SUMMARY",
            "-" * 40,
            f"Sites Improved:    {self.sites_improved:>15d}",
            f"Sites Deferred:    {self.sites_deferred:>15d}",
            "=" * 60,
        ]
        return "\n".join(lines)


@dataclass
class OptimizerConfig:
    """Configuration for the optimizer.
    
    Attributes:
        budget: Total available budget ($)
        discount_rate: Annual discount rate (e.g., 0.07 for 7%)
        analysis_horizon: Analysis period in years
        time_limit: Maximum solver time in seconds
        mip_gap: Acceptable optimality gap
        verbose: Whether to print solver output
    """
    budget: float
    discount_rate: float = 0.07
    analysis_horizon: int = 20
    time_limit: float = 300.0
    mip_gap: float = 0.0001
    verbose: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.budget <= 0:
            raise ValueError(f"Budget must be positive, got {self.budget}")
        if not 0 < self.discount_rate < 1:
            raise ValueError(f"Discount rate must be between 0 and 1, got {self.discount_rate}")
        if self.analysis_horizon <= 0:
            raise ValueError(f"Analysis horizon must be positive, got {self.analysis_horizon}")


class Optimizer:
    """MILP Optimizer for MCBOMs framework.
    
    This class implements the core optimization engine using Gurobi
    to solve the project selection problem.
    
    Example:
        >>> optimizer = Optimizer(
        ...     sites=sites_df,
        ...     alternatives=alternatives_df,
        ...     budget=10_000_000
        ... )
        >>> results = optimizer.solve()
        >>> print(results.summary())
    
    Attributes:
        sites: DataFrame containing site characteristics
        alternatives: DataFrame containing improvement alternatives
        config: Optimizer configuration
    """
    
    def __init__(
        self,
        sites: pd.DataFrame,
        alternatives: pd.DataFrame,
        budget: float,
        discount_rate: float = 0.07,
        analysis_horizon: int = 20,
        # Optional constraints (Eq 2.8 - 2.10)
        dependencies: list[tuple[int, int, int, int]] | None = None,
        conflicts: list[tuple[int, int, int, int]] | None = None,
        min_bcr: float | None = None,
        # Network-level constraints (Eq 2.14 - 2.16)
        facility_budgets: dict[str, float] | None = None,
        regional_caps: dict[str, float] | None = None,
        regional_floors: dict[str, float] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the optimizer.
        
        Args:
            sites: DataFrame with site characteristics. Required column: site_id.
                Optional columns: facility_type (for Eq 2.14), region (for Eq 2.15-2.16).
            alternatives: DataFrame with alternatives (site_id, alt_id, total_cost, total_benefit)
            budget: Total available budget
            discount_rate: Annual discount rate
            analysis_horizon: Analysis period in years
            dependencies: Optional. List of (i, j, ip, jp) tuples meaning alternative
                (i,j) requires alternative (ip,jp). Implements Eq 2.8.
            conflicts: Optional. List of (i, j, ip, jp) tuples meaning alternatives
                (i,j) and (ip,jp) cannot both be selected. Implements Eq 2.9.
            min_bcr: Optional. Minimum benefit-cost ratio per project. Implements
                Eq 2.10. Set to 1.0 to enforce benefit >= cost on each selection.
            facility_budgets: Optional. Dict mapping facility type to maximum spend.
                Requires sites DataFrame to have 'facility_type' column.
                Implements Eq 2.14.
            regional_caps: Optional. Dict mapping region to maximum spend.
                Requires sites DataFrame to have 'region' column.
                Implements Eq 2.15.
            regional_floors: Optional. Dict mapping region to minimum-investment
                fraction (e.g., 0.20 = 20% of total budget). Requires sites
                DataFrame to have 'region' column. Implements Eq 2.16.
            **kwargs: Additional configuration options for OptimizerConfig
                (time_limit, mip_gap, verbose).
        """
        self.sites = sites
        self.alternatives = alternatives
        self.config = OptimizerConfig(
            budget=budget,
            discount_rate=discount_rate,
            analysis_horizon=analysis_horizon,
            **kwargs,
        )
        
        # Optional constraints (Eq 2.8 - 2.10)
        self.dependencies = dependencies or []
        self.conflicts = conflicts or []
        self.min_bcr = min_bcr
        
        # Network-level constraints (Eq 2.14 - 2.16)
        self.facility_budgets = facility_budgets or {}
        self.regional_caps = regional_caps or {}
        self.regional_floors = regional_floors or {}
        
        self._model: gp.Model | None = None
        self._variables: dict[tuple[int, int], Any] = {}
        
        # Validate inputs
        self._validate_inputs()
        
        logger.info(
            f"Optimizer initialized with {len(sites)} sites, "
            f"{len(alternatives)} alternatives, budget=${budget:,.0f}"
        )
        if self.dependencies:
            logger.info(f"  Eq 2.8 (dependencies): {len(self.dependencies)} pairs")
        if self.conflicts:
            logger.info(f"  Eq 2.9 (conflicts): {len(self.conflicts)} pairs")
        if self.min_bcr is not None:
            logger.info(f"  Eq 2.10 (min BCR): {self.min_bcr}")
        if self.facility_budgets:
            logger.info(f"  Eq 2.14 (facility budgets): {len(self.facility_budgets)} types")
        if self.regional_caps:
            logger.info(f"  Eq 2.15 (regional caps): {len(self.regional_caps)} regions")
        if self.regional_floors:
            logger.info(f"  Eq 2.16 (regional floors): {len(self.regional_floors)} regions")
    
    def _validate_inputs(self) -> None:
        """Validate input data."""
        required_site_cols = {"site_id"}
        required_alt_cols = {"site_id", "alt_id", "total_cost", "total_benefit"}
        
        missing_site = required_site_cols - set(self.sites.columns)
        if missing_site:
            raise ValueError(f"Sites DataFrame missing columns: {missing_site}")
        
        missing_alt = required_alt_cols - set(self.alternatives.columns)
        if missing_alt:
            raise ValueError(f"Alternatives DataFrame missing columns: {missing_alt}")
        
        # Check all sites have at least one alternative
        site_ids_in_sites = set(self.sites["site_id"])
        site_ids_in_alts = set(self.alternatives["site_id"])
        
        missing = site_ids_in_sites - site_ids_in_alts
        if missing:
            logger.warning(f"Sites without alternatives: {missing}")
        
        # Validate that facility_type column exists if facility_budgets are used
        if self.facility_budgets and "facility_type" not in self.sites.columns:
            raise ValueError(
                "facility_budgets specified (Eq 2.14) but sites DataFrame "
                "lacks 'facility_type' column. Add a 'facility_type' column to "
                "sites with values matching the keys of facility_budgets."
            )
        if self.facility_budgets:
            site_facility_types = set(self.sites["facility_type"].unique())
            unknown_facilities = set(self.facility_budgets.keys()) - site_facility_types
            if unknown_facilities:
                logger.warning(
                    f"facility_budgets references unknown facility types "
                    f"(no sites match): {unknown_facilities}. Constraints will be "
                    f"vacuous for these."
                )
        
        # Validate that region column exists if regional caps/floors are used
        if (self.regional_caps or self.regional_floors) and "region" not in self.sites.columns:
            raise ValueError(
                "regional_caps or regional_floors specified (Eq 2.15-2.16) but "
                "sites DataFrame lacks 'region' column. Add a 'region' column to "
                "sites with values matching the keys of these dicts."
            )
        if self.regional_caps or self.regional_floors:
            site_regions = set(self.sites["region"].unique())
            specified_regions = set(self.regional_caps.keys()) | set(self.regional_floors.keys())
            unknown_regions = specified_regions - site_regions
            if unknown_regions:
                logger.warning(
                    f"regional constraints reference unknown regions "
                    f"(no sites match): {unknown_regions}. Constraints will be "
                    f"vacuous for these."
                )
        
        # Validate min_bcr is positive if specified
        if self.min_bcr is not None and self.min_bcr < 0:
            raise ValueError(f"min_bcr must be >= 0, got {self.min_bcr}")
        
        # Validate regional_floors fractions are in [0, 1]
        for region, fraction in self.regional_floors.items():
            if not 0 <= fraction <= 1:
                raise ValueError(
                    f"regional_floors[{region!r}] = {fraction} must be in [0, 1]. "
                    f"This is the minimum FRACTION of total budget."
                )
        
        # Validate dependency and conflict tuples reference valid (i, j) pairs
        valid_pairs = set(zip(self.alternatives["site_id"], self.alternatives["alt_id"]))
        for dep in self.dependencies:
            if len(dep) != 4:
                raise ValueError(
                    f"Dependency must be 4-tuple (i, j, ip, jp), got {dep}"
                )
            i, j, ip, jp = dep
            if (i, j) not in valid_pairs or (ip, jp) not in valid_pairs:
                raise ValueError(
                    f"Dependency {dep} references unknown alternative pair"
                )
        for conf in self.conflicts:
            if len(conf) != 4:
                raise ValueError(
                    f"Conflict must be 4-tuple (i, j, ip, jp), got {conf}"
                )
            i, j, ip, jp = conf
            if (i, j) not in valid_pairs or (ip, jp) not in valid_pairs:
                raise ValueError(
                    f"Conflict {conf} references unknown alternative pair"
                )
    
    def _build_model(self) -> None:
        """Build the Gurobi MILP model."""
        import gurobipy as gp
        from gurobipy import GRB
        
        logger.info("Building MILP model...")
        
        # Create model
        self._model = gp.Model("MCBOMs")
        
        # Set parameters
        self._model.Params.TimeLimit = self.config.time_limit
        self._model.Params.MIPGap = self.config.mip_gap
        if not self.config.verbose:
            self._model.Params.OutputFlag = 0
        
        # Create decision variables: x[i,j] = 1 if alternative j selected for site i
        self._variables = {}
        for _, row in self.alternatives.iterrows():
            site_id = row["site_id"]
            alt_id = row["alt_id"]
            var_name = f"x_{site_id}_{alt_id}"
            self._variables[(site_id, alt_id)] = self._model.addVar(
                vtype=GRB.BINARY, name=var_name
            )
        
        # Objective: Maximize net benefit
        # Per Harwood (2003): NBjk = PSBjk + PTOBjk + PNRjk - PRPjk - CCjk
        # If objective_value column exists (includes penalties), use it
        # Otherwise fall back to total_benefit - safety_improvement_cost
        def get_objective_coeff(row):
            if "objective_value" in row.index:
                return row["objective_value"]
            else:
                return row["total_benefit"] - row.get("safety_improvement_cost", row["total_cost"])
        
        obj_expr = gp.quicksum(
            get_objective_coeff(row) * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.setObjective(obj_expr, GRB.MAXIMIZE)
        
        # Constraint 1: Mutual exclusivity - at most one alternative per site
        for site_id in self.sites["site_id"].unique():
            site_alts = self.alternatives[self.alternatives["site_id"] == site_id]
            if len(site_alts) > 0:
                self._model.addConstr(
                    gp.quicksum(
                        self._variables[(site_id, row["alt_id"])]
                        for _, row in site_alts.iterrows()
                    ) <= 1,
                    name=f"exclusivity_{site_id}"
                )
        
        # Constraint 2: Budget constraint (Eq 2.5 — total budget)
        budget_expr = gp.quicksum(
            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.addConstr(budget_expr <= self.config.budget, name="budget")
        
        # ----------------------------------------------------------------
        # Optional constraints (Eq 2.8 - 2.10)
        # ----------------------------------------------------------------
        
        # Eq 2.8 — Dependency: x_ij <= x_i'j' for each (i,j,i',j') in dependencies
        # Selecting alternative (i,j) requires selecting alternative (ip,jp).
        for idx, (i, j, ip, jp) in enumerate(self.dependencies):
            self._model.addConstr(
                self._variables[(i, j)] <= self._variables[(ip, jp)],
                name=f"dependency_{idx}_{i}_{j}_requires_{ip}_{jp}"
            )
        
        # Eq 2.9 — Cross-project exclusivity: x_ij + x_i'j' <= 1
        # Alternatives (i,j) and (ip,jp) cannot both be selected.
        for idx, (i, j, ip, jp) in enumerate(self.conflicts):
            self._model.addConstr(
                self._variables[(i, j)] + self._variables[(ip, jp)] <= 1,
                name=f"conflict_{idx}_{i}_{j}_vs_{ip}_{jp}"
            )
        
        # Eq 2.10 — Minimum BCR per project
        # If a project is selected (sum_j x_ij = 1), the chosen alternative's
        # benefit must meet theta * cost. Linearized as:
        #   sum_j (B_ij - theta * C_ij) * x_ij >= 0  for each project i
        # When project not selected (all x_ij = 0), constraint is 0 >= 0 (satisfied).
        if self.min_bcr is not None:
            theta = self.min_bcr
            for site_id in self.sites["site_id"].unique():
                site_alts = self.alternatives[self.alternatives["site_id"] == site_id]
                if len(site_alts) > 0:
                    self._model.addConstr(
                        gp.quicksum(
                            (row["total_benefit"] - theta * row["total_cost"])
                            * self._variables[(site_id, row["alt_id"])]
                            for _, row in site_alts.iterrows()
                        ) >= 0,
                        name=f"min_bcr_{site_id}"
                    )
        
        # ----------------------------------------------------------------
        # Network-level constraints (Eq 2.14 - 2.16)
        # ----------------------------------------------------------------
        
        # Eq 2.14 — Facility-type sub-budget
        # sum over (i,j) where facility_type[i] = m of C_ij * x_ij <= B_m
        if self.facility_budgets:
            # Build site -> facility_type lookup
            facility_lookup = dict(zip(self.sites["site_id"], self.sites["facility_type"]))
            for facility_type, sub_budget in self.facility_budgets.items():
                facility_alts = self.alternatives[
                    self.alternatives["site_id"].map(facility_lookup) == facility_type
                ]
                if len(facility_alts) > 0:
                    self._model.addConstr(
                        gp.quicksum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in facility_alts.iterrows()
                        ) <= sub_budget,
                        name=f"facility_budget_{facility_type}"
                    )
        
        # Eq 2.15 — Regional cap
        # sum over (i,j) where region[i] = r of C_ij * x_ij <= B_r^cap
        if self.regional_caps:
            region_lookup = dict(zip(self.sites["site_id"], self.sites["region"]))
            for region, cap in self.regional_caps.items():
                region_alts = self.alternatives[
                    self.alternatives["site_id"].map(region_lookup) == region
                ]
                if len(region_alts) > 0:
                    self._model.addConstr(
                        gp.quicksum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in region_alts.iterrows()
                        ) <= cap,
                        name=f"regional_cap_{region}"
                    )
        
        # Eq 2.16 — Regional minimum-investment floor
        # sum over (i,j) where region[i] = r of C_ij * x_ij >= beta_r * B_total
        if self.regional_floors:
            region_lookup = dict(zip(self.sites["site_id"], self.sites["region"]))
            for region, fraction in self.regional_floors.items():
                region_alts = self.alternatives[
                    self.alternatives["site_id"].map(region_lookup) == region
                ]
                if len(region_alts) > 0:
                    minimum_spend = fraction * self.config.budget
                    self._model.addConstr(
                        gp.quicksum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in region_alts.iterrows()
                        ) >= minimum_spend,
                        name=f"regional_floor_{region}"
                    )
        
        self._model.update()
        
        logger.info(
            f"Model built: {self._model.NumVars} variables, "
            f"{self._model.NumConstrs} constraints"
        )
    
    def solve(self) -> OptimizationResult:
        """Solve the optimization problem.
        
        Returns:
            OptimizationResult containing the optimal solution.
        
        Raises:
            RuntimeError: If optimization fails.
        """
        from gurobipy import GRB
        
        # Build model if not already built
        if self._model is None:
            self._build_model()
        
        logger.info("Solving MILP...")
        
        # Solve
        self._model.optimize()
        
        # Check status
        status = self._model.Status
        status_map = {
            GRB.OPTIMAL: "optimal",
            GRB.INFEASIBLE: "infeasible",
            GRB.UNBOUNDED: "unbounded",
            GRB.TIME_LIMIT: "time_limit",
            GRB.INTERRUPTED: "interrupted",
        }
        status_str = status_map.get(status, f"unknown_{status}")
        
        if status == GRB.INFEASIBLE:
            logger.error("Model is infeasible")
            raise RuntimeError("Optimization problem is infeasible")
        
        if status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            logger.error(f"Optimization failed with status: {status_str}")
            raise RuntimeError(f"Optimization failed: {status_str}")
        
        # Extract results
        return self._extract_results(status_str)
    
    def _extract_results(self, status: str) -> OptimizationResult:
        """Extract results from solved model."""
        from gurobipy import GRB
        
        # Get selected alternatives
        selected = []
        for (site_id, alt_id), var in self._variables.items():
            if var.X > 0.5:  # Binary variable selected
                alt_row = self.alternatives[
                    (self.alternatives["site_id"] == site_id) &
                    (self.alternatives["alt_id"] == alt_id)
                ].iloc[0]
                row_data = {
                    "site_id": site_id,
                    "alt_id": alt_id,
                    "description": alt_row.get("description", ""),
                    "total_cost": alt_row["total_cost"],
                    "total_benefit": alt_row["total_benefit"],
                    "net_benefit": alt_row["total_benefit"] - alt_row["total_cost"],
                }
                # Add optional columns if present
                for col in ["resurfacing_cost", "safety_improvement_cost", 
                           "safety_benefit", "ops_benefit", "ccm_benefit"]:
                    if col in alt_row:
                        row_data[col] = alt_row[col]
                selected.append(row_data)
        
        selected_df = pd.DataFrame(selected)
        
        # Calculate totals
        total_cost = selected_df["total_cost"].sum() if len(selected_df) > 0 else 0
        total_benefit = selected_df["total_benefit"].sum() if len(selected_df) > 0 else 0
        
        # Net benefit per Harwood: total_benefit - safety_improvement_cost (not total_cost)
        if len(selected_df) > 0 and "safety_improvement_cost" in selected_df.columns:
            safety_cost = selected_df["safety_improvement_cost"].sum()
            net_benefit = total_benefit - safety_cost
        else:
            net_benefit = total_benefit - total_cost
        
        # Count sites
        sites_improved = len(selected_df[selected_df["alt_id"] != 0]) if len(selected_df) > 0 else 0
        total_sites = len(self.sites)
        sites_deferred = total_sites - len(selected_df)
        
        result = OptimizationResult(
            status=status,
            objective_value=self._model.ObjVal,
            net_benefit=net_benefit,
            total_cost=total_cost,
            total_benefit=total_benefit,
            selected_alternatives=selected_df,
            budget_utilization=total_cost / self.config.budget if self.config.budget > 0 else 0,
            solve_time=self._model.Runtime,
            gap=self._model.MIPGap if hasattr(self._model, "MIPGap") else 0,
            sites_improved=sites_improved,
            sites_deferred=sites_deferred,
        )
        
        logger.info(f"Optimization complete: {result}")
        
        return result
    
    def add_constraint(
        self,
        name: str,
        expression: Any,
        sense: str = "<=",
        rhs: float = 0,
    ) -> None:
        """Add a custom constraint to the model.
        
        Args:
            name: Constraint name
            expression: Left-hand side expression
            sense: Constraint sense ('<=', '>=', '==')
            rhs: Right-hand side value
        """
        if self._model is None:
            self._build_model()
        
        from gurobipy import GRB
        
        sense_map = {
            "<=": GRB.LESS_EQUAL,
            ">=": GRB.GREATER_EQUAL,
            "==": GRB.EQUAL,
        }
        
        self._model.addConstr(expression, sense_map[sense], rhs, name=name)
        logger.info(f"Added constraint: {name}")
    
    def get_variable(self, site_id: int, alt_id: int) -> Any:
        """Get a decision variable by site and alternative ID.
        
        Args:
            site_id: Site identifier
            alt_id: Alternative identifier
        
        Returns:
            Gurobi variable object
        """
        return self._variables.get((site_id, alt_id))


def solve_harwood_problem(
    sites: pd.DataFrame,
    alternatives: pd.DataFrame,
    budget: float,
    discount_rate: float = 0.04,  # Harwood uses 4%
) -> OptimizationResult:
    """Convenience function to solve Harwood-style problem.
    
    This function sets up the optimizer with parameters matching
    Harwood et al. (2003) for validation purposes.
    
    Args:
        sites: Site characteristics DataFrame
        alternatives: Alternatives DataFrame
        budget: Budget constraint
        discount_rate: Discount rate (default 4% per Harwood)
    
    Returns:
        OptimizationResult
    """
    optimizer = Optimizer(
        sites=sites,
        alternatives=alternatives,
        budget=budget,
        discount_rate=discount_rate,
        analysis_horizon=20,
        verbose=False,
    )
    return optimizer.solve()
