$TITLE MCBOMs Project-Level MILP - Harwood 50M
$ONTEXT
   Harwood et al. (2003) case study, 50M dollar budget
   Mathematical formulation per Chapter 2 of MCBOMs Task 4 report.
   Maximize total net benefit subject to a budget and at most one
   alternative per project.
$OFFTEXT

Sets
   i        projects                 / 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 /
   j        alternatives             / 0 , 1 , 2 /
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

Scalar B_total  total budget / 50000000 /;

Parameters
   Benefit(i,j)  PV total benefit /
   1 . 0   0
   1 . 1   35107
   2 . 0   0
   2 . 1   399756
   3 . 0   0
   3 . 1   1188606
   4 . 0   0
   4 . 1   834008
   5 . 0   0
   5 . 1   1408618
   6 . 0   0
   6 . 1   901437
   7 . 0   0
   7 . 1   1040641
   8 . 0   0
   8 . 1   705644
   8 . 2   1270056
   9 . 0   0
   9 . 1   1153238
   10 . 0   0
   10 . 1   2409442
   /;

Parameter Cost(i,j)  PV total cost /
   1 . 0   0
   1 . 1   528803
   2 . 0   0
   2 . 1   639763
   3 . 0   0
   3 . 1   1381621
   4 . 0   0
   4 . 1   1047816
   5 . 0   0
   5 . 1   1420017
   6 . 0   0
   6 . 1   3068549
   7 . 0   0
   7 . 1   1863237
   8 . 0   0
   8 . 1   1578989
   8 . 2   2078989
   9 . 0   0
   9 . 1   1701302
   10 . 0   0
   10 . 1   2541150
   /;

* ----------------------------------------------------------------
* Variables
* ----------------------------------------------------------------
Binary Variable x(i,j)   alternative selection;
Variable Z               total net benefit;

Equations
   Objective              objective function (Eq 2.4)
   TotalBudget            total budget constraint (Eq 2.5)
   MutualExclusivity(i)   at most one alt per project (Eq 2.6)
   ;

Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost(i,j)) * x(i,j));

TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;

Model mcboms / all /;

Solve mcboms using MIP maximizing Z;

Display Z.l, x.l;