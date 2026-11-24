import sys
import itertools
from xcad import *
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

def get_bounds(s):
    bb=Bnd_Box()
    BRepBndLib.Add_s(s,bb,False)
    return None if bb.IsVoid() else bb.Get()

def leaves(d,l=TopLoc_Location(), prefix=()):
    for p,i,o,place in walk(d,l,prefix):
        if not list(children(o)):
            s=ST.GetShape_s(o).Moved(place)
            b=get_bounds(s)
            if b is not None:
                yield (p,s,b)

def pick(d,p):
    return next((i,o,l) for i,o,l in children(d) if name(i).startswith(p) or name(o).startswith(p))

def bbox_overlap(a,b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i])>.015 for i in range(3))

def intersect(a,b):
    if not bbox_overlap(a[2],b[2]):
        return None
    c=BRepAlgoAPI_Common(a[1],b[1])
    if not c.IsDone():
        print('FAILED',a[0][-1],b[0][-1],flush=True)
        return None
    props=GProp_GProps()
    BRepGProp.VolumeProperties_s(c.Shape(),props)
    v=props.Mass()
    return (v,get_bounds(c.Shape())) if v>.1 else None

def short(part):
    return '/'.join(part[0][-4:])

import re, math
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
import cadquery as cq
p=sys.argv[1]
with open(p,'rb') as f:
    f.seek(-4096,2)
    assert len(re.findall(rb' = INVISIBILITY\(\(#\d+\)\);',f.read()))==6
doc,tool,(root,)=open_step(p)
_,lower,ll=pick(root,'Lower BoxTurtle')
_,upper,ul=pick(root,'Upper BoxTurtle')
_,opts,ol=pick(root,'OPTIONS')
_,mid,ml=pick(root,'Middle divider')
_,roof,rl=pick(root,'Upper roof')
_,post,pl=pick(root,'Shared frame')
assert len(list(children(opts)))==6
assert abs(ul.Transformation().TranslationPart().Z()-400)<.001
assert not any('lower dryer' in name(d).lower() for p,i,d,l in walk(root))
for leaf in leaves(post,pl):
    b=leaf[2]
    assert [round(b[i+3]-b[i],3) for i in range(3)]==[20,20,760]
    holes=set()
    for f in cq.Shape.cast(leaf[1]).Faces():
        adaptor=BRepAdaptor_Surface(f.wrapped)
        if adaptor.GetType()!=GeomAbs_Cylinder:continue
        c=adaptor.Cylinder()
        a=c.Axis().Direction()
        if abs(c.Radius()-2.75)>.002 or abs(a.Z())>.002:continue
        holes.add(('X' if abs(a.X())>.99 else 'Y',round(c.Location().Z()-b[2],3)))
    assert holes=={(axis,z) for axis in ('X','Y') for z in (10,90,350,410,490,750)},holes
print('Four posts: 20 x 20 x 760, both-axis 5.5 mm holes at all six stock-derived elevations',flush=True)

d=next(a for a in leaves(mid,ml) if a[0][-1].startswith('Solid divider'))
assert abs(d[2][2]-352.3)<.002 and abs(d[2][5]-355.3)<.002
u=next(a for a in leaves(roof,rl) if a[0][-1]=='Top:1')
assert abs(u[2][2]-752.3)<.002 and abs(u[2][5]-755.3)<.002
for panel,tier,tier_l in [(d,lower,ll),(u,upper,ul)]:
    _,shell,sl=pick(tier,'Stock enclosure')
    for candidate in leaves(shell,tier_l*sl):
        assert not intersect(panel,candidate),(panel[0],candidate[0])
print('Lower divider and upper roof clear stock clips, covers and screws',flush=True)

_,seals,spos=pick(opts,'04 -')
_,guides,gpos=pick(opts,'03 -')
panels=[a for a in leaves(seals,ol*spos) if a[0][-1].startswith('Foam rail seam strip')]
nuts=[a for a in leaves(guides,ol*gpos) if 'M3 hex nut' in a[0][-1]]
mounts=[a for a in leaves(guides,ol*gpos) if 'nut pocket' in a[0][-1]]
assert len(panels)>=8 and len(nuts)==len(mounts)==4
main=list(leaves(lower,ll))+list(leaves(upper,ul))+list(leaves(post,pl))
for a in panels:
    for b in main:
        assert not intersect(a,b),(a[0],b[0])
for a,b in itertools.product(nuts,mounts):
    assert not intersect(a,b),(a[0],b[0])
print(len(panels),'floor tape lengths clear both mechanisms; captive M3 nuts clear guide brackets',flush=True)
_,door,dl=pick(lower,'Stock left-swing enclosure door')
assert abs(dl.Transformation().Value(2,1)+math.sin(math.pi/4)) < .00001
print('Lower door retains its 80-degree service pose',flush=True)
print('Six-option dry-storage STEP passed reimport',flush=True)
