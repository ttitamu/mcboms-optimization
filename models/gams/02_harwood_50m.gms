$TITLE Harwood (2003) Case Study - $50M budget
$ONTEXT
   Reference: Harwood, Rabbani, Richard (2003), TRR 1840, Tables 2 and 3
   10-site case study, mix of rural and urban undivided/divided 2- and
   4-lane nonfreeway facilities.

   Eq 2.2 - total benefit aggregation: B_total = PSB + PTOB
   Eq 2.4 - objective: max sum (Benefit - Cost_disc) * x
   Cost_disc (Harwood-style) = SafetyImprovementCost only;
   total budget uses ResurfacingCost + SafetyImprovementCost.

   PSB and PTOB taken directly from Harwood Tables 2 and 3 (paper-faithful).
   The Eq 2.18 per-severity computation that produces PSB internally is
   demonstrated in worked_example.gms.
$OFFTEXT

Sets
   i    projects     / 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 /
   j    alternatives / 0 , 1 , 2 /
   ;

Set ij(i,j)  valid project-alternative pairs /
   1 . 0
   1 . 1
   2 . 0
   2 . 1
   3 . 0
   3 . 1
   4 . 0
   4 . 1
   5 . 0
   5 . 1
   6 . 0
   6 . 1
   7 . 0
   7 . 1
   8 . 0
   8 . 1
   8 . 2
   9 . 0
   9 . 1
   10 . 0
   10 . 1
   /;

Scalar B_total   total budget USD / 50000000 /;

Parameters
   ResurfacingCost(i,j)     'committed component'  /
   1 . 0   0
   1 . 1   528803
   2 . 0   0
   2 . 1   519763
   3 . 0   0
   3 . 1   821621
   4 . 0   0
   4 . 1   475200
   5 . 0   0
   5 . 1   1180017
   6 . 0   0
   6 . 1   2508549
   7 . 0   0
   7 . 1   1503237
   8 . 0   0
   8 . 1   1398989
   8 . 2   1398989
   9 . 0   0
   9 . 1   1365302
   10 . 0   0
   10 . 1   1488369
   /;

Parameter SafetyImprovementCost(i,j)  'discretionary component' /
   1 . 0   0
   1 . 1   0
   2 . 0   0
   2 . 1   120000
   3 . 0   0
   3 . 1   560000
   4 . 0   0
   4 . 1   572616
   5 . 0   0
   5 . 1   240000
   6 . 0   0
   6 . 1   560000
   7 . 0   0
   7 . 1   360000
   8 . 0   0
   8 . 1   180000
   8 . 2   680000
   9 . 0   0
   9 . 1   336000
   10 . 0   0
   10 . 1   1052781
   /;

Parameter PSB(i,j)  'safety benefit (PV)' /
   1 . 0   0
   1 . 1   0
   2 . 0   0
   2 . 1   328176
   3 . 0   0
   3 . 1   1094909
   4 . 0   0
   4 . 1   775629
   5 . 0   0
   5 . 1   1355589
   6 . 0   0
   6 . 1   808637
   7 . 0   0
   7 . 1   947234
   8 . 0   0
   8 . 1   555526
   8 . 2   1119938
   9 . 0   0
   9 . 1   1071895
   10 . 0   0
   10 . 1   2329256
   /;

Parameter PTOB(i,j)  'operational benefit (PV)' /
   1 . 0   0
   1 . 1   35107
   2 . 0   0
   2 . 1   71580
   3 . 0   0
   3 . 1   93697
   4 . 0   0
   4 . 1   58379
   5 . 0   0
   5 . 1   53029
   6 . 0   0
   6 . 1   92800
   7 . 0   0
   7 . 1   93407
   8 . 0   0
   8 . 1   150118
   8 . 2   150118
   9 . 0   0
   9 . 1   81343
   10 . 0   0
   10 . 1   80186
   /;

* Derived: Benefit, Cost, Cost_disc
Parameter Benefit(i,j);
Benefit(i,j) = PSB(i,j) + PTOB(i,j);

Parameter Cost(i,j);
Cost(i,j) = ResurfacingCost(i,j) + SafetyImprovementCost(i,j);

Parameter Cost_disc(i,j);
Cost_disc(i,j) = SafetyImprovementCost(i,j);

Binary Variable x(i,j);
Variable Z                  'total net benefit';

Equations
   Objective                'Eq 2.4'
   TotalBudget              'Eq 2.5'
   MutualExclusivity(i)     'Eq 2.6'
   ;

Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost_disc(i,j)) * x(i,j));

TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;

Model harwood / all /;
Solve harwood using MIP maximizing Z;

Display Z.l, x.l;