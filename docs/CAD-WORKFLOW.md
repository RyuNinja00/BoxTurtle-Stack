# CAD workflow and provenance

## Start from the shipped model

Use [CAD retrieval](../cad/README.md) to restore the exact released STEP. It is the editable exchange model, including individual assemblies, stock solids, mounting details and references. The repo does not contain a native Fusion feature-history file.

For OpenCascade verification or extracting an option, install the pinned environment in a Python 3.11 or 3.12 virtual environment:

```sh
python -m pip install -r tools/requirements.txt
python tools/verify_dry_storage.py downloads/BoxTurtle-V1-Dual-Tier.step
python tools/export_option.py downloads/BoxTurtle-V1-Dual-Tier.step 1 sieve-cassettes.step
```

For broader solid collision comparison across the custom options and tier boundaries, run `python tools/inspect_clearance.py downloads/BoxTurtle-V1-Dual-Tier.step`. Foam, threads, and designed mating contacts can produce geometric overlaps in a clearance run, so assess reports in context.

## Pinned primary sources

| Source | Pin and assets used |
| --- | --- |
| ArmoredTurtle BoxTurtle Enclosure V1.0 | [c2940c63be7a276a4c5c59f111fb72c9bd807601](https://github.com/ArmoredTurtle/BoxTurtle-Enclosure/tree/c2940c63be7a276a4c5c59f111fb72c9bd807601), `CAD.zip → CAD/BTE V1.0.step` contains the full BoxTurtle and enclosure assembly. The three stock `Panels/` DXFs are copied into this repo. |
| N3MI-DG Lane-Buffer | [0a6b0cdb551db7cce285cbef08f7ae515c3962ac](https://github.com/N3MI-DG/Lane-Buffer/tree/0a6b0cdb551db7cce285cbef08f7ae515c3962ac), `STEP/Lane Buffer.step`. The project also provides printable STLs and a hardware BOM. |

Both upstream projects license these models under GPLv3. The shipped STEP records their URLs and revisions in its header.

## Rebuilding the stages

`python tools/rebuild.py --work-dir rebuild-work` assembles the recipe in a clean workspace. It downloads the pinned upstream files, uses the recorded stock post measurements, and runs the following stages in order:

1. Extract the complete original BoxTurtle V1 geometry and build the shared 760 mm frame, independent front doors and divider.
2. Reference the official Lane-Buffer assembly and fit the three-piece rear skirt and four buffer placements per tier.
3. Build the accessory option groups and service pose. The source door's pivot is X = −57, Y = −11.5. The source assembly pose is 35° from closed. The service-pose correction applies an additional 45° of opening around that pivot.
4. Install the dry-storage refinements, remove the lower dryer option, compress the modeled gasket stacks, replace the floor template with rail strips, add captive M3 hardware and apply the measured upright drill pattern. Write and reimport the final STEP.

The [stage source directory](../tools/rebuild-stages/) retains the work used to produce the assembly, including the original cross-hole survey and the clearance-tested edits. The delivery STEP, its hash, and the verification output are the release baseline. The clean-workspace runner was assembled from the working stages. An end-to-end rebuild of the runner has not yet been independently verified, and OpenCascade exports can differ at the byte level. Use geometry checks when comparing regenerated output.
