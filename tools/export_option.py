#!/usr/bin/env python3
"""Export one named optional assembly from the released STEP."""
import argparse
from pathlib import Path

from OCP.STEPCAFControl import STEPCAFControl_Writer
from xcad import IFSelect_RetDone, children, name, open_step, walk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Uncompressed BoxTurtle STEP")
    parser.add_argument("option", type=int, choices=range(1, 7))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    doc, tool, (root,) = open_step(str(args.input))
    options = next(d for _, d, _ in children(root) if name(d).startswith("OPTIONS"))
    marker = f"{args.option:02} - "
    found = [(instance, definition) for instance, definition, _ in children(options)
             if name(definition).startswith(marker)]
    if len(found) != 1:
        raise ValueError("The model does not have the requested unique option group")
    occurrence, definition = found[0]
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    for label in [occurrence, definition] + [label for _, i, d, _ in walk(definition) for label in (i, d)]:
        color_tool.SetVisibility(label, True)
    writer = STEPCAFControl_Writer()
    if not writer.Transfer(definition) or writer.Write(str(args.output)) != IFSelect_RetDone:
        raise RuntimeError("OpenCascade could not write the option STEP")
    print(name(definition))


if __name__ == "__main__":
    main()
