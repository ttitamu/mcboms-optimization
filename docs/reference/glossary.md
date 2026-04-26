# Glossary

## A

**AADT** — Annual Average Daily Traffic. Vehicles per day at a location, averaged over a year.

**AMF** — Accident Modification Factor. Multiplier (typically 0.5–1.5) representing the safety effect of a treatment on expected crashes. AMF < 1 means crash reduction. The current term in the literature is CMF; both terms are used interchangeably here.

## B

**BCA** — Benefit-Cost Analysis.

## C

**CMF** — Crash Modification Factor. The current term for what was historically called AMF. Both terms appear in the literature; this framework treats them synonymously.

**CPM** — Crash Prediction Module. A statistical model (originally implemented in IHSDM) that predicts expected annual crashes at intersections from ADTs and intersection attributes. The form used in MCBOMs is the IHSDM CPM as documented in FHWA-RD-99-207.

## H

**HSM** — Highway Safety Manual (AASHTO 2010). The standard reference for safety performance functions and crash modification factors.

## I

**IHSDM** — Interactive Highway Safety Design Model. FHWA software (FHWA-RD-99-207) that includes the original parametric crash prediction module for two-lane rural roads.

## K

**KABCO** — Five-level crash severity scale used throughout U.S. transportation safety analysis: K = fatal, A = incapacitating injury, B = non-incapacitating injury, C = possible injury, O = property damage only.

## M

**MILP** — Mixed-Integer Linear Programming. The optimization technique on which MCBOMs is built.

## P

**PDO** — Property Damage Only. The "O" in KABCO.

**PNR** — Penalty for Not Resurfacing. A deferral cost mechanism in the original RSRAP framework, applied to do-nothing alternatives. Not implemented in MCBOMs because per-site values are not published in the source literature.

**PRP** — Penalty for Resurfacing-only Project. A penalty in the original RSRAP framework applied when a site is resurfaced without geometric improvements. Not implemented in MCBOMs.

**PSB** — Present value of Safety Benefits. Notation from the RSRAP literature.

**PTOB** — Present value of Traffic Operational Benefits. Notation from the RSRAP literature.

**PV** — Present Value.

**PWF** — Present Worth Factor. The factor that converts a stream of equal annual payments to a single present value. Formula: $PWF(r, T) = \frac{(1+r)^T - 1}{r \cdot (1+r)^T}$. For $r=0.07$, $T=20$: PWF = 10.594.

## R

**RRR** — Resurfacing, Restoration, Rehabilitation. The federal program category that funds the kind of pavement work the validation case studies address.

**RSRAP** — Resurfacing Safety Resource Allocation Program. The original optimization tool for safety resource allocation within RRR projects, documented in Harwood et al. (2003).

## S

**SPF** — Safety Performance Function. A statistical model that predicts expected crashes from facility characteristics.

## T

**TRR** — Transportation Research Record. Peer-reviewed journal of the Transportation Research Board.

## V

**VOC** — Vehicle Operating Cost. Per-mile fuel, maintenance, and tire costs.

**VOT** — Value of Time. Hourly rate at which travelers value their time, used to monetize travel time savings.
