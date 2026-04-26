\* Harwood et al. (2003) - Harwood 10M *\
\* Reference: Harwood (2003), TRR 1840, Tables 2 and 3 *\
\* 10-site case study, mix of rural/urban undivided/divided 2- and 4-lane *\
\* Objective uses discretionary cost convention (Harwood/Chapter 2 Section 2.2.1): *\
\*   max Sum (B - SafetyImprovementCost) * x *\
\* Budget uses total cost (resurfacing + safety): *\
\*   Sum (ResurfacingCost + SafetyImprovementCost) * x <= B_total *\
\*  *\
\* Per-alternative coefficient = total_benefit - safety_improvement_cost *\
\* Expected optimal objective Z = $4,931,520 *\
\* Harwood_10M *\
Maximize
OBJ: 1356661 x_10_1 + 35107 x_1_1 + 279756 x_2_1 + 628606 x_3_1 + 261392 x_4_1
 + 1168618 x_5_1 + 341437 x_6_1 + 680641 x_7_1 + 525644 x_8_1 + 590056 x_8_2
 + 817238 x_9_1
Subject To
MutEx_1: x_1_0 + x_1_1 <= 1
MutEx_10: x_10_0 + x_10_1 <= 1
MutEx_2: x_2_0 + x_2_1 <= 1
MutEx_3: x_3_0 + x_3_1 <= 1
MutEx_4: x_4_0 + x_4_1 <= 1
MutEx_5: x_5_0 + x_5_1 <= 1
MutEx_6: x_6_0 + x_6_1 <= 1
MutEx_7: x_7_0 + x_7_1 <= 1
MutEx_8: x_8_0 + x_8_1 + x_8_2 <= 1
MutEx_9: x_9_0 + x_9_1 <= 1
TotalBudget: 2541150 x_10_1 + 528803 x_1_1 + 639763 x_2_1 + 1381621 x_3_1
 + 1047816 x_4_1 + 1420017 x_5_1 + 3068549 x_6_1 + 1863237 x_7_1
 + 1578989 x_8_1 + 2078989 x_8_2 + 1701302 x_9_1 <= 10000000
Binaries
x_10_0
x_10_1
x_1_0
x_1_1
x_2_0
x_2_1
x_3_0
x_3_1
x_4_0
x_4_1
x_5_0
x_5_1
x_6_0
x_6_1
x_7_0
x_7_1
x_8_0
x_8_1
x_8_2
x_9_0
x_9_1
End
