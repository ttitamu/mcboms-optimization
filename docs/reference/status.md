# Validation Status and Known Limitations

## What is validated

- **Worked example (Section 2.3.7)**: arithmetic verified against the MCBOMs Methodology document to the cent, in Python and AMPL/GAMS/LP.
- **Harwood $50M**: 4 of 4 rigorous metrics match Harwood Table 4 within $5 (rounding). 10 of 10 site selections match exactly.
- **Harwood $10M**: documented +5.5% divergence on net benefit. The MCBOMs solution has higher net benefit than Harwood's because PNR is not implemented.
- **Banihashemi intersection sub-problem**: structural validation passes. Int 12 LTL identified as most cost-effective, signalization at Int 3/4 rejected, rank ordering of LTL improvements consistent with Banihashemi Table 5.
- **Cross-validation against TTI BCA spreadsheet**: 35 segment-alternative pairs checked, $0.00 maximum error after applying the 10.594× present-worth factor bridge.

## What is implemented but not yet externally validated

The optional constraints (Eq 2.8 dependency, Eq 2.9 cross-project exclusivity, Eq 2.10 minimum BCR) are formulated and the AMPL `00_optimization.mod` and GAMS `00_optimization.gms` support them. They are not exercised by the current validation cases. They will be tested when an agency provides a use case.

## What is documented but not yet implemented

- **`operations.py`**: Operational benefit module (Eq 2.21). Formulation is locked; implementation follows the same pattern as `safety.py`.
- **`ccm.py`**: Corridor condition benefit module (Eq 2.27). Computational structure is locked; per-category monetization functions to be added incrementally.
- **Network-level constraints in the Python optimizer**: Eq 2.14–2.16 (facility-type sub-budget, regional cap, regional floor) are in the AMPL and GAMS models but not yet wired into the Python `Optimizer` class.

## What is documented as a deferred enhancement

- **Banihashemi full-network validation**: the published Banihashemi case has 135 homogeneous segments plus 13 intersections (3,385 binary variables). We currently validate the intersection sub-problem. Full-network validation requires segment geometry data not published in the paper.
- **Segment-level treatment composition**: Section 2.1.2 documents this concept (per FHWA reviewer requirement) and the Eq 2.5a cost decomposition. The Python prototype currently uses alternative-level aggregate costs. Per-treatment decomposition will be added when an agency provides treatment-cost catalog data.

## Known data quality concerns

- The Task 4 BCA spreadsheet has an operational benefit formula in cell AH3 with documented unit-conversion and missing-AADT issues. The framework's correct Eq 2.21 implementation will not match the spreadsheet output until the spreadsheet formula is corrected. Tracking this with the spreadsheet maintainer.
