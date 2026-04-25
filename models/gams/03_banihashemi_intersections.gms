$TITLE Banihashemi (2007) Intersection Sub-Problem - Full Parametric
$ONTEXT
   Reference: Banihashemi (2007), TRR 2019, Table 3 and pp.109-115
   13 intersections, 43 alternatives
   IHSDM Crash Prediction Module (Banihashemi Eq 15):
     N_i = exp(alpha + beta*ln(ADT1) + gamma*ln(ADT2)) * C_i * prod(AMFs)

   Banihashemi minimizes total (crash + delay) cost. The MCBOMs
   framework is benefit-maximization, so we convert: Benefit_ij =
   avoided cost vs baseline alternative 0.
$OFFTEXT

Sets
   i        intersections / 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 , 11 , 12 , 13 /
   j        alternative IDs / 0 , 1 , 2 , 3 , 4 /
   itype    intersection types / 'leg4_stop', 'leg4_signal' /
   ;

Set ij(i,j)  valid project-alternative pairs /
   1 . 0
   1 . 1
   1 . 2
   1 . 3
   2 . 0
   2 . 1
   2 . 2
   2 . 3
   3 . 0
   3 . 1
   4 . 0
   4 . 1
   5 . 0
   5 . 1
   5 . 2
   5 . 3
   6 . 0
   6 . 1
   6 . 2
   6 . 3
   7 . 0
   7 . 1
   7 . 2
   7 . 3
   8 . 0
   8 . 1
   9 . 0
   9 . 1
   9 . 2
   9 . 3
   10 . 0
   10 . 1
   11 . 0
   11 . 1
   12 . 0
   12 . 1
   12 . 2
   12 . 3
   13 . 0
   13 . 1
   13 . 2
   13 . 3
   13 . 4
   /;

* ----------------------------------------------------------------
* IHSDM CPM parameters by intersection type (Banihashemi p.113)
* Note: GAMS doesn't allow leading digit in set element so we use
* 'leg4_stop' and 'leg4_signal' here (was '4leg_stop' in the .py source)
* ----------------------------------------------------------------

Parameter alpha(itype) /
   leg4_stop   -9.34
   leg4_signal -5.73
   /;
Parameter beta(itype) /
   leg4_stop   0.6
   leg4_signal 0.6
   /;
Parameter gamma(itype) /
   leg4_stop   0.61
   leg4_signal 0.2
   /;
Parameter Ci(itype) /
   leg4_stop   0.98
   leg4_signal 0.94
   /;
Parameter CrashCost(itype) /
   leg4_stop   81375
   leg4_signal 31665
   /;

Scalar T              project lifetime years            / 20 /;
Scalar UnitDelayCost  delay cost USD per veh-hour       / 12.5 /;
Scalar B_total        total budget                      / 12000000 /;

* ----------------------------------------------------------------
* Per-intersection ADTs
* ----------------------------------------------------------------

Parameter ADT1(i)  major-road ADT /
   1   7100
   2   7100
   3   7100
   4   7100
   5   7100
   6   7100
   7   7100
   8   9000
   9   9000
   10   7975
   11   6950
   12   6950
   13   6950
   /;
Parameter ADT2(i)  minor-road ADT /
   1   2500
   2   2500
   3   2500
   4   2500
   5   2500
   6   2500
   7   5000
   8   2500
   9   2500
   10   2500
   11   2500
   12   2500
   13   2500
   /;

* ----------------------------------------------------------------
* Per-(i,j) alternative attributes
* ----------------------------------------------------------------

Parameter Skew(i,j) /
   1 . 0   4.75
   1 . 1   4.75
   1 . 2   4.75
   1 . 3   4.75
   2 . 0   0.0
   2 . 1   0.0
   2 . 2   0.0
   2 . 3   0.0
   3 . 0   9.0
   3 . 1   9.0
   4 . 0   3.77
   4 . 1   3.77
   5 . 0   4.11
   5 . 1   4.11
   5 . 2   4.11
   5 . 3   4.11
   6 . 0   1.89
   6 . 1   1.89
   6 . 2   1.89
   6 . 3   1.89
   7 . 0   43.14
   7 . 1   43.14
   7 . 2   0.0
   7 . 3   0.0
   8 . 0   23.25
   8 . 1   23.25
   9 . 0   6.75
   9 . 1   6.75
   9 . 2   6.75
   9 . 3   6.75
   10 . 0   13.25
   10 . 1   13.25
   11 . 0   17.5
   11 . 1   17.5
   12 . 0   7.0
   12 . 1   7.0
   12 . 2   0.0
   12 . 3   0.0
   13 . 0   8.0
   13 . 1   8.0
   13 . 2   8.0
   13 . 3   0.0
   13 . 4   8.0
   /;

