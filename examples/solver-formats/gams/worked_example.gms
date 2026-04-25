$TITLE Worked Example - MCBOMs Eq 2.18 (safety benefit) full chain
$ONTEXT
   MCBOMs Task 4 Report, Chapter 2 Section 2.3.7
   5-mile rural two-lane segment, 6 crashes/yr, CMF 0.88
   Severity distribution per HSM defaults; unit costs USDOT BCA May 2025
   Discount rate 7%, horizon 20 years
   Expected: annual benefit $211,810; PV benefit $2,243,913
$OFFTEXT

* ----------------------------------------------------------------
* Sets
* ----------------------------------------------------------------

Sets
   s    severity levels (KABCO)  / K, A, B, C, O /
   i    projects                 / 1 /
   j    alternatives             / 0, 1 /
   ;

Set ij(i,j)  valid project-alternative pairs /
   1 . 0
   1 . 1
   /;

* ----------------------------------------------------------------
* Raw input parameters
* ----------------------------------------------------------------

Scalar N            'observed crashes per year'      / 6.0 /;
Scalar CMF          'crash modification factor'      / 0.88 /;
Scalar r            'discount rate'                  / 0.07 /;
Scalar T            'analysis horizon (years)'       / 20 /;
Scalar TreatmentCost 'cost of treatment'             / 750000 /;
Scalar B_total      'total budget'                   / 1000000 /;

Parameter p(s)      'severity proportion' /
   K  0.013
   A  0.065
   B  0.095
   C  0.117
   O  0.710
   /;

Parameter UC(s)     'unit crash cost USD (USDOT BCA May 2025)' /
   K  13200000
   A  1254700
   B  246900
   C  118000
   O  5300
   /;

* ----------------------------------------------------------------
* Derived parameters - Eq 2.18 chain
* ----------------------------------------------------------------

* Present worth factor PWF(r,T) = ((1+r)^T - 1) / (r * (1+r)^T)
Scalar PWF;
PWF = (power(1+r, T) - 1) / (r * power(1+r, T));

* E_nobuild_s: expected crashes by severity, no-build
Parameter E_nobuild(s);
E_nobuild(s) = N * p(s);

* E_build_s for the active treatment alternative (CMF uniform across severity)
Parameter E_build(s);
E_build(s) = E_nobuild(s) * CMF;

* Annual safety benefit by alternative (Eq 2.18 inner sum)
Parameter B_safety_year(i,j);
B_safety_year(i,'0') = 0;
B_safety_year(i,'1') = sum(s, (E_nobuild(s) - E_build(s)) * UC(s));

* Present-value safety benefit
Parameter B_safety_PV(i,j);
B_safety_PV(i,j) = B_safety_year(i,j) * PWF;

* Total benefit (only safety relevant here)
Parameter Benefit(i,j);
Benefit(i,j) = B_safety_PV(i,j);

* Cost
Parameter Cost(i,j);
Cost(i,'0') = 0;
Cost(i,'1') = TreatmentCost;

* ----------------------------------------------------------------
* Variables
* ----------------------------------------------------------------

Binary Variable x(i,j)    'alternative selection';
Variable Z                'total net benefit';

Equations
   Objective              'Eq 2.4 - objective'
   TotalBudget            'Eq 2.5 - total budget'
   MutualExclusivity(i)   'Eq 2.6 - mutual exclusivity'
   ;

Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost(i,j)) * x(i,j));

TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;

Model worked_example / all /;
Solve worked_example using MIP maximizing Z;

Display PWF, B_safety_year, B_safety_PV, Z.l, x.l;
