"""Normalize the lower door occurrence when the STEP writer drops its transform."""
import math
from pathlib import Path
import re
import sys

model = Path(sys.argv[1])
body = model.read_bytes()


def one(pattern):
    matches = list(re.finditer(pattern, body, re.M))
    if len(matches) != 1:
        raise ValueError(f"Expected one STEP match, got {len(matches)}: {pattern!r}")
    return matches[0]


def product_definition(prefix):
    product = one(rb"^(#\d+)\s*=\s*PRODUCT\(\s*'" + re.escape(prefix)).group(1)
    formation = one(rb"^(#\d+)\s*=\s*PRODUCT_DEFINITION_FORMATION\('','',\s*" + product + rb"\s*\);").group(1)
    return one(rb"^(#\d+)\s*=\s*PRODUCT_DEFINITION\('design','',\s*" + formation + rb"\s*,").group(1)


lower = product_definition(b"Lower BoxTurtle - 80")
door = product_definition(b"Stock left-swing enclosure door")
occurrence = one(rb"^(#\d+)\s*=\s*NEXT_ASSEMBLY_USAGE_OCCURRENCE\('([^']*)',\s*'[^']*',\s*'[^']*',\s*" + lower + rb"\s*,\s*" + door + rb"\s*,\s*\$\s*\);")
placement = one(rb"^(#\d+)\s*=\s*PRODUCT_DEFINITION_SHAPE\('Placement','Placement of an item',\s*" + occurrence.group(1) + rb"\s*\);").group(1)
context = one(rb"^#\d+\s*=\s*CONTEXT_DEPENDENT_SHAPE_REPRESENTATION\(\s*(#\d+)\s*,\s*" + placement + rb"\s*\);").group(1)
transform = one(rb"^" + context + rb"\s*=\s*\(\s*REPRESENTATION_RELATIONSHIP\([^;]*?REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION\((#\d+)\)").group(1)
ref, target = one(rb"^" + transform + rb"\s*=\s*ITEM_DEFINED_TRANSFORMATION\('','',\s*(#\d+)\s*,\s*(#\d+)\s*\);").groups()
if ref == target:
    raise ValueError("The export reused the source transform as the destination")
point, direction = one(rb"^" + target + rb"\s*=\s*AXIS2_PLACEMENT_3D\('',\s*(#\d+)\s*,\s*#\d+\s*,\s*(#\d+)\s*\);").groups()
for entity in (target, point, direction):
    if len(re.findall(re.escape(entity)+rb'(?!\d)',body))>3:
        raise ValueError(f"Refusing to modify reused transform record {entity!r}")

theta = math.radians(-45)
c, s = math.cos(theta), math.sin(theta)
x, y = -57, -11.5
shift_x, shift_y = x - c*x + s*y, y - s*x - c*y
edits = [
    (occurrence, occurrence.group(1)+b" = NEXT_ASSEMBLY_USAGE_OCCURRENCE('"+occurrence.group(2)+b"','Lower stock door - 80 deg service pose','',"+lower+b","+door+b",$);"),
    (one(rb"^"+point+rb"\s*=\s*CARTESIAN_POINT\(''[^;]*;"),point+f" = CARTESIAN_POINT('',({shift_x:.12f},{shift_y:.12f},0.));".encode()),
    (one(rb"^"+direction+rb"\s*=\s*DIRECTION\(''[^;]*;"),direction+f" = DIRECTION('',({c:.14f},{s:.14f},0.));".encode()),
]
for match, replacement in sorted(edits,key=lambda item:item[0].start(),reverse=True):
    body=body[:match.start()]+replacement+body[match.end():]
model.write_bytes(body)
