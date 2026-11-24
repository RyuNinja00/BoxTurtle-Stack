import ast
from pathlib import Path
from math import cos, pi
import cadquery as cq
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Quantity import Quantity_ColorRGBA
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.gp import gp_Trsf, gp_Vec
from OCP.XCAFDoc import XCAFDoc_ColorGen
from xcad import *

source='audited/BoxTurtle-V1-Dual-Tier.step'
target='dry-storage/BoxTurtle-V1-Dual-Tier.step'
doc, tool, (root,) = open_step(source)
print('Loaded audited assembly', flush=True)

def rename(label,title):
    TDataStd_Name.Set_s(label,TCollection_ExtendedString(title))
    return label

def pick(parent,prefix):
    return next(e for e in children(parent) if name(e[0]).startswith(prefix) or name(e[1]).startswith(prefix))

def find_leaf(parent,prefix):
    return next((i,d,l) for p,i,d,l in walk(parent) if name(d).startswith(prefix) and not list(children(d)))

def block(dx,dy,dz,x,y,z):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))

def cyl(r,h,x,y,z,axis=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis))

def shape(entry):
    return cq.Shape.cast(ST.GetShape_s(entry[1]).Moved(entry[2]))

def verify_solid(s,title):
    assert len(s.Solids())==1 and BRepCheck_Analyzer(s.wrapped).IsValid(), title

def replace(entry,s,title=None):
    if title and title.startswith("Foam gasket"):
        assert s.Solids() and all(BRepCheck_Analyzer(part.wrapped).IsValid() for part in s.Solids()), title
    else:
        verify_solid(s,title or name(entry[1]))
    tool.SetShape(entry[1],s.wrapped.Moved(entry[2].Inverted()))
    if title:
        rename(entry[0],title)
        rename(entry[1],title)

def add_solid(parent,s,title,rgba):
    verify_solid(s,title)
    definition=rename(tool.AddShape(s.wrapped,False),title)
    color.SetColor(definition,Quantity_ColorRGBA(*rgba),XCAFDoc_ColorGen)
    return rename(tool.AddComponent(parent,definition,TopLoc_Location()),title)

def bbox(s):
    b=Bnd_Box()
    BRepBndLib.Add_s(s.wrapped,b,False)
    return None if b.IsVoid() else b.Get()

def conflicts(a,b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-6 for i in range(3))

def shift(z):
    t=gp_Trsf()
    t.SetTranslation(gp_Vec(0,0,z))
    return TopLoc_Location(t)

_,options,_=pick(root,'OPTIONS')
tool.RemoveComponent(pick(options,'07 - Lower dryer')[0])
_,lower,_=pick(root,'Lower BoxTurtle')
_,mid,_=pick(root,'Middle divider')
_,posts,_=pick(root,'Shared frame')
color=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

# Leave a 0.10 mm nominal gap beneath the stock clip ledges. The closed
# cell 3 mm gasket is shown compressed to a 2.30 mm installed stack.
old_gasket=pick(mid,'Perimeter foam gasket')
gasket_title='Foam gasket - 3 mm stock, 2.3 mm installed thickness'
gasket=shape(old_gasket).intersect(block(500,400,2.3,-100,-40,350))
replace(old_gasket,gasket,gasket_title)
divider=pick(mid,'Solid divider')
replace(divider,shape(divider).translate((0,0,-.7)),'Solid divider - 372 x 232.4 x 3 mm - under stock clips')
print('Middle divider seated below the clip ledges',flush=True)

