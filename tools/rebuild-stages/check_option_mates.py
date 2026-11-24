from pathlib import Path
import cadquery as cq
s=Path('audit_revision.py').read_text()
class Tool:
    def NewShape(self): return object()
def move(x=0,y=0,z=0):
    return cq.Vector(x,y,z)
sets={}
scope=dict(cq=cq, steel=None, orange=None, gray=None, rubber=None, teal=None,
           green=None, loc=move, group=lambda *a:(object(),None),option=lambda *a:object(),
           rename=lambda z,*_:z,place_on_tiers=lambda *a:None,tool=Tool())
def piece(parent,shape,title,rgba):
    assert len(shape.Solids())==1,title
    sets.setdefault(parent,[]).append((title,shape))
def add(parent,source,title,shift):
    sets.setdefault(parent,[]).extend((title+': '+n,k.translate(shift)) for n,k in sets[source])
scope.update(piece=piece,add=add)
exec(s[s.index('def block('):s.index('def piece(')]+s[s.index('def add_hole_y('):s.index('def place_on_tiers(')],scope)
exec(s[s.index('bins = option('):s.index('seals = option(')],scope)
for label in ('bin_module','meter_group','routing'):
    parts=sets[scope[label]]
    for i,(n,a) in enumerate(parts):
        for m,b in list(parts.items())[i+1:] if isinstance(parts,dict) else parts[i+1:]:
            overlap=a.intersect(b).Volume()
            assert overlap<.005, (n,m,overlap)
    print(label, 'matched parts', len(parts), 'with zero volumetric overlap')
for name,first in sets[scope['bin_module']]:
    for name2,second in sets[scope['meter_group']]:
        volume=first.intersect(second).Volume()
        if volume >= .001:
            b=first.intersect(second).BoundingBox(); print('Cassette x meter interference:',name,name2,volume, (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax))
            raise AssertionError('Cassette and meter options must clear together')
