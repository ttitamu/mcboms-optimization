# MCBOMs Project-Level MILP Model
# Mathematical formulation per Chapter 2 of the MCBOMs Task 4 report
#
# Maximize total net benefit subject to a budget and at most one
# alternative per project. Optional constraints (dependency,
# cross-project exclusivity, minimum BCR) are commented out below
# and can be enabled when applicable data is provided.

# ------------------------------------------------------------------
# Sets
# ------------------------------------------------------------------

set PROJECTS;                       # candidate projects (sites, intersections)
set ALTERNATIVES{i in PROJECTS};    # alternatives available for project i
                                    # alternative 0 is do-nothing baseline

# ------------------------------------------------------------------
# Parameters
# ------------------------------------------------------------------

param B_total;                                                  # total program budget
param Benefit{i in PROJECTS, j in ALTERNATIVES[i]};             # PV total benefit
param Cost{i in PROJECTS, j in ALTERNATIVES[i]};                # PV total cost

# ------------------------------------------------------------------
# Decision variables
# ------------------------------------------------------------------

var x{i in PROJECTS, j in ALTERNATIVES[i]} binary;

# ------------------------------------------------------------------
# Objective: Eq. 2.4
# ------------------------------------------------------------------

maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost[i,j]) * x[i,j];

# ------------------------------------------------------------------
# Core constraints
# ------------------------------------------------------------------

# Eq. 2.5 - total budget
subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

# Eq. 2.6 - at most one alternative per project
subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;

# Eq. 2.7 - binary decision variables enforced by var declaration above

# ------------------------------------------------------------------
# Optional constraints (uncomment + populate corresponding sets/params
# when applicable to the instance)
# ------------------------------------------------------------------

# Eq. 2.8 - dependency: alternative (i,j) requires (ip,jp) to be selected
# set DEPENDENCIES within {i in PROJECTS, j in ALTERNATIVES[i],
#                          ip in PROJECTS, jp in ALTERNATIVES[ip]};
# subject to Dependency {(i,j,ip,jp) in DEPENDENCIES}:
#     x[i,j] <= x[ip,jp];

# Eq. 2.9 - cross-project exclusivity: pairs of conflicting alternatives
# set CONFLICTS within {i in PROJECTS, j in ALTERNATIVES[i],
#                       ip in PROJECTS, jp in ALTERNATIVES[ip]};
# subject to CrossExclusivity {(i,j,ip,jp) in CONFLICTS}:
#     x[i,j] + x[ip,jp] <= 1;

# Eq. 2.10 - minimum benefit-cost ratio (parameter theta)
# param theta default 1.0;
# subject to MinBCR {i in PROJECTS}:
#     sum {j in ALTERNATIVES[i]} Benefit[i,j] * x[i,j]
#       >= theta * sum {j in ALTERNATIVES[i]} Cost[i,j] * x[i,j];

# ------------------------------------------------------------------
# Network-level constraints (uncomment when facility-type or regional
# segmentation is supplied in the data file)
# ------------------------------------------------------------------

# set FACILITY_TYPES;
# set FacilityProjects{m in FACILITY_TYPES} within PROJECTS;
# param B_facility{m in FACILITY_TYPES};
# subject to FacilityBudget {m in FACILITY_TYPES}:
#     sum {i in FacilityProjects[m], j in ALTERNATIVES[i]}
#         Cost[i,j] * x[i,j] <= B_facility[m];

# set REGIONS;
# set RegionProjects{r in REGIONS} within PROJECTS;
# param B_region_cap{r in REGIONS};
# param beta_region{r in REGIONS} default 0;
# subject to RegionalCap {r in REGIONS}:
#     sum {i in RegionProjects[r], j in ALTERNATIVES[i]}
#         Cost[i,j] * x[i,j] <= B_region_cap[r];
# subject to RegionalFloor {r in REGIONS}:
#     sum {i in RegionProjects[r], j in ALTERNATIVES[i]}
#         Cost[i,j] * x[i,j] >= beta_region[r] * B_total;