Parameter HasLTL(i,j) /
   1 . 0   0
   1 . 1   1
   1 . 2   0
   1 . 3   1
   2 . 0   0
   2 . 1   1
   2 . 2   0
   2 . 3   1
   3 . 0   0
   3 . 1   0
   4 . 0   0
   4 . 1   0
   5 . 0   0
   5 . 1   1
   5 . 2   0
   5 . 3   1
   6 . 0   0
   6 . 1   1
   6 . 2   0
   6 . 3   1
   7 . 0   0
   7 . 1   0
   7 . 2   0
   7 . 3   0
   8 . 0   0
   8 . 1   0
   9 . 0   0
   9 . 1   1
   9 . 2   0
   9 . 3   1
   10 . 0   0
   10 . 1   1
   11 . 0   0
   11 . 1   0
   12 . 0   0
   12 . 1   1
   12 . 2   0
   12 . 3   1
   13 . 0   0
   13 . 1   0
   13 . 2   1
   13 . 3   1
   13 . 4   1
   /;

Parameter HasISD(i,j) /
   1 . 0   0
   1 . 1   0
   1 . 2   0
   1 . 3   0
   2 . 0   0
   2 . 1   0
   2 . 2   0
   2 . 3   0
   3 . 0   0
   3 . 1   0
   4 . 0   0
   4 . 1   0
   5 . 0   0
   5 . 1   0
   5 . 2   0
   5 . 3   0
   6 . 0   0
   6 . 1   0
   6 . 2   0
   6 . 3   0
   7 . 0   1
   7 . 1   0
   7 . 2   1
   7 . 3   0
   8 . 0   0
   8 . 1   0
   9 . 0   0
   9 . 1   0
   9 . 2   0
   9 . 3   0
   10 . 0   0
   10 . 1   0
   11 . 0   0
   11 . 1   0
   12 . 0   0
   12 . 1   0
   12 . 2   0
   12 . 3   0
   13 . 0   1
   13 . 1   0
   13 . 2   1
   13 . 3   1
   13 . 4   0
   /;

* Control encoding: 0 = Minor stop, 1 = All stop, 2 = Signalized
Parameter ControlCode(i,j) /
   1 . 0   0
   1 . 1   0
   1 . 2   1
   1 . 3   1
   2 . 0   0
   2 . 1   0
   2 . 2   1
   2 . 3   1
   3 . 0   0
   3 . 1   2
   4 . 0   0
   4 . 1   2
   5 . 0   0
   5 . 1   0
   5 . 2   1
   5 . 3   1
   6 . 0   0
   6 . 1   0
   6 . 2   1
   6 . 3   1
   7 . 0   0
   7 . 1   0
   7 . 2   0
   7 . 3   0
   8 . 0   0
   8 . 1   1
   9 . 0   0
   9 . 1   0
   9 . 2   1
   9 . 3   1
   10 . 0   2
   10 . 1   2
   11 . 0   0
   11 . 1   1
   12 . 0   0
   12 . 1   0
   12 . 2   0
   12 . 3   0
   13 . 0   0
   13 . 1   0
   13 . 2   0
   13 . 3   0
   13 . 4   0
   /;

Parameter Delay(i,j)  vehicle-hours per year /
   1 . 0   3039
   1 . 1   3039
   1 . 2   14852
   1 . 3   9151
   2 . 0   3039
   2 . 1   3039
   2 . 2   14852
   2 . 3   9151
   3 . 0   6078
   3 . 1   98165
   4 . 0   6078
   4 . 1   72450
   5 . 0   3039
   5 . 1   3039
   5 . 2   14852
   5 . 3   9151
   6 . 0   3039
   6 . 1   3039
   6 . 2   14852
   6 . 3   9151
   7 . 0   67698
   7 . 1   67698
   7 . 2   67698
   7 . 3   67698
   8 . 0   5438
   8 . 1   66412
   9 . 0   5438
   9 . 1   5438
   9 . 2   66412
   9 . 3   21645
   10 . 0   81607
   10 . 1   83030
   11 . 0   2935
   11 . 1   8994
   12 . 0   5870
   12 . 1   5870
   12 . 2   5870
   12 . 3   5870
   13 . 0   5870
   13 . 1   5870
   13 . 2   5870
   13 . 3   5870
   13 . 4   5870
   /;

Parameter Improvement_Cost(i,j) /
   1 . 0   0
   1 . 1   300000
   1 . 2   0
   1 . 3   300000
   2 . 0   0
   2 . 1   300000
   2 . 2   0
   2 . 3   300000
   3 . 0   0
   3 . 1   0
   4 . 0   0
   4 . 1   0
   5 . 0   0
   5 . 1   400000
   5 . 2   0
   5 . 3   400000
   6 . 0   0
   6 . 1   400000
   6 . 2   0
   6 . 3   400000
   7 . 0   0
   7 . 1   500000
   7 . 2   600000
   7 . 3   1100000
   8 . 0   0
   8 . 1   0
   9 . 0   0
   9 . 1   600000
   9 . 2   0
   9 . 3   600000
   10 . 0   0
   10 . 1   600000
   11 . 0   0
   11 . 1   0
   12 . 0   0
   12 . 1   100000
   12 . 2   600000
   12 . 3   700000
   13 . 0   0
   13 . 1   600000
   13 . 2   600000
   13 . 3   1200000
   13 . 4   1200000
   /;

