import math,sys
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from xcad import *

def cylinders(s):
    info=set()
    for face in cq.Shape.cast(s).Faces():
        surf=BRepAdaptor_Surface(face.wrapped)
        if surf.GetType()!=GeomAbs_Cylinder: continue
        cyl=surf.Cylinder()
        o=cyl.Location()
        ax=cyl.Axis().Direction()
        direction=tuple(round(abs(i),6) for i in (ax.X(),ax.Y(),ax.Z()))
        if max(direction)<.9999: continue
        coord=tuple(round(n,3) for n,flag in zip((o.X(),o.Y(),o.Z()),direction) if flag<.5)
        info.add(('XYZ'[direction.index(max(direction))], round(cyl.Radius()*2,3),coord))
    return sorted(info)

doc,tool,(root,)=open_step(sys.argv[1])
target=['rail and rear stop','bezel pocket','rear keeper','retains','rear rail standoff','removable cap','channels on 90','tie plate','standoff washer','Transfer template','anti-tip anchor','concept flange','1.4 mm gasket ring']
for path,i,d,l in walk(root):
    if list(children(d)):
        continue
    n=name(d)
    if not any(t in n for t in target):
        continue
    if any(p.startswith('Upper -') for p in path):
        continue
    s=ST.GetShape_s(d).Moved(l)
    print(n, cylinders(s), flush=True)
print('COMPLETE',flush=True)
