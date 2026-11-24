# Build and fit notes

All dimensions are millimeters. This is the stacking/enclosure supplement. Use the upstream BoxTurtle and Lane-Buffer instructions for the original mechanisms, wiring and hardware.

| Part or feature | Quantity or dimensions |
| --- | --- |
| Continuous posts | Four 20 × 20 × 760 |
| Cross drill | Ø5.5 through both axes at 10, 90, 350, 410, 490 and 750 from the bottom end |
| Frame envelope | 400 wide × 260 deep × 760 high, excluding feet, trim and dryer dock |
| Tier pitch and metal gap | 400 pitch, 40 gap between lower roof and upper base rail faces |
| Roof rail ring | Per tier, two 360 and two 220 mm 2020 lengths |
| Stock door rails | Per door, two 360 and two 280 mm 2020 lengths. The upstream instructions reuse one base rail. |
| Stock side acrylic | Four total, 232 × 252.4 × 3 |
| Stock rear acrylic | Two total, 371 × 251.4 × 3 |
| Stock door acrylic | Two total, 371 × 251.4 × 3 |
| Solid middle acrylic | One, 372 × 232.4 × 3 with stock outside contour, solid |
| Roof and divider gasket | Nominal 3 mm foam, modeled at 2.3 mm installed thickness |
| Rear lane buffers | Four per tier, 90 mm pitch |

Use the DXF contours for stock acrylic; the envelope dimensions above do not describe the corner reliefs. Mount the loaded upper tier to the metal frame. Confirm drill centerlines against the actual extrusion and rail stack and use the stock blind-joint hardware.

## Options in the Fusion Browser

| Group | Fit and hardware |
| --- | --- |
| 01 Molecular sieve | Two 145 × 68 × 38 mm cassette bodies per tier, roughly 0.31 L gross each. Rear stops, removable 1 mm slotted covers, and M5 T-nut hangers. Install fine media-retaining mesh if needed. Outer hangers attach to the side roof rails, inner hangers to the front roof rail. Open the door to the service position to pull them. |
| 02 Hygrometer | One per tier, visible through the door acrylic. 45.6 mm nominal bezel pocket for the specified 45 × 16 mm gauge, M5 rail attachment, and two M2.5 keeper screws. Check the actual gauge body, clips, air inlet, and battery access. |
| 03 PTFE guides | Four nominal 4 mm tube paths per tier, 4.8 mm modeled bores. Two M3 × 25 cap screws engage standard 5.5 mm AF hex nuts in the underside pockets. M5 T-nuts mount the standoffs. Use actual tube bends and leave operating space around the buffer collets. |
| 04 Air sealing | Eight labeled rail-top strips per tier, 4 mm wide × 1 mm nominal thick, with relief at moving hardware. Active-lane collars and unused-lane plugs are separate groups. The nominal plug tip is 1.9 mm for a measured 2 mm tube bore. |
| 05 Anti-tip anchors | Metal bracket envelopes at the upper rear. Choose fasteners and anchoring for the actual mounting structure. Structural capacity has not been verified. |
| 06 Mid-frame ties | Metal side plates with three Ø5.3 holes each and 4 mm standoffs. Separate reference gauges show the lower roof and upper base drill elevations. |

The [complete Fusion option and fit notes](FUSION-OPTIONS-AND-FIT.txt) also cover service access and application order. After assembly use the per-tier hygrometers, with the active dryer off, to see whether opening one bay affects the other. The foam and feedthrough options have been checked geometrically; chamber leak rate has not been measured.

## Upstream build guides

- [ArmoredTurtle BoxTurtle documentation](https://armoredturtle.org/docs/boxturtle/index.html)
- [BoxTurtle Enclosure assembly manual](https://armoredturtle.org/manual-sections.html?manual=bte)
- [Enclosure BOM at the pinned source](https://github.com/ArmoredTurtle/BoxTurtle-Enclosure/blob/c2940c63be7a276a4c5c59f111fb72c9bd807601/BT_Enclosure_BOM.md)
- [Lane-Buffer assembly and per-lane BOM at the pinned source](https://github.com/N3MI-DG/Lane-Buffer/blob/0a6b0cdb551db7cce285cbef08f7ae515c3962ac/README.md)
