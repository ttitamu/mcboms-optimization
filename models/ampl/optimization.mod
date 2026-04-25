# =====================================================================
# MCBOMs Optimization Layer - AMPL model
# Mathematical formulation per Chapter 2 of the MCBOMs Task 4 report.
# This file encodes Eq 2.4 - 2.10 (project-level) and Eq 2.11 - 2.16
# (network-level extensions). Benefit and cost values are computed in
# the corresponding instance file (e.g., harwood_50m.mod includes this
# file plus the benefit-side equations Eq 2.18, 2.21).
#
# Optional and network-level constraints are activated by populating
# the corresponding sets in the .dat file. When the sets are empty,
# the constraints are vacuously satisfied.
# =====================================================================

# ---------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------

set PROJECTS;
set ALTERNATIVES{i in PROJECTS};

# Optional: pairs (i, j, ip, jp) where alternative (i,j) requires (ip,jp)
set DEPENDENCIES dimen 4 default {};

# Optional: pairs (i, j, ip, jp) that conflict pairwise
set CONFLICTS dimen 4 default {};

# Optional: facility-type partitioning of projects
set FACILITY_TYPES default {};
set FacilityProjects{m in FACILITY_TYPES} within PROJECTS default {};

# Optional: regional partitioning of projects
set REGIONS default {};
set RegionProjects{r in REGIONS} within PROJECTS default {};

# ---------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------

param B_total;
param Benefit{i in PROJECTS, j in ALTERNATIVES[i]};
param Cost{i in PROJECTS, j in ALTERNATIVES[i]};
param Cost_disc{i in PROJECTS, j in ALTERNATIVES[i]} default Cost[i,j];

# Optional thresholds
param theta default 0;                              # min BCR; 0 disables
param B_facility{m in FACILITY_TYPES} default Infinity;
param B_region_cap{r in REGIONS} default Infinity;
param beta_region{r in REGIONS} default 0;

# ---------------------------------------------------------------------
# Decision variables (Eq 2.7)
# ---------------------------------------------------------------------

var x{i in PROJECTS, j in ALTERNATIVES[i]} binary;

# ---------------------------------------------------------------------
# Objective (Eq 2.4)
#   max sum_{i,j} (B_ij - C_ij^disc) * x_ij
# ---------------------------------------------------------------------

maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost_disc[i,j]) * x[i,j];

# ---------------------------------------------------------------------
# Core constraints
# ---------------------------------------------------------------------

# Eq 2.5 - total budget
subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

# Eq 2.6 - mutual exclusivity
subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;

# ---------------------------------------------------------------------
# Optional constraints (Eq 2.8 - 2.10)
# ---------------------------------------------------------------------

# Eq 2.8 - dependency
subject to Dependency {(i,j,ip,jp) in DEPENDENCIES}:
    x[i,j] <= x[ip,jp];

# Eq 2.9 - cross-project exclusivity
subject to CrossExclusivity {(i,j,ip,jp) in CONFLICTS}:
    x[i,j] + x[ip,jp] <= 1;

# Eq 2.10 - minimum benefit-cost ratio (per project, when theta > 0)
subject to MinBCR {i in PROJECTS: theta > 0}:
    sum {j in ALTERNATIVES[i]} Benefit[i,j] * x[i,j]
      >= theta * sum {j in ALTERNATIVES[i]} Cost[i,j] * x[i,j];

# ---------------------------------------------------------------------
# Network-level constraints (Eq 2.14 - 2.16)
# ---------------------------------------------------------------------

# Eq 2.14 - facility-type sub-budget
subject to FacilityBudget {m in FACILITY_TYPES}:
    sum {i in FacilityProjects[m], j in ALTERNATIVES[i]} Cost[i,j] * x[i,j]
      <= B_facility[m];

# Eq 2.15 - regional cap
subject to RegionalCap {r in REGIONS}:
    sum {i in RegionProjects[r], j in ALTERNATIVES[i]} Cost[i,j] * x[i,j]
      <= B_region_cap[r];

# Eq 2.16 - regional minimum-investment floor
subject to RegionalFloor {r in REGIONS}:
    sum {i in RegionProjects[r], j in ALTERNATIVES[i]} Cost[i,j] * x[i,j]
      >= beta_region[r] * B_total;
