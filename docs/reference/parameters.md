# Default Parameters

The framework ships with USDOT Benefit-Cost Analysis Guidance for Discretionary Grant Programs (May 2025) default values. All values are in 2023 dollars unless noted otherwise.

## Discounting

| Parameter | Value | Source |
|---|---|---|
| Discount rate | 7% real | USDOT BCA May 2025 |
| Analysis horizon | 20 years | USDOT BCA May 2025 |
| Present Worth Factor (PWF) | 10.594 | Computed from $r=0.07$, $T=20$ |

## Crash unit costs (KABCO scale)

| Severity | Code | Unit cost (2023 $) | Source |
|---|---|---|---|
| Fatal | K | $13,200,000 | USDOT BCA May 2025 Table A-1 |
| Incapacitating injury | A | $1,254,700 | USDOT BCA May 2025 Table A-1 |
| Non-incapacitating injury | B | $246,900 | USDOT BCA May 2025 Table A-1 |
| Possible injury | C | $118,000 | USDOT BCA May 2025 Table A-1 |
| Property damage only | O | $5,300 | USDOT BCA May 2025 Table A-1 |

## Value of Time

| Trip purpose | Value (2023 $) | Source |
|---|---|---|
| All purposes | $21.10 / person-hour | USDOT BCA May 2025 Table A-2 |
| Personal | $19.40 / person-hour | USDOT BCA May 2025 Table A-2 |
| Business | $33.50 / person-hour | USDOT BCA May 2025 Table A-2 |

## Vehicle parameters

| Parameter | Value | Source |
|---|---|---|
| Average vehicle occupancy (passenger) | 1.52 | USDOT BCA May 2025 Table A-3 |
| Vehicle Operating Cost (light-duty) | $0.56 / vehicle-mile | USDOT BCA May 2025 Table A-4 |

## Overriding defaults

State agencies may override these with state-specific values.

**In the solver-language models** — edit the parameter values directly in the relevant `.dat` file (AMPL) or at the top of the `.gms` file (GAMS). The values are explicit at the top of each instance file.

**In the Python implementation** — edit `src/mcboms/utils/economics.py` to change globally, or pass values as arguments to the relevant functions.

**In the Excel workbooks** — edit the parameter cells directly on the input sheet of each workbook in `docs/models/excel/`. The Solver setup will pick up the new values on the next run.

For HSIP-context applications, FHWA-SA-25-021 (October 2025) documents a per-capita-income procedure for adjusting national crash costs to state-specific values.
