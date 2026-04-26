\* ===================================================================== *\
\* MCBOMs Core Optimization Model - LP Format Reference                  *\
\*                                                                       *\
\* Mathematical formulation per Chapter 2 of the MCBOMs Task 4 report.   *\
\*                                                                       *\
\* This file shows the STRUCTURE of an MCBOMs MILP instance in LP        *\
\* format using a minimal 2-project, 4-alternative illustrative example. *\
\*                                                                       *\
\* The LP file format is a flat numeric form - it cannot represent the   *\
\* abstract model symbolically (sets, indexed sums, parameter formulas). *\
\* Any LP file is an INSTANTIATION of the model with specific numbers.   *\
\*                                                                       *\
\* For the abstract symbolic form, see:                                  *\
\*   - models/ampl/00_optimization.mod  (AMPL)                           *\
\*   - models/gams/00_optimization.gms  (GAMS)                           *\
\*                                                                       *\
\* For real validation instances, see:                                   *\
\*   - 01_worked_example.lp                                              *\
\*   - 02_harwood_50m.lp / 02_harwood_10m.lp                             *\
\*   - 03_banihashemi_intersections.lp                                   *\
\* ===================================================================== *\

\* --------------------------------------------------------------------- *\
\* ILLUSTRATIVE INSTANCE                                                 *\
\*                                                                       *\
\* 2 projects, each with 2 alternatives (do-nothing + 1 improvement).    *\
\* Project 1: B_1_1 = $500K, C_1_1 = $200K                              *\
\* Project 2: B_2_1 = $300K, C_2_1 = $150K                              *\
\* Budget: $300K                                                         *\
\* Discretionary cost = total cost (no committed component)              *\
\*                                                                       *\
\* Optimal solution: x_1_1=1 (alt 1 of project 1), x_2_0=0=x_2_1 (do nothing)  *\
\*   No - that violates budget. Optimal is alt 1 in P1 only:             *\
\*  the Eq 2.6 constraint is sum x_ij <= 1, allowing all-zero.)          *\
\* --------------------------------------------------------------------- *\

\* Eq 2.4 - Objective: max sum_ij (Benefit_ij - Cost_disc_ij) * x_ij    *\
Maximize
 OBJ: 300 x_1_1 + 150 x_2_1

\* (Coefficients: 300 = Benefit_1_1 (500) - Cost_disc_1_1 (200);         *\
\*                150 = Benefit_2_1 (300) - Cost_disc_2_1 (150))         *\

Subject To

\* Eq 2.5 - Total budget: sum_ij C_ij * x_ij <= B_total                 *\
 TotalBudget: 200 x_1_1 + 150 x_2_1 <= 300

\* Eq 2.6 - Mutual exclusivity: at most one alt per project              *\
 MutEx_1: x_1_0 + x_1_1 <= 1
 MutEx_2: x_2_0 + x_2_1 <= 1

\* --------------------------------------------------------------------- *\
\* Eq 2.7 - Binary decision variables                                    *\
\* --------------------------------------------------------------------- *\
Binaries
 x_1_0
 x_1_1
 x_2_0
 x_2_1

End

\* ===================================================================== *\
\* HOW THE OTHER LP INSTANCES EXTEND THIS PATTERN                        *\
\*                                                                       *\
\* Each MCBOMs LP instance has the same block structure:                 *\
\*   Maximize: OBJ = sum (B_ij - C_disc_ij) * x_ij                       *\
\*   Subject To:                                                         *\
\*     TotalBudget: sum C_ij * x_ij <= B_total                           *\
\*     MutEx_i: sum_j x_ij <= 1   (one per project)                      *\
\*   Binaries: x_ij                                                      *\
\*                                                                       *\
\* The instances differ in:                                              *\
\*   - Number of projects and alternatives                               *\
\*   - Specific coefficient values (which encode Eq 2.18, 2.21 etc.      *\
\*     evaluated for that case study)                                    *\
\*   - The header comments document how each coefficient was derived     *\
\*     (e.g., 02_harwood_50m.lp has DERIVATION TABLE comments showing    *\
\*     how the obj coefficients trace back to Harwood Tables 2-3)        *\
\*                                                                       *\
\* The optional and network constraints (Eq 2.8, 2.9, 2.10, 2.14, 2.15,  *\
\* 2.16) are not exercised by the current validation instances. When     *\
\* used, they appear as additional constraint rows in the Subject To     *\
\* block, with names matching their AMPL/GAMS counterparts:              *\
\*   Dependency_<i>_<j>_<ip>_<jp>:  x_i_j - x_ip_jp <= 0                 *\
\*   CrossExclusivity_<...>:        x_i_j + x_ip_jp <= 1                 *\
\*   MinBCR_<i>:                    sum (B - theta*C) x_ij >= 0          *\
\*   FacilityBudget_<m>:            sum C_ij x_ij <= B_facility_m        *\
\*   RegionalCap_<r>:               sum C_ij x_ij <= B_region_cap_r      *\
\*   RegionalFloor_<r>:             sum C_ij x_ij >= beta_r * B_total    *\
\* ===================================================================== *\