* ----------------------------------------------------------------
* Effective intersection type for each alternative
* (signalization changes the type from leg4_stop to leg4_signal)
* ----------------------------------------------------------------

Parameter IsSignal(i,j);
IsSignal(i,j)$ij(i,j) = 1$(ControlCode(i,j) eq 2);

* AMFs (IHSDM / Vogt-Bared standard values)
Parameter AMF_skew(i,j);
AMF_skew(i,j)$ij(i,j) = 1$(IsSignal(i,j) eq 1) + (1 - 1$(IsSignal(i,j) eq 1)) * exp(0.0054 * abs(Skew(i,j)));

Parameter AMF_tc(i,j);
AMF_tc(i,j)$ij(i,j) = 1$(IsSignal(i,j) eq 1) + 0.70$(ControlCode(i,j) eq 1) + 1$(ControlCode(i,j) eq 0);

Parameter AMF_ltl(i,j);
AMF_ltl(i,j)$ij(i,j) = 1$(HasLTL(i,j) eq 0) + 0.77$(HasLTL(i,j) eq 1 and IsSignal(i,j) eq 1) + 0.67$(HasLTL(i,j) eq 1 and IsSignal(i,j) eq 0);

Parameter AMF_sd(i,j);
AMF_sd(i,j)$ij(i,j) = 1$(HasISD(i,j) eq 0) + 1.42$(HasISD(i,j) eq 1);

* ----------------------------------------------------------------
* Banihashemi Eq 15: crash prediction
*   N_ij = exp(alpha + beta*ln(ADT1) + gamma*ln(ADT2)) * Ci * prod(AMFs)
* ----------------------------------------------------------------

Parameter EffType_label(i,j) effective intersection type;
* 1 = leg4_stop, 2 = leg4_signal
Parameter Crashes_per_year(i,j);
Crashes_per_year(i,j)$(ij(i,j) and IsSignal(i,j) eq 0) =
    exp(alpha('leg4_stop') + beta('leg4_stop')*log(ADT1(i)) + gamma('leg4_stop')*log(ADT2(i)))
    * Ci('leg4_stop') * AMF_skew(i,j) * AMF_tc(i,j) * AMF_ltl(i,j) * AMF_sd(i,j);
Crashes_per_year(i,j)$(ij(i,j) and IsSignal(i,j) eq 1) =
    exp(alpha('leg4_signal') + beta('leg4_signal')*log(ADT1(i)) + gamma('leg4_signal')*log(ADT2(i)))
    * Ci('leg4_signal') * AMF_skew(i,j) * AMF_tc(i,j) * AMF_ltl(i,j) * AMF_sd(i,j);

* 20-year crash and delay cost
Parameter Crash_Cost_20yr(i,j);
Crash_Cost_20yr(i,j)$(ij(i,j) and IsSignal(i,j) eq 0) = Crashes_per_year(i,j) * CrashCost('leg4_stop') * T;
Crash_Cost_20yr(i,j)$(ij(i,j) and IsSignal(i,j) eq 1) = Crashes_per_year(i,j) * CrashCost('leg4_signal') * T;

Parameter Delay_Cost_20yr(i,j);
Delay_Cost_20yr(i,j)$ij(i,j) = Delay(i,j) * UnitDelayCost * T;

Parameter Total_Cost_20yr(i,j);
Total_Cost_20yr(i,j)$ij(i,j) = Crash_Cost_20yr(i,j) + Delay_Cost_20yr(i,j);

* ----------------------------------------------------------------
* MCBOMs benefit (avoided cost) and cost
* ----------------------------------------------------------------

Parameter Benefit(i,j);
Benefit(i,j)$ij(i,j) = Total_Cost_20yr(i,'0') - Total_Cost_20yr(i,j);

Parameter Cost(i,j);
Cost(i,j)$ij(i,j) = Improvement_Cost(i,j);

* ----------------------------------------------------------------
* Variables, objective, constraints (Eq 2.4 - 2.7)
* ----------------------------------------------------------------

Binary Variable x(i,j);
Variable Z;

Equations Objective, TotalBudget, MutualExclusivity(i);

Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost(i,j)) * x(i,j));

TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;

Model banihashemi / all /;
Solve banihashemi using MIP maximizing Z;

Display Crashes_per_year, Total_Cost_20yr, Z.l, x.l;