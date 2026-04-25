# =====================================================================
# Worked Example - Single segment, full Eq 2.18 (safety) chain
#
# Reference: MCBOMs Task 4 Report, Chapter 2, Section 2.3.7
#   5-mile rural two-lane segment
#   AADT = 5,000 veh/day
#   Observed crashes = 6.0 / year
#   Severity distribution (K, A, B, C, O): 1.3%, 6.5%, 9.5%, 11.7%, 71.0%
#   Treatment: lane widening from 10 ft to 12 ft, CMF = 0.88
#   Discount rate r = 0.07, horizon T = 20 yr, PWF = 10.594
#   Unit costs: USDOT BCA Guidance May 2025, Appendix A Table A-1 (2023 $)
#
# This file demonstrates the Eq 2.18 safety benefit calculation explicitly:
#
#   B^safety_year = sum over severity s of:
#       (E^nobuild - E^build) * UC[s]
#     = sum_s ( N * p[s] * (1 - CMF) ) * UC[s]
#
#   B^safety_PV = B^safety_year * PWF(r, T)
#
# Expected result: annual = $211,810, PV = $2,243,913
# =====================================================================

# ---------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------

set SEVERITY := { "K", "A", "B", "C", "O" };

# For optimization layer
set PROJECTS := { 1 };
set ALTERNATIVES{i in PROJECTS} := { 0, 1 };  # 0=do nothing, 1=widen lanes

# ---------------------------------------------------------------------
# Raw input parameters (paper / report values)
# ---------------------------------------------------------------------

# Annual observed crash count at the site
param N := 6.0;

# Severity distribution
param p{SEVERITY};
let p["K"] := 0.013;
let p["A"] := 0.065;
let p["B"] := 0.095;
let p["C"] := 0.117;
let p["O"] := 0.710;

# Unit costs by severity (USDOT BCA May 2025, 2023 dollars)
param UC{SEVERITY};
let UC["K"] := 13200000;
let UC["A"] := 1254700;
let UC["B"] := 246900;
let UC["C"] := 118000;
let UC["O"] := 5300;

# CMF for the treatment (lane widening 10->12 ft)
param CMF := 0.88;

# Economics
param r := 0.07;          # discount rate
param T := 20;            # analysis horizon (years)

# Cost of the treatment
param TreatmentCost := 750000;     # USD, illustrative

# Total program budget
param B_total := 1000000;

# ---------------------------------------------------------------------
# Derived parameters: Eq 2.18 chain
# ---------------------------------------------------------------------

# Present worth factor PWF(r, T) = ((1+r)^T - 1) / (r * (1+r)^T)
param PWF := ((1 + r)**T - 1) / (r * (1 + r)**T);

# E^nobuild_s: expected crashes by severity, no-build
param E_nobuild{s in SEVERITY} := N * p[s];

# E^build_s for the active treatment alternative
# (CMF applies uniformly across severity here; report Section 2.3.7)
param E_build_alt1{s in SEVERITY} := E_nobuild[s] * CMF;

# Annual safety benefit by alternative (Eq 2.18 inner sum)
# - Alt 0 = do nothing: B = 0
# - Alt 1 = widen lanes: B = sum_s (E_nobuild - E_build) * UC[s]
param B_safety_year{i in PROJECTS, j in ALTERNATIVES[i]} :=
    if j = 0 then 0
    else sum {s in SEVERITY} (E_nobuild[s] - E_build_alt1[s]) * UC[s];

# Present value safety benefit (Eq 2.18 with PWF)
# In a constant-annual-crashes prototype, B^safety_PV = B^safety_year * PWF
param B_safety_PV{i in PROJECTS, j in ALTERNATIVES[i]} :=
    B_safety_year[i,j] * PWF;

# Total benefit (Eq 2.2; for this example only safety is relevant)
param Benefit{i in PROJECTS, j in ALTERNATIVES[i]} := B_safety_PV[i,j];

# Cost
param Cost{i in PROJECTS, j in ALTERNATIVES[i]} :=
    if j = 0 then 0 else TreatmentCost;

# ---------------------------------------------------------------------
# Decision variables (Eq 2.7)
# ---------------------------------------------------------------------

var x{i in PROJECTS, j in ALTERNATIVES[i]} binary;

# ---------------------------------------------------------------------
# Objective (Eq 2.4)
# ---------------------------------------------------------------------

maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost[i,j]) * x[i,j];

# ---------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------

# Eq 2.5 - total budget
subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

# Eq 2.6 - mutual exclusivity
subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;
