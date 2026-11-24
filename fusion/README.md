# BoxTurtle Options toolbar in Autodesk Fusion

The add-in runs in desktop Autodesk Fusion on Windows and macOS. It adds a **BoxTurtle Options** tab to the **Design** workspace and lets you show or hide the six optional assemblies in the shipped BoxTurtle-Stack STEP.

## 1. Open the BoxTurtle assembly

1. Follow the [CAD download instructions](../cad/README.md) to extract `BoxTurtle-V1-Dual-Tier.step`.
2. In desktop Fusion, choose **File → Upload** and select that STEP file. Wait for translation, then open the resulting design from the Data Panel.
3. In the Browser, expand the imported assembly and locate **OPTIONS - use visibility to show each group**. It contains six numbered components, **01** through **06**. Keep those names and the assembly structure intact for the add-in.

[Autodesk's STEP import instructions](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-import-or-open-a-STEP-file-in-Fusion-360.html)

## 2. Install and start the toolbar

1. [Download BoxTurtle-Fusion-Options.zip](BoxTurtle-Fusion-Options.zip?raw=true) and extract it into a folder you plan to keep.
2. Locate the **BoxTurtleOptions** folder inside the extracted archive. It must contain both `BoxTurtleOptions.py` and `BoxTurtleOptions.manifest`. You can also use the equivalent [source folder](BoxTurtleOptions/) from a checkout.
3. From the **Design** workspace in desktop Fusion, open **Utilities → Add-Ins → Scripts and Add-Ins**.
4. Select the **Add-Ins** tab. Click **+**, choose **Script or add-in from device** if Fusion shows that menu, then select the **BoxTurtleOptions** folder itself.
5. Select **BoxTurtleOptions** in the list and click **Run**. In the top toolbar, open **BoxTurtle Options → Show options**.
6. For automatic loading, check **Run on Startup** for the add-in if that control is shown. Leave the linked folder in place so Fusion can find it after restarting.

[Autodesk's add-in installation instructions](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954)

## 3. Show or hide parts

The first time the add-in recognizes a design, it turns all six optional assemblies off. In **Show options**, select the groups you want and click **OK**. The checkboxes reflect the current Browser visibility. Save the Fusion design to keep the chosen states and the one-time initialization marker.

| Checkbox | What it shows |
| --- | --- |
| Molecular sieve cassettes | Two front-pull trays and their hangers per tier |
| Hygrometer brackets | The cradles, rear keepers, and meter reference envelopes |
| Rear PTFE guides | The tube combs, caps, standoffs, and captive M3 nut references |
| Floor seals and feedthrough plugs | Rail-top foam lengths, collars, and unused-lane plugs |
| Anti-tip brackets | Upper rear anchor bracket envelopes |
| Frame joints and drill template | Mid-frame metal tie plates, spacers, and transfer gauges |

You can also toggle the individual groups with the visibility icons in the Fusion Browser. Keep the parent **OPTIONS** component visible to use the child toggles. The add-in changes visibility only. See the [fit notes](../docs/FUSION-OPTIONS-AND-FIT.txt) before fabricating the optional parts.

## Quick check in Fusion

1. On a fresh import, run the add-in. Check that **BoxTurtle Options → Show options** lists six unchecked boxes.
2. Enable only **Molecular sieve cassettes** and click **OK**. The cassettes should appear on both tiers. Open the dialog again and check that only that box is selected.
3. Enable **Hygrometer brackets** too, save the Fusion design, then close and reopen it. Both choices should persist.
4. Turn both choices off. The core frame, doors, and lane-buffer assemblies should remain visible.

## Troubleshooting and updates

- **No toolbar tab** — Confirm you are in the **Design** workspace and that **BoxTurtleOptions** is running in the **Add-Ins** tab. Confirm both files are inside the linked folder.
- **The command asks you to open a BoxTurtle design** — Activate the translated BoxTurtle-Stack STEP design. Check that the named **OPTIONS** component and all six numbered children are present in the Browser. If the file came through a flattened export, import the supplied STEP again.
- **Options are visible immediately after import** — Some importers can discard STEP visibility flags. Start the add-in for a fresh design or toggle the six groups in the Browser. A previously initialized and saved design keeps its last selection.
- **Update the add-in** — Stop the old copy in **Add-Ins** before replacing its files. Either replace the contents of the linked folder or use **Unlink** and link the new extracted folder. Then select it and click **Run**. Keep only one copy linked.
- **Remove the toolbar** — Click **Stop** to remove the UI for the current session. Disable **Run on Startup** or unlink the add-in if you no longer need it.

The UI behavior is covered by the [mock smoke test](../tools/test_fusion_options.py). The quick check above still needs a desktop Fusion session.
