# Design handoff

## Current requirements

- Stack two ArmoredTurtle BoxTurtle V1 units vertically, with a stock-style front door per tier. Reuse the original side and rear acrylic outlines. Use one continuous 2020 corner post at each corner.
- Store filament after it has been dried. Keep the two storage chambers separated so opening one door minimizes exposure in the other chamber. The lower rear acrylic has no dryer cutouts.
- Use N3MI-DG Lane-Buffer geometry with four independent buffers and three rear skirt pieces per tier. The prior shared rear hub and skirt are replaced. The original rear fan and its fasteners are retained.
- Give both chambers two front-removable molecular-sieve cassettes and a visible round hygrometer option. Six optional groups appear under **OPTIONS**, hidden by default via STEP directives and supported by a Fusion add-in.

## Coordinate conventions

X spans the lanes. The four centerlines are X = **15, 105, 195, and 285 mm**. Positive Y points to the rear, positive Z points up. The same feature on the upper tier is **400 mm** above its lower-tier counterpart. The 760 mm posts run from Z = −10 to +750, with centers at X = −40 and +340 and Y = 0 and +240. The lower door hinge axis is X = −57, Y = −11.5. Its assembly view is open 80° from closed.

## Decisions and superseded designs

| Decision | Reason |
| --- | --- |
| Separate stock side/rear panels per tier | The roof and base rails interrupt the stock extrusion-slot path. Continuous outside skins were discussed and are outside the shipped geometry. |
| Solid center divider and separate doors | Each tier has its own enclosed volume. |
| Six optional assemblies | The optional lower dryer bulkhead concept was removed. Both-tier storage, seals, sieve cassettes, hygrometers, rear routing, frame ties and anchors are supported by the current geometry. |
| 80° lower door pose | The stock 35° CAD pose intersects the left cassette's front pull path. |
| Side-mounted outer cassette hangers | They leave room for the gauge's rear keeper when both options are shown. |
| Labeled rail-top foam lengths | The prior continuous floor gasket intersected the trays and moving lane hardware. |
| 2.3 mm installed gasket thickness | The nominal 3 mm stack overlapped the stock clip lips. Both roof assemblies use the revised compressed stack. |
| Captive standard M3 hex nuts | The former smooth guide-standoff bores had no screw retention. |
| Stock cross drilling copied from the vendor geometry | It registers the lower and upper frame rails against the common 760 mm posts. |

## Resume here

Use the [shipped STEP](../cad/README.md) for geometry edits. It contains complete assemblies, with actual placements and stock parts preserved. See [build and fit](BUILD-AND-FIT.md) for physical dimensions and [verification](VERIFICATION.md) for tested checks. The photos used during design supplied a 45 mm gauge bezel and 16 mm overall depth. Gauge barrel diameter, retaining tabs, and battery clearance require a measurement from the actual part.
