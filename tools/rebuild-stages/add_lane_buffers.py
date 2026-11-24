from math import pi
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.Quantity import Quantity_ColorRGBA
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_ColorCurv
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from xcad import *

original = 'BoxTurtle-V1-Dual-Tier.step'
accessory = 'lane-buffer/STEP/Lane Buffer.step'
target = 'revised/BoxTurtle-V1-Dual-Tier.step'

def rename(label, title):
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(title))
    return label

def shift(x=0, y=0, z=0):
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(x,y,z))
    return TopLoc_Location(tr)

def pick(parent, prefix):
    matches = [entry for entry in children(parent) if name(entry[0]).startswith(prefix) or name(entry[1]).startswith(prefix)]
    assert len(matches) == 1, (prefix, [name(entry[0]) for entry in matches])
    return matches[0]

def bound(shape):
    box = Bnd_Box()
    BRepBndLib.Add_s(shape,box,False)
    return tuple(round(v,3) for v in box.Get())

doc, tool, (root,) = open_step(original)
print('Loaded existing stacked CAD', flush=True)
mod_doc, _, (mod_root,) = open_step(accessory)
print('Loaded Lane Buffer CAD', flush=True)
mod_color = XCAFDoc_DocumentTool.ColorTool_s(mod_doc.Main())
dest_color = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

def add(parent, definition, loc, title):
    return rename(tool.AddComponent(parent, definition, loc), title)

def group(title):
    return rename(tool.NewShape(), title)

cache = {}
def clone(definition):
    key = definition.Tag()
    if key in cache:
        return cache[key]
    parts = list(children(definition))
    if parts:
        result = group(name(definition))
        for occurrence, item, loc in parts:
            add(result, clone(item), loc, name(occurrence))
    else:
        result = rename(tool.AddShape(ST.GetShape_s(definition), False), name(definition))
        for kind in (XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_ColorCurv):
            rgba = Quantity_ColorRGBA()
            if mod_color.GetColor_s(definition, kind, rgba):
                dest_color.SetColor(result, rgba, kind)
    cache[key] = result
    return result

_, lower, lower_position = pick(root, 'Lower BoxTurtle')
_, upper, upper_position = pick(root, 'Upper BoxTurtle')
_, lower_base, _ = pick(lower, 'BoxTurtle V1 - original')
_, upper_base, _ = pick(upper, 'BoxTurtle V1 - original')
assert lower_base.Tag() == upper_base.Tag()
assert round(upper_position.Transformation().TranslationPart().Z() - lower_position.Transformation().TranslationPart().Z(),4) == 400

old_rear_instance, old_rear, old_rear_loc = pick(lower_base, 'Rear:')
_, old_hw, old_hw_loc = pick(old_rear, 'Hardware (1)')
extras = [(i,d,old_rear_loc*old_hw_loc*l) for i,d,l in children(old_hw)
          if (name(i).startswith(('3010 DC Axial Fan', 'M3x16 BHCS')) or name(d).startswith(('3010 DC Axial Fan', 'M3x16 BHCS')))]
assert len(extras) == 5
tool.RemoveComponent(old_rear_instance)
module = group('N3MI-DG - four lane buffers and rear skirts')
add(lower_base, module, TopLoc_Location(), 'N3MI-DG - four lane buffers and rear skirts')

# Project CAD places the skirt on its local Y=0 rail. The BoxTurtle's
# rear rail runs across X at Y=240, facing in the opposite direction.
spin = gp_Trsf()
spin.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),pi)
rear_mount = shift(300,240) * TopLoc_Location(spin)
_, mod_skirts, skirt_loc = pick(mod_root, 'Rear Skirts')
assert len(list(children(mod_skirts))) == 3
add(module, clone(mod_skirts), rear_mount * skirt_loc, 'Rear skirt - end, center and power')

_, mod_buffer, buffer_loc = pick(mod_root, 'Lane_Buffer')
buffer = clone(mod_buffer)
for lane in range(1,5):
    loc = rear_mount * shift(x=90*(4-lane)) * buffer_loc
    add(module, buffer, loc, f'Lane {lane} buffer')
    print('Lane', lane, 'envelope', bound(ST.GetShape_s(mod_buffer).Moved(loc)), flush=True)

fan = group('Original rear fan and fasteners')
for i,d,l in extras:
    add(fan, d, l, name(i))
add(module, fan, TopLoc_Location(), 'Original rear fan and fasteners')
tool.UpdateAssemblies()

for tier in (lower,upper):
    _, base, _ = pick(tier,'BoxTurtle V1 - original')
    _, mod, _ = pick(base,'N3MI-DG')
    assert len([n for n,_,_ in children(mod) if name(n).startswith('Lane ')]) == 4
    assert not any(name(n).startswith('Rear:') for n,_,_ in children(base))
print('Both tiers have four buffers and a replacement skirt', flush=True)

writer = STEPCAFControl_Writer()
assert writer.Transfer(root)
assert writer.Write(target) == IFSelect_RetDone