# Smooth cap/comb/boss holes now end at underside pockets for captive
# standard M3 hex nuts. Cap and guide bolts insert from the top.
_,guides,_=pick(options,'03 -')
for search,x in [('Left',0),('Right',300)]:
    items=[(i,d,l) for p,i,d,l in walk(guides) if 'threaded-insert tab' in name(d)
           and not list(children(d)) and p[0].startswith('Lower')]
    entry=next(e for e in items if (bbox(shape(e))[0]<0)==(x==0))
    pocket=(cq.Workplane('XY',origin=(x,288,52.9))
            .polygon(6,5.7/cos(pi/6)).extrude(2.7).val())
    changed=shape(entry).cut(pocket).clean()
    replace(entry,changed,f'Print - {search} rear standoff - captive M3 nut pocket 5.7 AF')
    nut=(cq.Workplane('XY',origin=(x,288,53.1))
         .polygon(6,5.5/cos(pi/6)).extrude(2.4).val()
         .cut(cyl(1.5,3,x,288,53)))
    # Each tier references the same guide assembly.
    guide_body=pick(guides,'Lower')[1]
    add_solid(guide_body,nut,f'Hardware reference - {search} M3 hex nut, 5.5 AF x 2.4',(.56,.60,.64,1))
print('PTFE supports now carry two captive M3 nuts per tier',flush=True)

# Replace the interfering one-piece template by strips on the top rail
# lands. Split strips at keep-out zones of installed components.
_,seals,_=pick(options,'04 -')
_,seal_body,_=pick(seals,'Lower')
old=pick(seal_body,'Cut from closed-cell foam')
tool.RemoveComponent(old[0])
stock=[]
for path,i,d,l in walk(lower):
    if list(children(d)): continue
    s=shape((i,d,l))
    b=bbox(s)
    if b is not None and b[2]<91.2 and b[5]>89.9:
        stock.append((path[-1],s,b))
for label,axis,s in [
    ('Front',0,block(359.6,4,1,-29.8,5.8,90)),
    ('Rear',0,block(359.6,4,1,-29.8,230.2,90)),
    ('Left',1,block(4,219.6,1,-34.2,10.2,90)),
    ('Right',1,block(4,219.6,1,330.2,10.2,90)),
]:
    box=bbox(s)
    exclusion=[]
    for title,solid,b in stock:
        if not conflicts(box,b): continue
        common=s.intersect(solid)
        if common.Volume()>.02:
            cut=bbox(common)
            exclusion.append((cut[axis]-.5, cut[axis+3]+.5))
    # Use full-width interrupted lengths to keep the installation simple.
    for start,end in sorted(exclusion):
        tool_shape=(block(end-start,9,3,start,box[1]-1,89) if axis==0
                    else block(9,end-start,3,box[0]-1,start,89))
        s=s.cut(tool_shape)
    segments=sorted([seg for seg in s.Solids() if seg.Volume()>=10],key=lambda seg:bbox(seg)[axis])
    assert segments,label
    for index,segment in enumerate(segments,1):
        for title,solid,b in stock:
            if conflicts(bbox(segment),b):
                assert segment.intersect(solid).Volume()<.02,(label,title)
        b=bbox(segment)
        length=round(b[axis+3]-b[axis],1)
        title=f'Foam rail seam strip - {label} {index} - {length:g} x 4 x 1 mm'
        add_solid(seal_body,segment,title,(.30,.33,.36,1))
        print(title,flush=True)

# Read feature centers measured from the actual stock upright STEP, and
# repeat that pattern at the upper-tier offset.
from time import sleep
holefile=Path('stock_posts_holes.txt')
for i in range(90):
    data=holefile.read_text().splitlines()
    if len(data)>=4:
        break
    sleep(1)
assert len(data)==4, data
print('Stock source hole data',data,flush=True)
# Hole instructions are generated separately from the source CAD scan.
exec(Path('machine_posts.py').read_text())

tool.UpdateAssemblies()
remaining=list(children(options))
assert [name(d)[:2] for i,d,l in remaining]==[f'{n:02}' for n in range(1,7)]
writer=STEPCAFControl_Writer()
assert writer.Transfer(root)
assert writer.Write(target)==IFSelect_RetDone
print('Wrote the six-option dry-storage assembly',flush=True)
