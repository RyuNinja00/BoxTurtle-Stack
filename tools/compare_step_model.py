#!/usr/bin/env python3
"""Compare BoxTurtle STEP model records while ignoring export headers and appearance."""
import argparse
import hashlib
from itertools import zip_longest
from pathlib import Path
import re

ENTITY = re.compile(rb"^#\d+\s*=\s*([A-Z_]+)\b")
APPEARANCE = {
    b"COLOUR_RGB",
    b"CURVE_STYLE",
    b"DRAUGHTING_PRE_DEFINED_COLOUR",
    b"DRAUGHTING_PRE_DEFINED_CURVE_FONT",
    b"FILL_AREA_STYLE",
    b"FILL_AREA_STYLE_COLOUR",
    b"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION",
    b"OVER_RIDING_STYLED_ITEM",
    b"PRESENTATION_STYLE_ASSIGNMENT",
    b"STYLED_ITEM",
    b"SURFACE_SIDE_STYLE",
    b"SURFACE_STYLE_FILL_AREA",
    b"SURFACE_STYLE_RENDERING_WITH_PROPERTIES",
    b"SURFACE_STYLE_TRANSPARENT",
    b"SURFACE_STYLE_USAGE",
}


def model_records(path):
    with path.open("rb") as stream:
        for line in stream:
            if line.strip() == b"DATA;":
                break
        else:
            raise ValueError(f"Missing STEP data section in {path}")
        record = bytearray()
        excluded = False
        for line in stream:
            if line.startswith(b"#"):
                if record and not excluded:
                    yield bytes(record)
                record = bytearray(line)
                match = ENTITY.match(line)
                excluded = bool(match and match[1] in APPEARANCE)
            elif line.strip() == b"ENDSEC;":
                if record and not excluded:
                    yield bytes(record)
                return
            else:
                record.extend(line)
        raise ValueError(f"Missing end of STEP data section in {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("rebuilt", type=Path)
    args = parser.parse_args()
    digest = hashlib.sha256()
    count = 0
    for reference, candidate in zip_longest(model_records(args.reference), model_records(args.rebuilt)):
        if reference != candidate:
            where = (reference or candidate).split(b"=", 1)[0].decode("ascii")
            raise SystemExit(f"Non-appearance STEP records differ at {where.strip()}")
        digest.update(reference)
        count += 1
    print(f"{count:,} matching STEP model records (including placements and visibility directives)")
    print(f"Model-record SHA-256: {digest.hexdigest()}")


if __name__ == "__main__":
    main()
