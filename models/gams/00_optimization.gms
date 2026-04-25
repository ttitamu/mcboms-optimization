$TITLE MCBOMs Core Optimization Model (GAMS)
$ONTEXT
   =====================================================================
   MCBOMs Optimization Layer - GAMS model
   Mathematical formulation per Chapter 2 of the MCBOMs Task 4 report.
   This file encodes Eq 2.4 - 2.10 (project-level) and Eq 2.14 - 2.16
   (network-level extensions). Benefit and cost values are computed in
   the corresponding instance files (e.g., 02_harwood_50m.gms includes
   this layer plus the benefit-side equations Eq 2.18, 2.21).

   Optional and network-level constraints are activated by populating
   the corresponding sets. When the sets are empty, the constraints
   are vacuously satisfied.

   This is the abstract / template model. Run an instance file
   (e.g., 02_harwood_50m.gms) to solve a specific case study.
   =====================================================================
$OFFTEXT

* ---------------------------------------------------------------------
* Sets
* ---------------------------------------------------------------------

Sets
   i           projects (sites, intersections)
   j           alternative IDs
   ;

Set ij(i,j)        valid project-alternative pairs;

* Optional: dependency pairs - alternative (i,j) requires (ip,jp)
Set deps(i,j,ip,jp)    dependency pairs;

* Optional: conflict pairs - alternatives (i,j) and (ip,jp) cannot both be selected
Set conflicts(i,j,ip,jp)   conflict pairs;

* Optional: facility-type partitioning
Sets
   m           facility types
   facilityProjects(m,i)   projects in each facility type
   ;

* Optional: regional partitioning
Sets
   r           regions
   regionProjects(r,i)     projects in each region
   ;

* ---------------------------------------------------------------------
* Parameters
* ---------------------------------------------------------------------

Scalar B_total      total program budget;
Scalar theta        minimum benefit-cost ratio (0 disables);

Parameters
   Benefit(i,j)     PV total benefit
   Cost(i,j)        PV total cost (full)
   Cost_disc(i,j)   discretionary cost component (defaults to Cost)
   B_facility(m)    facility-type sub-budget
   B_region_cap(r)  regional cap
   beta_region(r)   regional minimum-investment fraction
   ;

* If Cost_disc not explicitly set in instance, default to Cost
Cost_disc(i,j)$(ij(i,j) and Cost_disc(i,j) = 0) = Cost(i,j);

* ---------------------------------------------------------------------
* Decision variables (Eq 2.7)
* ---------------------------------------------------------------------

Binary Variable x(i,j)   alternative selection;
Variable Z               total net benefit;

* ---------------------------------------------------------------------
* Equations
* ---------------------------------------------------------------------

Equations
   Objective                 'Eq 2.4 - objective function'
   TotalBudget               'Eq 2.5 - total budget'
   MutualExclusivity(i)      'Eq 2.6 - mutual exclusivity'
   Dependency(i,j,ip,jp)     'Eq 2.8 - dependency (optional)'
   CrossExclusivity(i,j,ip,jp)  'Eq 2.9 - cross-project exclusivity (optional)'
   MinBCR(i)                 'Eq 2.10 - minimum benefit-cost ratio (optional)'
   FacilityBudget(m)         'Eq 2.14 - facility-type sub-budget'
   RegionalCap(r)            'Eq 2.15 - regional cap'
   RegionalFloor(r)          'Eq 2.16 - regional minimum-investment floor'
   ;

* Eq 2.4 - objective
Objective ..
   Z =E= sum(ij(i,j), (Benefit(i,j) - Cost_disc(i,j)) * x(i,j));

* Eq 2.5 - total budget
TotalBudget ..
   sum(ij(i,j), Cost(i,j) * x(i,j)) =L= B_total;

* Eq 2.6 - mutual exclusivity (at most one alternative per project)
MutualExclusivity(i) ..
   sum(ij(i,j), x(i,j)) =L= 1;

* Eq 2.8 - dependency: (i,j) selected implies (ip,jp) selected
Dependency(i,j,ip,jp)$deps(i,j,ip,jp) ..
   x(i,j) =L= x(ip,jp);

* Eq 2.9 - cross-project exclusivity
CrossExclusivity(i,j,ip,jp)$conflicts(i,j,ip,jp) ..
   x(i,j) + x(ip,jp) =L= 1;

* Eq 2.10 - minimum BCR per project (active only when theta > 0)
MinBCR(i)$(theta > 0) ..
   sum(ij(i,j), Benefit(i,j) * x(i,j))
     =G= theta * sum(ij(i,j), Cost(i,j) * x(i,j));

* Eq 2.14 - facility-type sub-budget
FacilityBudget(m) ..
   sum((i,j)$(ij(i,j) and facilityProjects(m,i)), Cost(i,j) * x(i,j))
     =L= B_facility(m);

* Eq 2.15 - regional cap
RegionalCap(r) ..
   sum((i,j)$(ij(i,j) and regionProjects(r,i)), Cost(i,j) * x(i,j))
     =L= B_region_cap(r);

* Eq 2.16 - regional minimum-investment floor
RegionalFloor(r) ..
   sum((i,j)$(ij(i,j) and regionProjects(r,i)), Cost(i,j) * x(i,j))
     =G= beta_region(r) * B_total;

Model mcboms_core / all /;

* This file is the abstract model. To solve, use an instance file
* (e.g., 02_harwood_50m.gms) that includes this model and provides data.
