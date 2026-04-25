# =====================================================================
# Banihashemi (2007) Intersection Sub-Problem - AMPL Model
# Mathematical formulation per Chapter 2 of MCBOMs Task 4 report
# Banihashemi Eq 15: N_i = exp(alpha + beta*ln(ADT1) + gamma*ln(ADT2))
#                          * C_i * prod(AMFs)
#
# Banihashemi minimizes total (crash + delay) cost. The MCBOMs
# framework is benefit-maximization, so we convert: benefit of an
# alternative = avoided (crash + delay) cost vs the baseline (alt 0).
#
# Crash unit costs by intersection type (Banihashemi p.109):
#   4-leg stop:        $81,375 / crash
#   4-leg signalized:  $31,665 / crash
#   3-leg stop:        $55,239 / crash
# Unit delay cost: $12.50 per vehicle-hour (Banihashemi p.109)
# Project lifetime: 20 years (uniform horizon)
#
# AMF values are standard IHSDM/Vogt-Bared (Banihashemi did not publish
# his exact AMFs; this reconstruction uses values from FHWA-RD-99-207).
# =====================================================================

# ---------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------

set PROJECTS := { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 };
set ALTERNATIVES[1] := { 0, 1, 2, 3 };
set ALTERNATIVES[2] := { 0, 1, 2, 3 };
set ALTERNATIVES[3] := { 0, 1 };
set ALTERNATIVES[4] := { 0, 1 };
set ALTERNATIVES[5] := { 0, 1, 2, 3 };
set ALTERNATIVES[6] := { 0, 1, 2, 3 };
set ALTERNATIVES[7] := { 0, 1, 2, 3 };
set ALTERNATIVES[8] := { 0, 1 };
set ALTERNATIVES[9] := { 0, 1, 2, 3 };
set ALTERNATIVES[10] := { 0, 1 };
set ALTERNATIVES[11] := { 0, 1 };
set ALTERNATIVES[12] := { 0, 1, 2, 3 };
set ALTERNATIVES[13] := { 0, 1, 2, 3, 4 };

set INT_TYPES := { '4leg_stop', '4leg_signal' };

# ---------------------------------------------------------------------
# Parameters - intersection-level (per project i)
# ---------------------------------------------------------------------

param ADT1 {PROJECTS};   # major-road ADT
param ADT2 {PROJECTS};   # minor-road ADT
param ExistingType {PROJECTS} symbolic;  # 4leg_stop or 4leg_signal

# ---------------------------------------------------------------------
# Parameters - alternative-level (per (i,j))
# ---------------------------------------------------------------------

param Skew {i in PROJECTS, j in ALTERNATIVES[i]};
param Control {i in PROJECTS, j in ALTERNATIVES[i]} symbolic;  # MinorStop, AllStop, Signalized
param HasLTL {i in PROJECTS, j in ALTERNATIVES[i]} binary;
param HasISD {i in PROJECTS, j in ALTERNATIVES[i]} binary;     # 1 if ISD deficiency present
param Delay {i in PROJECTS, j in ALTERNATIVES[i]};             # vehicle-hours per year
param Improvement_Cost {i in PROJECTS, j in ALTERNATIVES[i]};

# ---------------------------------------------------------------------
# IHSDM CPM parameters by intersection type (Banihashemi p.113)
# ---------------------------------------------------------------------

param alpha {INT_TYPES};
param beta {INT_TYPES};
param gamma {INT_TYPES};
param Ci {INT_TYPES};
param CrashCost {INT_TYPES};

let alpha['4leg_stop'] := -9.34;
let beta['4leg_stop']  := 0.6;
let gamma['4leg_stop'] := 0.61;
let Ci['4leg_stop']    := 0.98;
let CrashCost['4leg_stop'] := 81375;
let alpha['4leg_signal'] := -5.73;
let beta['4leg_signal']  := 0.6;
let gamma['4leg_signal'] := 0.2;
let Ci['4leg_signal']    := 0.94;
let CrashCost['4leg_signal'] := 31665;

# Effective intersection type for each alternative
# (signalization changes the type from 4leg_stop to 4leg_signal)
param EffType {i in PROJECTS, j in ALTERNATIVES[i]} symbolic :=
    if Control[i,j] = 'Signalized' then '4leg_signal' else '4leg_stop';

