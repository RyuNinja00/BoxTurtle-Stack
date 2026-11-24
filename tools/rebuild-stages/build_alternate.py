import math
import re
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Quantity import Quantity_ColorRGBA
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_DocumentTool
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from xcad import *

SOURCE = 'bte/CAD/BTE V1.0.step'
PITCH = 400
POST_HEIGHT = 360 + PITCH

def rename(label, title):
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(title))
    return label

def shift(x=0, y=0, z=0):
    transform = gp_Trsf()
    transform.SetTranslation(gp_Vec(x, y, z))
    return TopLoc_Location(transform)

def simple_bounds(shape):
    box = cq.Shape.cast(shape).BoundingBox()
    return tuple(round(n, 2) for n in (box.xmin, box.ymin, box.zmin, box.xmax, box.ymax, box.zmax))

doc, tool, roots = open_step(SOURCE)
assert len(roots) == 1
print('Official assembly loaded', flush=True)
source = roots[0]
color = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
entries = list(walk(source))

def get(predicate):
    hits = [entry for entry in entries if predicate(entry[0])]
    assert len(hits) == 1, [p for p, *_ in hits]
    return hits[0]

def by_last(value):
    return get(lambda p: p[-1] == value)

def group(title):
    return rename(tool.NewShape(), title)

def add(parent, definition, placement=TopLoc_Location(), title=None):
    return rename(tool.AddComponent(parent, definition, placement), title or name(definition))

def add_from(parent, entry, title=None, offset=TopLoc_Location()):
    _, instance, definition, placement = entry
    add(parent, definition, offset * placement, title or name(instance))

def solid(parent, shape, title, rgba):
    assert BRepCheck_Analyzer(shape).IsValid(), title
    definition = rename(tool.AddShape(shape, False), title)
    color.SetColor(definition, Quantity_ColorRGBA(*rgba), XCAFDoc_ColorGen)
    add(parent, definition, title=title)
    return definition

def shape_at(entry):
    return ST.GetShape_s(entry[2]).Moved(entry[3])

root = group('Stacked BoxTurtle V1')
posts = group('Shared frame - four 760 mm uprights')
add(root, posts)

# Sweep the actual stock profile through the entire proposed upright length.
post_entry = get(lambda p: len(p)>1 and p[-2].startswith('step_3_upright_1') and p[-1] == '360mm 2020 (1):1')
post_source = shape_at(post_entry)
post_section_z = 170
section = BRepAlgoAPI_Section(post_source, gp_Pln(gp_Pnt(0, 0, post_section_z), gp_Dir(0, 0, 1)))
section.Build()
assert section.IsDone()
wires = cq.Wire.combine(cq.Shape.cast(section.Shape()).Edges())
wires.sort(key=lambda wire: cq.Face.makeFromWires(wire).Area(), reverse=True)
post = cq.Solid.extrudeLinear(wires[0], wires[1:], cq.Vector(0, 0, POST_HEIGHT))
post = post.translate(cq.Vector(-340, -240, -post_section_z))
assert math.isclose(post.BoundingBox().zlen, POST_HEIGHT, abs_tol=0.01)
post_label = rename(tool.AddShape(post.wrapped, False), '2020 extrusion - 760 mm')
color.SetColor(post_label, Quantity_ColorRGBA(.18, .20, .22, 1.0), XCAFDoc_ColorGen)
for x, y, title in [
    (-40, 0, 'Front left'), (340, 0, 'Front right'),
    (-40, 240, 'Rear left'), (340, 240, 'Rear right')
]:
    add(posts, post_label, shift(x, y, -10), title + ' - 760 mm')

shell = group('Stock enclosure hardware and roof rails')
base = group('BoxTurtle V1 - original frame and four lanes')
full = by_last('Full_Simple v1:1')
bt_entry = next(e for e in entries if e[0][-2:] == ('Full_Simple v1:1', 'BT_Simple v2:1'))
bt_prefix = bt_entry[0]

# The enclosure replaces the stock corners and the front skirt. The official
# enclosed base already positions all lanes, drive components and electronics.
for entry in entries:
    path = entry[0]
    if path[:len(bt_prefix)] == bt_prefix and len(path) == len(bt_prefix) + 1:
        if path[-1].startswith(('Corners:', 'Skirts:')):
            for piece in entries:
                part_path = piece[0]
                if part_path[:-1] == path and part_path[-1].startswith(('Sides:', 'Rear:')):
                    add_from(base, piece)
            continue
        add_from(base, entry)

# Pick up inlet parts and any other siblings of the stock mechanism.
for entry in entries:
    path = entry[0]
    if path[:-1] == full[0][:-1] and path != full[0]:
        add_from(base, entry)

panels = group('Stock side and rear acrylic')
panel_parent = by_last('panels v1:4')
panel_solids = []
for entry in entries:
    p = entry[0]
    if p[:len(panel_parent[0])] != panel_parent[0] or list(children(entry[2])):
        continue
    for shape in cq.Shape.cast(shape_at(entry)).Solids():
        panel_solids.append((shape, simple_bounds(shape.wrapped)))
