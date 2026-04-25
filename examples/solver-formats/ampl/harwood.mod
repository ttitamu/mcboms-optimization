# =====================================================================
# Harwood et al. (2003) Case Study - AMPL Model
# Mathematical formulation per Chapter 2 of MCBOMs Task 4 report
#
# Reference: Harwood, Rabbani, Richard (2003), TRR 1840, Tables 2 and 3.
# 10-site case study, mix of rural and urban undivided/divided 2- and
# 4-lane nonfreeway facilities.
#
# DATA SCOPE:
# This file uses Harwood's published per-site, per-alternative values
# from Tables 2 and 3 (PSB, PTOB, costs) directly. Harwood's RSRAP
# computes PSB internally from per-severity AMFs, accident frequencies,
# and unit costs (his Eq. 1, paper p.151), but those raw inputs are
# not published in the paper - only the aggregate PSB values are.
# Therefore this file expresses Eq 2.2 (total benefit aggregation) and
# Eq 2.4 (objective) explicitly, with PSB and PTOB as input parameters.
# The full Eq 2.18 chain from raw severity-level inputs is demonstrated
# in worked_example.mod.
#
# OBJECTIVE FORMULATION:
# Harwood treats RRR projects with required pavement resurfacing - the
# resurfacing cost is committed (every site is resurfaced under the
# program), and only the safety improvement cost is the discretionary
# optimization variable. Per Chapter 2 Section 2.2.1 (discretionary
# vs committed cost), the objective uses:
#   max sum_{i,j} (Benefit_ij - Cost_disc_ij) * x_ij
# where Cost_disc = SafetyImprovementCost (the discretionary part).
# The budget constraint uses the full cost (resurfacing + safety).
#
# Validation status: $50M budget reproduces Harwood Table 4 exactly
# (within $5 rounding); $10M budget produces a different selection set
# because PNR is not implemented (see Chapter 2 Section 2.7.3).
# =====================================================================

# ---------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------

set PROJECTS;                       # 10 sites (Harwood Table 1)
set ALTERNATIVES{i in PROJECTS};    # alt 0 = do nothing; 1, 2 = improvement options

# ---------------------------------------------------------------------
# Parameters - per Harwood Tables 2 and 3
# ---------------------------------------------------------------------

# Cost components
param ResurfacingCost {i in PROJECTS, j in ALTERNATIVES[i]};        # committed
param SafetyImprovementCost {i in PROJECTS, j in ALTERNATIVES[i]};  # discretionary

# Benefit components (Harwood paper notation)
param PSB {i in PROJECTS, j in ALTERNATIVES[i]};   # safety benefits, PV
param PTOB {i in PROJECTS, j in ALTERNATIVES[i]};  # operational benefits, PV

# Total budget (set in instance .dat file: 50,000,000 or 10,000,000)
param B_total;

# ---------------------------------------------------------------------
# Derived parameters - Eq 2.2 (total benefit aggregation)
#   B_total_ij = PSB_ij + PTOB_ij  (no CCM in Harwood; PNR/PRP disabled)
# ---------------------------------------------------------------------

param Benefit {i in PROJECTS, j in ALTERNATIVES[i]} := PSB[i,j] + PTOB[i,j];

# Cost (Eq 2.2 cost side)
#   Total cost = ResurfacingCost + SafetyImprovementCost
#   Discretionary cost = SafetyImprovementCost only (Harwood convention)
param Cost {i in PROJECTS, j in ALTERNATIVES[i]} :=
    ResurfacingCost[i,j] + SafetyImprovementCost[i,j];

param Cost_disc {i in PROJECTS, j in ALTERNATIVES[i]} :=
    SafetyImprovementCost[i,j];

# ---------------------------------------------------------------------
# Decision variables (Eq 2.7)
# ---------------------------------------------------------------------

var x {i in PROJECTS, j in ALTERNATIVES[i]} binary;

# ---------------------------------------------------------------------
# Objective (Eq 2.4 with discretionary cost convention)
#   max sum (B_ij - C_disc_ij) * x_ij
# ---------------------------------------------------------------------

maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost_disc[i,j]) * x[i,j];

# ---------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------

# Eq 2.5 - total budget (uses full cost = resurfacing + safety)
subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

# Eq 2.6 - mutual exclusivity
subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;
