# Working on BoxTurtle-Stack

Read [DESIGN-HANDOFF](docs/DESIGN-HANDOFF.md) and [CAD-WORKFLOW](docs/CAD-WORKFLOW.md) before changing the model. Start from the shipped, verified STEP when editing an existing assembly. Use the pinned upstream sources when replacing a stock part.

- Units are millimeters. Global X spans the four lanes, +Y points toward the rear, +Z points up. The upper tier is a 400 mm translation.
- Preserve the two independent dry chambers, front cassette access, four individual lane buffers per tier, and the six named option groups. The lower bay is dry storage and uses uncut rear acrylic.
- Preserve the lower door service pose at 80° and verify the full 90 mm cassette pull path if changes affect it.
- Re-run the latest-model verification after export. Record actual CAD checks separately from any physical or Fusion checks you have performed.
- Keep the Fusion add-in, delivery archive, checksums, and documentation synchronized. Keep superseded scratch exports out of published CAD.
