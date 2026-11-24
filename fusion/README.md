# Fusion options

Extract `BoxTurtle-Fusion-Options.zip`, then in Fusion open **Utilities → Scripts and Add-Ins → Add-Ins**. Use **+** to add the extracted `BoxTurtleOptions` folder and click **Run**. Find **BoxTurtle Options → Show options** in the Design workspace.

The add-in detects the six option subassemblies in the open design. It applies the all-off default the first time it recognizes a design and remembers that initialization when you save the Fusion document. It controls visibility and uses the existing STEP geometry.

The unpacked add-in source is in [BoxTurtleOptions](BoxTurtleOptions/). See the [fit notes](../docs/FUSION-OPTIONS-AND-FIT.txt) for each group's intent. The add-in logic was verified with a mock Fusion design. A desktop Fusion test is pending.