print('Stock glazing solids:', [bounds for _, bounds in panel_solids], flush=True)
left = [shape for shape, b in panel_solids if b[3] < 0 and abs(b[4]-b[1]-232) < .02]
right = [shape for shape, b in panel_solids if b[0] > 300 and abs(b[4]-b[1]-232) < .02]
rear = [shape for shape, b in panel_solids if abs(b[3]-b[0]-371) < .02 and 235 < b[1] < 242]
assert len(left) == len(rear) == 1
assert len(right) <= 1
for shape, title in [
    (left[0], 'Left side acrylic - 232 x 252.4 mm'),
    (right[0] if right else left[0].translate(cq.Vector(380, 0, 0)), 'Right side acrylic - 232 x 252.4 mm'),
    (rear[0], 'Rear acrylic - 371 x 251.4 mm')
]:
    solid(panels, shape.wrapped, title, (.48,.67,.76,.27))

def copy_pruned(parent, entry, omit):
    path, inst, definition, placement = entry
    if omit(path[-1]):
        return
    items = list(children(definition))
    if not items:
        add_from(parent, entry)
        return
    branch = group(name(definition))
    for component, part, part_loc in items:
        copy_pruned(branch, ((name(component),), component, part, part_loc), omit)
    if list(children(branch)):
        add(parent, branch, placement, name(inst))

def stationary_trim_omit(label):
    return label.lower().startswith((
        'arrow', 'upper_hinge_door', 'lower_hinge_door',
        'lower_hinge_left_door', 'upper_cover_door'
    ))

step_nodes = (
    'step_7_top_extrusions', 'step_8_seals', 'step_1_roll_nuts',
    'step_2_skirt', 'step_3_lower_front_covers', 'step_4_rear_covers',
    'step_6_panel_clip_hardware', 'step_6_door_prep', 'step_8_screw_covers'
)
for entry in entries:
    path = entry[0]
    if path[0].startswith('step_9') and len(path)>1 and path[-2].lower().startswith(step_nodes):
        if not path[-1].lower().startswith('step_'):
            copy_pruned(shell, entry, stationary_trim_omit)

# The moving door in the source is already open. Align its moving hinge
# with the same hinge in the assembly preparation view for the closed tier.
door = group('Stock left-swing enclosure door')
door_root = by_last('step_10_door_7 v3:1')
open_hinge = get(lambda p: p[:1] == door_root[0] and p[-1] == 'upper_hinge_door_left:1')
closed_hinge = get(lambda p: p[0].startswith('step_9') and p[-1] == 'upper_hinge_door_left:1')
close_door = closed_hinge[3] * open_hinge[3].Inverted()
for entry in entries:
    if entry[0][:-1] == door_root[0]:
        copy_pruned(door, entry, lambda label: label.lower().startswith('arrow'))

lower = group('Lower BoxTurtle - door open')
upper = group('Upper BoxTurtle - door closed')
for tier in (lower, upper):
    add(tier, base)
    add(tier, shell)
    add(tier, panels)
add(lower, door, title='Lower stock door - open 35 degrees')
add(upper, door, close_door, 'Upper stock door - closed')
add(root, lower)
add(root, upper, shift(z=PITCH))

gasket = get(lambda p: any(c.startswith('step_13_top_2') for c in p) and p[-1] == 'foam seal:1')
divider = group('Middle divider - solid acrylic and gasket')
add(root, divider)
add_from(divider, gasket, 'Perimeter foam gasket')
divider_shape = (cq.Workplane('XY', origin=(148.99,120.2,353))
                 .rect(372,232.4).extrude(3).edges('|Z').fillet(1).val())
solid(divider, divider_shape.wrapped, 'Solid divider - 372 x 232.4 x 3 mm', (.30,.56,.70,.48))

roof = group('Upper roof - stock panel and PolyDryer')
add(root, roof, shift(z=PITCH))
add_from(roof, by_last('New_Top_Panel v10:1'), 'Stock upper roof panel and dock hardware')
add_from(roof, gasket, 'Perimeter foam gasket')
for entry in entries:
    path = entry[0]
    if (len(path) == 1 and path[0].startswith(('Lid', 'PolyDryer_Dummy'))) or (path[0].startswith('step_9') and len(path)==2 and path[-1].startswith('=>')):
        add_from(roof, entry, 'PolyDryer outline' if path[0].startswith('PolyDryer') else None)

print('New assemblies built', flush=True)
tool.UpdateAssemblies()
print('New assemblies updated', flush=True)
for title, label in [('base',base),('shell',shell),('door',door),('roof',roof),('stack',root)]:
    shape=ST.GetShape_s(label)
    print(title, len(list(walk(label))), flush=True)

writer = STEPCAFControl_Writer()
assert writer.Transfer(root)
assert writer.Write('stack_alternate.step') == IFSelect_RetDone
