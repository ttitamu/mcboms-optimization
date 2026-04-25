$TITLE MCBOMs Project-Level MILP - Banihashemi Intersections
$ONTEXT
   Banihashemi (2007) intersection sub-problem (13 intersections, 43 alts)
   Mathematical formulation per Chapter 2 of MCBOMs Task 4 report.
   Maximize total net benefit subject to a budget and at most one
   alternative per project.
$OFFTEXT

Sets
   i        projects                 / 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 , 11 , 12 , 13 /
   j        alternatives             / 0 , 1 , 2 , 3 , 4 /
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

Scalar B_total  total budget / 12000000 /;

Parameters
   Benefit(i,j)  PV total benefit /
   1 . 0   0
   1 . 1   1147066
   1 . 2   -1910462
   1 . 3   317734
   2 . 0   0
   2 . 1   1118018
   2 . 2   -1936869
   2 . 3   270993
   3 . 0   0
   3 . 1   -21355578
   4 . 0   0
   4 . 1   -15025870
   5 . 0   0
   5 . 1   1143109
   5 . 2   -1914059
   5 . 3   311366
   6 . 0   0
   6 . 1   1129487
   6 . 2   -1926443
   6 . 3   289447
   7 . 0   -2741473
   7 . 1   0
   7 . 2   -815311
   7 . 3   1356452
   8 . 0   0
   8 . 1   -13914966
   9 . 0   0
   9 . 1   1336809
   9 . 2   -14028218
   9 . 3   -1900702
   10 . 0   0
   10 . 1   110462
   11 . 0   0
   11 . 1   -411858
   12 . 0   0
   12 . 1   1146307
   12 . 2   128853
   12 . 3   1232639
   13 . 0   -1466836
   13 . 1   0
   13 . 2   169733
   13 . 3   310219
   13 . 4   1152514
   /;

Parameter Cost(i,j)  PV total cost /
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