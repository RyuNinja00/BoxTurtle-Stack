# BoxTurtle-Stack

A two-tier dry-storage enclosure for the **ArmoredTurtle BoxTurtle V1**. The assembly has eight filament lanes, two independently accessible chambers, four continuous 2020 posts and a solid gasketed divider. Load pre-dried spools and maintain humidity with molecular sieve cassettes. The lower chamber uses stock rear acrylic without dryer cutouts.

## Open the CAD

1. Retrieve the STEP using [the CAD download instructions](cad/README.md).
2. Upload `BoxTurtle-V1-Dual-Tier.step` in Fusion, then open the resulting design from the Data Panel.
3. Expand **OPTIONS** in the Browser to show any of the six assemblies. The STEP carries hidden-by-default directives. The [Fusion add-in](fusion/README.md) applies the defaults and provides a **BoxTurtle Options** tab if the importer drops those flags.

The lower door is shown at its **80° cassette-service pose** and the upper door is closed.

For the dedicated toolbar, see the **[BoxTurtle Options installation and troubleshooting guide](fusion/README.md)**.

## Project references

| Start here | Contents |
| --- | --- |
| [Build and fit notes](docs/BUILD-AND-FIT.md) | Geometry, hardware, service access and checks before cutting or drilling |
| [Design handoff](docs/DESIGN-HANDOFF.md) | Requirements, decisions, known limits and where to resume |
| [CAD workflow](docs/CAD-WORKFLOW.md) | Pinned upstream CAD, source-stage scripts, and verification |
| [Verification record](docs/VERIFICATION.md) | Measured facts, collision checks, and outstanding physical checks |
| [AGENTS.md](AGENTS.md) | Short instructions for future contributors and agents |

The shipped STEP is the authoritative assembly for this revision. It contains the full tier assemblies, eight lane buffers, the frame and enclosure, and the six optional subassemblies. Keep the model and Fusion option labels in sync when changing either one.

## Upstream and license

This model adapts the ArmoredTurtle BoxTurtle Enclosure V1.0 CAD and N3MI-DG Lane-Buffer CAD. Both source revisions and the stock panel files are documented in [the CAD workflow](docs/CAD-WORKFLOW.md). The CAD and build sources are supplied under [GPL-3.0](LICENSE), with upstream attribution in the STEP header.
