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

doc,tool,(root,)=open_step(sys.argv[1])
print('STEP OPEN',name(root),flush=True)
stock={}
options={}
for i,d,l in children(root):
    if name(d).startswith('OPTIONS'):
        options={name(oi).split(' - ')[0]:list(leaves(od,ol)) for oi,od,ol in children(d)}
    else:
        stock[name(d)]=list(leaves(d,l,prefix=(name(d),)))

all_stock=list(itertools.chain.from_iterable(stock.values()))
print('BASE LEAVES', {k:len(v) for k,v in stock.items()},flush=True)
for tag,objects in options.items():
    hits=0
    for a in objects:
        for b in all_stock:
            r=intersect(a,b)
            if r:
                hits+=1
                print('OPT',tag,short(a),'<->',short(b),round(r[0],2),tuple(round(w,1) for w in r[1]),flush=True)
    print('OPTION DONE',tag,hits,flush=True)

for ta,tb in itertools.combinations(options,2):
    for a,b in itertools.product(options[ta],options[tb]):
        r=intersect(a,b)
        if r:
            print('CROSS',ta,tb,short(a),'<->',short(b),round(r[0],2),flush=True)
print('CROSS DONE',flush=True)

# The assembly includes two complete vendors' models; check boundaries
# changed by the stacking and the buffer retrofit rather than screw threads.
keys=list(stock)
lower=next(k for k in keys if k.startswith('Lower BoxTurtle'))
upper=next(k for k in keys if k.startswith('Upper BoxTurtle'))
middle=next(k for k in keys if k.startswith('Middle divider'))
for ka,kb in [(lower,upper),(middle,lower),(middle,upper)]:
    for a,b in itertools.product(stock[ka],stock[kb]):
        r=intersect(a,b)
        if r:
            print('STACK',short(a),'<->',short(b),round(r[0],2),flush=True)
for k in (lower,upper):
    mdl=stock[k]
    mod=[part for part in mdl if any('N3MI-DG' in t for t in part[0])]
    rest=[part for part in mdl if not any('N3MI-DG' in t for t in part[0])]
    for a,b in itertools.product(mod,rest):
        r=intersect(a,b)
        if r and r[0]>1:
            print('BUFFER',short(a),'<->',short(b),round(r[0],2),tuple(round(w,1) for w in r[1]),flush=True)
    print('LANES DONE',k,flush=True)
print('COMPLETE',flush=True)
