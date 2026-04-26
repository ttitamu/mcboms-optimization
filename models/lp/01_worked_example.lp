\* Worked Example - MCBOMs Eq 2.18 (safety benefit) full chain *\
\* Reference: MCBOMs Task 4 Report Section 2.3.7 *\
\* 5-mile rural two-lane segment, 6 crashes/yr, CMF 0.88 *\
\* USDOT BCA May 2025 unit costs, r=0.07, T=20, PWF=10.594 *\
\*  *\
\* Per-alternative coefficient derivation: *\
\*   Annual safety benefit = Sum_s [N * p_s * (1-CMF)] * UC_s = $211,810 *\
\*   PV safety benefit (alt 1) = $2,243,914 *\
\*   Treatment cost (alt 1)    = $750,000 *\
\*   Net benefit (alt 1)       = $1,493,914 *\
\*   Net benefit (alt 0)       = $0 *\
\* Expected optimal Z = $1,493,914 (alt 1 selected within $1M budget) *\
\* Worked_Example *\
Maximize
OBJ: 1493913.91974 x_1_1
Subject To
MutEx_1: x_1_0 + x_1_1 <= 1
TotalBudget: 750000 x_1_1 <= 1000000
Binaries
x_1_0
x_1_1
End
