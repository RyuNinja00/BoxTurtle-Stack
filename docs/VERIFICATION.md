# Verification record

The published STEP was reimported using OpenCascade after writing. [Console output](verified-step-output.txt) records the final passing checks.

- Six option subassemblies and six STEP visibility directives. Lower dryer geometry is absent.
- Four 20 × 20 × 760 mm uprights, each with both axes of the stock-derived Ø5.5 cross holes at the six elevations.
- Lower divider and upper roof clear the stock clips, covers and screws at the modeled compressed gasket stack.
- All 16 labeled floor-strip lengths clear the installed baseline assemblies. Captive M3 nuts fit their pockets without volumetric overlap.
- The lower door retains its 80° service pose. A prior check in the same cassette configuration verified the full 90 mm cassette pull envelopes at that pose and the closed upper door with the cassette and gauge installed.
- Prior targeted CAD checks verified gauge/cradle/keeper mating, clear cassette and guide hardware assemblies, and four lane buffers per tier on 90 mm pitch. The storage layout was checked against a modeled 210 mm spool envelope.

A [clean, one-pass rebuild](rebuild-verification.txt) reproduced all 2,454,099 non-appearance STEP model records in the published file. The Fusion ZIP/source match, toolbar registration, option toggles, per-design defaults, and cleanup passed the [mock toolbar smoke test](../tools/test_fusion_options.py). Run it with `python tools/test_fusion_options.py`. Actual Fusion desktop behavior, brackets and anchors under load, the real hygrometer body, actual spool insertion, and assembled humidity isolation still require physical or application checks.

The CAD file archive and extracted STEP are verified independently by [the CAD retrieval script](../tools/get_cad.py).
