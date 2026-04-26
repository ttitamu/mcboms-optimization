"""MILP optimizer for transportation infrastructure investment decisions.

The optimizer maximizes net benefit subject to budget, mutual exclusivity,
dependency, conflict, BCR, facility-budget, and regional balance constraints.

Backend selection
-----------------
Two solver backends are supported:

* gurobi — preferred when available; commercial-grade, handles large instances
* pulp   — uses CBC, an open-source solver; good for problems up to a few
           thousand binary variables, no license required

`Optimizer.solve()` auto-detects what's available and picks gurobi over pulp.
Pass `solver="pulp"` to force the open-source backend (useful in environments
without a Gurobi license, e.g. Google Colab).

References
----------
Harwood et al. (2003); Banihashemi (2007).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from mcboms.utils.economics import calculate_discount_factors

logger = logging.getLogger(__name__)


def _gurobi_available() -> bool:
    """Return True if gurobipy is importable. Doesn't check license validity —
    that's only known at solve time."""
    try:
        import gurobipy  # noqa: F401
        return True
    except ImportError:
        return False


def _pulp_available() -> bool:
    """Return True if pulp is importable."""
    try:
        import pulp  # noqa: F401
        return True
    except ImportError:
        return False


@dataclass
class OptimizationResult:
    """Container for optimization results.

    Attributes
    ----------
    status : str
        Solver status — typically 'optimal', 'time_limit', or an error string.
    objective_value : float
        Value of the maximized objective at the solution.
    net_benefit : float
        Total net benefit of selected alternatives. Per the Harwood convention
        this equals (total benefit) - (safety improvement cost) when the input
        DataFrame includes a `safety_improvement_cost` column; otherwise
        (total benefit) - (total cost).
    total_cost, total_benefit : float
        Aggregates over selected alternatives.
    selected_alternatives : pd.DataFrame
        One row per selected (site, alternative) pair, with cost/benefit columns.
    budget_utilization : float
        total_cost / config.budget; in [0, 1].
    solve_time : float
        Wall-clock seconds the backend spent in `optimize()` / `solve()`.
    gap : float
        Final MIP gap when reported by the backend (0.0 if not available).
    sites_improved : int
        Number of sites where a non-trivial alternative was selected (alt_id != 0).
    sites_deferred : int
        Sites where no alternative was selected (do-nothing).
    solver_used : str
        Which backend produced this result: 'gurobi' or 'pulp'.
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
    solver_used: str = ""

    def __repr__(self) -> str:
        return (
            f"OptimizationResult(status={self.status!r}, "
            f"net_benefit=${self.net_benefit:,.0f}, "
            f"sites_improved={self.sites_improved}, "
            f"solver={self.solver_used or '?'})"
        )

    def summary(self) -> str:
        """Human-readable summary of the result.

        Returns a multi-line string suitable for printing or logging.
        """
        budget_used_pct = self.budget_utilization * 100

        out = []
        out.append("MCBOMs Optimization Result")
        out.append("=" * 50)
        out.append(f"Status                {self.status}")
        if self.solver_used:
            out.append(f"Solver                {self.solver_used}")
        out.append(f"Solve time            {self.solve_time:.2f} s")
        if self.gap > 0:
            out.append(f"Final MIP gap         {self.gap:.4%}")
        out.append("")

        out.append("Selection")
        out.append("-" * 50)
        out.append(f"Sites improved        {self.sites_improved}")
        out.append(f"Sites deferred        {self.sites_deferred}")
        out.append("")

        out.append("Financial")
        out.append("-" * 50)
        out.append(f"Total cost            ${self.total_cost:>15,.0f}")
        out.append(f"Total benefit         ${self.total_benefit:>15,.0f}")
        out.append(f"Net benefit           ${self.net_benefit:>15,.0f}")
        out.append(f"Budget utilization    {budget_used_pct:>15.1f}%")
        out.append("")

        if len(self.selected_alternatives) > 0:
            out.append("Selected alternatives")
            out.append("-" * 50)
            df = self.selected_alternatives.copy()
            # Format currency columns inline for readability.
            for col in ("total_cost", "total_benefit", "net_benefit",
                        "safety_improvement_cost", "resurfacing_cost",
                        "safety_benefit", "ops_benefit", "ccm_benefit"):
                if col in df.columns:
                    df[col] = df[col].apply(lambda v: f"${v:,.0f}" if pd.notna(v) else "")
            out.append(df.to_string(index=False))

        return "\n".join(out)

    def to_markdown(self) -> str:
        """Return the same summary as a Markdown-formatted string,
        suitable for embedding in notebooks or reports."""
        lines = [
            "## MCBOMs Optimization Result",
            "",
            f"- **Status:** `{self.status}`",
        ]
        if self.solver_used:
            lines.append(f"- **Solver:** `{self.solver_used}`")
        lines += [
            f"- **Solve time:** {self.solve_time:.2f} s",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Sites improved | {self.sites_improved} |",
            f"| Sites deferred | {self.sites_deferred} |",
            f"| Total cost | ${self.total_cost:,.0f} |",
            f"| Total benefit | ${self.total_benefit:,.0f} |",
            f"| Net benefit | **${self.net_benefit:,.0f}** |",
            f"| Budget utilization | {self.budget_utilization:.1%} |",
        ]
        if len(self.selected_alternatives) > 0:
            lines += ["", "### Selected alternatives", "",
                      self.selected_alternatives.to_markdown(index=False)]
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
        
        self._model: Any = None
        self._variables: dict[tuple[int, int], Any] = {}
        self._solver_used: str | None = None

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
    
    def _build_model_gurobi(self) -> None:
        """Build the model with gurobipy."""
        import gurobipy as gp
        from gurobipy import GRB

        self._model = gp.Model("MCBOMs")
        self._model.Params.TimeLimit = self.config.time_limit
        self._model.Params.MIPGap = self.config.mip_gap
        if not self.config.verbose:
            self._model.Params.OutputFlag = 0
        
        # x[i,j] = 1 if alternative j is selected at site i
        self._variables = {}
        for _, row in self.alternatives.iterrows():
            site_id = row["site_id"]
            alt_id = row["alt_id"]
            self._variables[(site_id, alt_id)] = self._model.addVar(
                vtype=GRB.BINARY, name=f"x_{site_id}_{alt_id}"
            )

        # Objective coefficient: pre-computed objective_value if available,
        # otherwise total_benefit - safety_improvement_cost (Harwood convention).
        def get_objective_coeff(row):
            if "objective_value" in row.index:
                return row["objective_value"]
            return row["total_benefit"] - row.get("safety_improvement_cost", row["total_cost"])

        obj_expr = gp.quicksum(
            get_objective_coeff(row) * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.setObjective(obj_expr, GRB.MAXIMIZE)

        # Mutual exclusivity: at most one alternative per site.
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

        # Budget.
        budget_expr = gp.quicksum(
            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )
        self._model.addConstr(budget_expr <= self.config.budget, name="budget")

        # Dependencies: selecting (i,j) requires (ip,jp).
        for idx, (i, j, ip, jp) in enumerate(self.dependencies):
            self._model.addConstr(
                self._variables[(i, j)] <= self._variables[(ip, jp)],
                name=f"dependency_{idx}_{i}_{j}_requires_{ip}_{jp}"
            )
        
        # Conflicts: alternatives (i,j) and (ip,jp) cannot both be selected.
        for idx, (i, j, ip, jp) in enumerate(self.conflicts):
            self._model.addConstr(
                self._variables[(i, j)] + self._variables[(ip, jp)] <= 1,
                name=f"conflict_{idx}_{i}_{j}_vs_{ip}_{jp}"
            )

        # Minimum BCR per project. Linearized form: sum_j (B - theta*C) * x_ij >= 0.
        # Holds trivially when no alternative is selected at site i.
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

        # Facility-type sub-budgets.
        if self.facility_budgets:
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

        # Per-region spending caps.
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

        # Per-region minimum-investment floors (fraction of total budget).
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
    
    def _build_model_pulp(self) -> None:
        """Build the model with pulp (CBC backend)."""
        import pulp

        prob = pulp.LpProblem("MCBOMs", pulp.LpMaximize)

        # x[i,j] = 1 if alternative j is selected at site i
        self._variables = {}
        for _, row in self.alternatives.iterrows():
            site_id = row["site_id"]
            alt_id = row["alt_id"]
            self._variables[(site_id, alt_id)] = pulp.LpVariable(
                f"x_{site_id}_{alt_id}", cat="Binary"
            )

        def get_objective_coeff(row):
            if "objective_value" in row.index:
                return row["objective_value"]
            return row["total_benefit"] - row.get("safety_improvement_cost", row["total_cost"])

        prob += pulp.lpSum(
            get_objective_coeff(row) * self._variables[(row["site_id"], row["alt_id"])]
            for _, row in self.alternatives.iterrows()
        )

        # Mutual exclusivity.
        for site_id in self.sites["site_id"].unique():
            site_alts = self.alternatives[self.alternatives["site_id"] == site_id]
            if len(site_alts) > 0:
                prob += (
                    pulp.lpSum(
                        self._variables[(site_id, row["alt_id"])]
                        for _, row in site_alts.iterrows()
                    ) <= 1,
                    f"exclusivity_{site_id}",
                )

        # Budget.
        prob += (
            pulp.lpSum(
                row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                for _, row in self.alternatives.iterrows()
            ) <= self.config.budget,
            "budget",
        )

        # Dependencies.
        for idx, (i, j, ip, jp) in enumerate(self.dependencies):
            prob += (
                self._variables[(i, j)] <= self._variables[(ip, jp)],
                f"dependency_{idx}_{i}_{j}_requires_{ip}_{jp}",
            )

        # Conflicts.
        for idx, (i, j, ip, jp) in enumerate(self.conflicts):
            prob += (
                self._variables[(i, j)] + self._variables[(ip, jp)] <= 1,
                f"conflict_{idx}_{i}_{j}_vs_{ip}_{jp}",
            )

        # Minimum BCR per project.
        if self.min_bcr is not None:
            theta = self.min_bcr
            for site_id in self.sites["site_id"].unique():
                site_alts = self.alternatives[self.alternatives["site_id"] == site_id]
                if len(site_alts) > 0:
                    prob += (
                        pulp.lpSum(
                            (row["total_benefit"] - theta * row["total_cost"])
                            * self._variables[(site_id, row["alt_id"])]
                            for _, row in site_alts.iterrows()
                        ) >= 0,
                        f"min_bcr_{site_id}",
                    )

        # Facility-type sub-budgets.
        if self.facility_budgets:
            facility_lookup = dict(zip(self.sites["site_id"], self.sites["facility_type"]))
            for facility_type, sub_budget in self.facility_budgets.items():
                facility_alts = self.alternatives[
                    self.alternatives["site_id"].map(facility_lookup) == facility_type
                ]
                if len(facility_alts) > 0:
                    prob += (
                        pulp.lpSum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in facility_alts.iterrows()
                        ) <= sub_budget,
                        f"facility_budget_{facility_type}",
                    )

        # Per-region spending caps.
        if self.regional_caps:
            region_lookup = dict(zip(self.sites["site_id"], self.sites["region"]))
            for region, cap in self.regional_caps.items():
                region_alts = self.alternatives[
                    self.alternatives["site_id"].map(region_lookup) == region
                ]
                if len(region_alts) > 0:
                    prob += (
                        pulp.lpSum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in region_alts.iterrows()
                        ) <= cap,
                        f"regional_cap_{region}",
                    )

        # Per-region minimum-investment floors.
        if self.regional_floors:
            region_lookup = dict(zip(self.sites["site_id"], self.sites["region"]))
            for region, fraction in self.regional_floors.items():
                region_alts = self.alternatives[
                    self.alternatives["site_id"].map(region_lookup) == region
                ]
                if len(region_alts) > 0:
                    minimum_spend = fraction * self.config.budget
                    prob += (
                        pulp.lpSum(
                            row["total_cost"] * self._variables[(row["site_id"], row["alt_id"])]
                            for _, row in region_alts.iterrows()
                        ) >= minimum_spend,
                        f"regional_floor_{region}",
                    )

        self._model = prob

    def solve(self, solver: str | None = None) -> OptimizationResult:
        """Solve the optimization problem.

        Parameters
        ----------
        solver : {'gurobi', 'pulp', None}, optional
            Backend to use. None (default) auto-detects: prefers gurobi
            if installed, falls back to pulp+CBC.

        Returns
        -------
        OptimizationResult
        """
        backend = self._select_solver(solver)
        self._solver_used = backend

        if backend == "gurobi":
            self._build_model_gurobi()
            return self._solve_gurobi()
        if backend == "pulp":
            self._build_model_pulp()
            return self._solve_pulp()
        raise RuntimeError(f"Unknown solver backend: {backend}")

    def _select_solver(self, requested: str | None) -> str:
        """Pick a solver backend. Honor explicit request if available; otherwise
        prefer gurobi over pulp."""
        if requested == "gurobi":
            if not _gurobi_available():
                raise RuntimeError(
                    "solver='gurobi' requested but gurobipy is not installed"
                )
            return "gurobi"
        if requested == "pulp":
            if not _pulp_available():
                raise RuntimeError(
                    "solver='pulp' requested but pulp is not installed"
                )
            return "pulp"
        if requested is not None:
            raise ValueError(f"solver must be 'gurobi', 'pulp', or None; got {requested!r}")
        # Auto-detect.
        if _gurobi_available():
            return "gurobi"
        if _pulp_available():
            return "pulp"
        raise RuntimeError(
            "No solver available. Install gurobipy (commercial) or pulp (open source)."
        )

    def _solve_gurobi(self) -> OptimizationResult:
        from gurobipy import GRB

        self._model.optimize()
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
            raise RuntimeError("Optimization problem is infeasible")
        if status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            raise RuntimeError(f"Optimization failed: {status_str}")
        return self._extract_results_gurobi(status_str)

    def _solve_pulp(self) -> OptimizationResult:
        import pulp

        solver = pulp.PULP_CBC_CMD(
            msg=1 if self.config.verbose else 0,
            timeLimit=self.config.time_limit,
            gapRel=self.config.mip_gap,
        )
        self._model.solve(solver)

        status_str = pulp.LpStatus[self._model.status].lower()
        # CBC returns "Not Solved" when interrupted; normalize names.
        status_map = {
            "optimal": "optimal",
            "infeasible": "infeasible",
            "unbounded": "unbounded",
            "not solved": "interrupted",
            "undefined": "unknown",
        }
        status_str = status_map.get(status_str, status_str)
        if status_str == "infeasible":
            raise RuntimeError("Optimization problem is infeasible")
        if status_str not in ("optimal", "time_limit"):
            # CBC doesn't have a separate "time_limit" status; if a solution was
            # found within the limit, treat as optimal-ish.
            if pulp.value(self._model.objective) is None:
                raise RuntimeError(f"Optimization failed: {status_str}")
        return self._extract_results_pulp(status_str)

    def _common_extract(self, selected: list[dict]) -> tuple[pd.DataFrame, float, float, float, int, int]:
        """Shared post-processing of selected alternatives."""
        selected_df = pd.DataFrame(selected)
        total_cost = selected_df["total_cost"].sum() if len(selected_df) > 0 else 0
        total_benefit = selected_df["total_benefit"].sum() if len(selected_df) > 0 else 0
        if len(selected_df) > 0 and "safety_improvement_cost" in selected_df.columns:
            net_benefit = total_benefit - selected_df["safety_improvement_cost"].sum()
        else:
            net_benefit = total_benefit - total_cost
        sites_improved = len(selected_df[selected_df["alt_id"] != 0]) if len(selected_df) > 0 else 0
        sites_deferred = len(self.sites) - len(selected_df)
        return selected_df, total_cost, total_benefit, net_benefit, sites_improved, sites_deferred

    def _selected_alternative_row(self, site_id, alt_id) -> dict:
        """Build a row dict for a selected alternative, copying optional columns."""
        alt_row = self.alternatives[
            (self.alternatives["site_id"] == site_id)
            & (self.alternatives["alt_id"] == alt_id)
        ].iloc[0]
        row_data = {
            "site_id": site_id,
            "alt_id": alt_id,
            "description": alt_row.get("description", ""),
            "total_cost": alt_row["total_cost"],
            "total_benefit": alt_row["total_benefit"],
            "net_benefit": alt_row["total_benefit"] - alt_row["total_cost"],
        }
        for col in ["resurfacing_cost", "safety_improvement_cost",
                    "safety_benefit", "ops_benefit", "ccm_benefit"]:
            if col in alt_row:
                row_data[col] = alt_row[col]
        return row_data

    def _extract_results_gurobi(self, status: str) -> OptimizationResult:
        selected = [
            self._selected_alternative_row(site_id, alt_id)
            for (site_id, alt_id), var in self._variables.items()
            if var.X > 0.5
        ]
        selected_df, total_cost, total_benefit, net_benefit, sites_improved, sites_deferred = (
            self._common_extract(selected)
        )
        return OptimizationResult(
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
            solver_used="gurobi",
        )

    def _extract_results_pulp(self, status: str) -> OptimizationResult:
        import pulp

        selected = [
            self._selected_alternative_row(site_id, alt_id)
            for (site_id, alt_id), var in self._variables.items()
            if var.value() is not None and var.value() > 0.5
        ]
        selected_df, total_cost, total_benefit, net_benefit, sites_improved, sites_deferred = (
            self._common_extract(selected)
        )
        obj_val = pulp.value(self._model.objective) or 0.0
        return OptimizationResult(
            status=status,
            objective_value=obj_val,
            net_benefit=net_benefit,
            total_cost=total_cost,
            total_benefit=total_benefit,
            selected_alternatives=selected_df,
            budget_utilization=total_cost / self.config.budget if self.config.budget > 0 else 0,
            solve_time=self._model.solutionTime if hasattr(self._model, "solutionTime") else 0,
            gap=0,  # CBC doesn't expose final MIP gap directly.
            sites_improved=sites_improved,
            sites_deferred=sites_deferred,
            solver_used="pulp",
        )
    
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
