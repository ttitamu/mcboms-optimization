# Scope of this prototype

The current prototype is implemented and validated for the rural two-lane highway use case. Three benchmarks have been reproduced from the published literature, and the framework is ready to extend to the full set of facility types and benefit categories as agency data becomes available.

## Validated benchmarks

| Benchmark | What it validates | Result |
|---|---|---|
| Worked example | The full safety-benefit chain end-to-end on a single segment, from raw per-severity inputs through the optimization | Arithmetic matches the methodology document to within numerical precision across the framework's implementations |
| Harwood (2003) at $50M | The optimization layer reproduces a published case study at the unconstrained budget | All four rigorous metrics match Harwood Table 4 within rounding tolerance; all ten site selections match exactly |
| Harwood (2003) at $10M | The optimization layer at a tight budget where alternative selection becomes binding | The MCBOMs solution has higher net benefit than the published Harwood result because the PNR deferral-cost mechanism is not part of the framework; the divergence is documented and explained |
| Banihashemi (2007) intersection sub-problem | The IHSDM Crash Prediction Module path for intersections | Structural validation passes; rank ordering of left-turn-lane improvements is consistent with the published case |

## Built and ready for agency data

The framework's optional and network-level features are implemented and unit-tested in isolation, but are not exercised by the published validation cases (which do not include the relevant inputs):

- **Project dependency, cross-project exclusivity, and minimum benefit-cost ratio constraints**, available as optional kwargs on the Python `Optimizer` and as conditional constraints in the AMPL and GAMS models
- **Facility-type sub-budgets, regional spending caps, and regional minimum-investment floors**, used when an agency must allocate budget across categories or geography
- **Operational benefit module** (travel-time savings + vehicle operating cost reductions), implemented with USDOT BCA May 2025 default unit values and tested against synthetic inputs
- **Corridor Condition Measures module** (energy, emissions, accessibility, resilience, pavement), with explicit double-counting prevention against the operational benefit
- **Banihashemi full-network case** (135 homogeneous segments plus 13 intersections; 3,385 binary variables): the optimization layer can handle this scale; reproducing the published full-network result requires the segment geometry data that the paper does not publish

These features are activated by populating the corresponding inputs. They are part of the framework as implemented today, ready for an agency use case.

## Where the methodology extends beyond the prototype

A few elements of the methodology are formally documented but await operational use cases to test against:

- **Segment-level treatment composition**, where alternatives are compositions of segment-specific treatments rather than uniform per-project treatments. The cost-decomposition formulation is in Section 2.1.2 of the methodology document. The Python prototype currently uses alternative-level aggregate costs; per-treatment decomposition will be added when an agency provides a treatment-cost catalog.
- **Multi-facility prototype expansion** beyond rural two-lane highways. The benefit modules and optimizer are facility-type-agnostic; bringing in urban, freeway, and intersection-only cases requires the corresponding parametric inputs (CMF tables, capacity functions, etc.).

These are not gaps in the framework; they are deliberate scoping decisions that match the data currently available.