# ---------------------------------------------------------------------
# AMF values (IHSDM / Vogt-Bared standard)
# ---------------------------------------------------------------------

# Skew angle AMF: AMF_skew = exp(0.0054 * |skew|) for stop-controlled,
# AMF_skew = 1.0 for signalized
param AMF_skew {i in PROJECTS, j in ALTERNATIVES[i]} :=
    if EffType[i,j] = '4leg_signal' then 1.0
    else exp(0.0054 * abs(Skew[i,j]));

# Traffic control AMF (vs base of minor-stop):
# minor->all-stop = 0.70, minor->signal = 0.56, all-stop->signal = 0.80
param AMF_tc {i in PROJECTS, j in ALTERNATIVES[i]} :=
    if EffType[i,j] = '4leg_signal' then 1.0  # signal is its own base
    else if Control[i,j] = 'All stop' then 0.70
    else 1.0;

# Left-turn lane AMF: 0.67 stop-control, 0.77 signal, 1.0 if no LTL added
param AMF_ltl {i in PROJECTS, j in ALTERNATIVES[i]} :=
    if HasLTL[i,j] = 0 then 1.0
    else if EffType[i,j] = '4leg_signal' then 0.77
    else 0.67;

# Sight distance AMF: 1.42 with deficiency, 1.0 if no deficiency
param AMF_sd {i in PROJECTS, j in ALTERNATIVES[i]} :=
    if HasISD[i,j] = 1 then 1.42 else 1.0;

# ---------------------------------------------------------------------
# Crash prediction (Banihashemi Eq 15)
#   N_ij = exp(alpha + beta*ln(ADT1) + gamma*ln(ADT2)) * Ci * prod(AMFs)
# ---------------------------------------------------------------------

param Crashes_per_year {i in PROJECTS, j in ALTERNATIVES[i]} :=
    exp( alpha[EffType[i,j]]
       + beta[EffType[i,j]] * log(ADT1[i])
       + gamma[EffType[i,j]] * log(ADT2[i]) )
    * Ci[EffType[i,j]]
    * AMF_skew[i,j] * AMF_tc[i,j] * AMF_ltl[i,j] * AMF_sd[i,j];

# ---------------------------------------------------------------------
# Cost computation - 20-year totals
# ---------------------------------------------------------------------

param T := 20;                    # project lifetime
param UnitDelayCost := 12.5;            # $/veh-hr

# 20-year crash cost
param Crash_Cost_20yr {i in PROJECTS, j in ALTERNATIVES[i]} :=
    Crashes_per_year[i,j] * CrashCost[EffType[i,j]] * T;

# 20-year delay cost
param Delay_Cost_20yr {i in PROJECTS, j in ALTERNATIVES[i]} :=
    Delay[i,j] * UnitDelayCost * T;

# Total societal cost (crash + delay) over 20 years
param Total_Cost_20yr {i in PROJECTS, j in ALTERNATIVES[i]} :=
    Crash_Cost_20yr[i,j] + Delay_Cost_20yr[i,j];

# ---------------------------------------------------------------------
# MCBOMs benefit and cost (per Eq 2.2 / 2.4)
#   Benefit = avoided cost vs baseline alternative 0
#   Cost    = improvement cost
# ---------------------------------------------------------------------

param Benefit {i in PROJECTS, j in ALTERNATIVES[i]} :=
    Total_Cost_20yr[i,0] - Total_Cost_20yr[i,j];

param Cost {i in PROJECTS, j in ALTERNATIVES[i]} := Improvement_Cost[i,j];

# Total budget
param B_total := 12000000;

# ---------------------------------------------------------------------
# Decision variables, objective (Eq 2.4), and constraints
# ---------------------------------------------------------------------

var x {i in PROJECTS, j in ALTERNATIVES[i]} binary;

maximize NetBenefit:
    sum {i in PROJECTS, j in ALTERNATIVES[i]}
        (Benefit[i,j] - Cost[i,j]) * x[i,j];

subject to TotalBudget:
    sum {i in PROJECTS, j in ALTERNATIVES[i]} Cost[i,j] * x[i,j] <= B_total;

subject to MutualExclusivity {i in PROJECTS}:
    sum {j in ALTERNATIVES[i]} x[i,j] <= 1;
