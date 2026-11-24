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

from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from collections import defaultdict
doc,tool,(r,)=open_step('bte/CAD/BTE V1.0.step')
for p,i,d,l in walk(r):
 if p[-1]=='360mm 2020 (1):1' and p[0].startswith('step_9'):
  s=cq.Shape.cast(ST.GetShape_s(d).Moved(l))
  box=Bnd_Box(); BRepBndLib.Add_s(s.wrapped,box,False)
  bounds=box.Get()
  cx,cy=[round((a+b)/2,4) for a,b in zip(bounds[:2],bounds[3:5])]
  faces=defaultdict(list)
  for f in s.Faces():
   surf=BRepAdaptor_Surface(f.wrapped)
   if surf.GetType()!=GeomAbs_Cylinder:continue
   cyl=surf.Cylinder()
   d=cyl.Axis().Direction()
   axis='X' if abs(d.X())>.999 else 'Y' if abs(d.Y())>.999 else None
   if axis is None or abs(cyl.Radius()-2.75)>.001:continue
   box=Bnd_Box(); BRepBndLib.Add_s(f.wrapped,box,False)
   b=box.Get()
   c=cyl.Location()
   j='XY'.index(axis)
   faces[(axis,round(c.Z(),3))].append((round(b[j],4),round(b[3+j],4)))
  print((cx,cy),dict(sorted(faces.items())),flush=True)
