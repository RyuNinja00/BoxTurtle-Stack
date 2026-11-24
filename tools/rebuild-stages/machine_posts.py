from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.XCAFDoc import XCAFDoc_Location
spanfile=Path('stock_post_face_spans.txt')
for retry in range(90):
    spans=spanfile.read_text().splitlines()
    if len(spans)==4:
        break
    sleep(1)
assert len(spans)==4
patterns={}
for line in spans:
    pos, pattern=line.split(') ',1)
    cx,cy=[round(v) for v in ast.literal_eval(pos+')')]
    patterns[(cx,cy)]=ast.literal_eval(pattern)
stock_diameter=5.5
locations=(0,80,340,400,480,740)
components=list(children(posts))
source_geometry=[shape(e) for e in components]
for e,original in zip(components,source_geometry):
    b=bbox(original)
    assert abs(b[5]-b[2]-760)<.01
    cx,cy=round((b[0]+b[3])/2),round((b[1]+b[4])/2)
    data=patterns[(cx,cy)]
    print(name(e[0]),'source cross drill spans',data,flush=True)
    new=original
    for (axis,z),spans_here in data.items():
        start=min(a for a,b in spans_here)
        end=max(b for a,b in spans_here)
        for offset in (0,400):
            cutter=(cyl(stock_diameter/2,end-start+.2,start-.1,cy,z+offset,(1,0,0)) if axis=='X'
                    else cyl(stock_diameter/2,end-start+.2,cx,start-.1,z+offset,(0,1,0)))
            new=new.cut(cutter)
    label=name(e[0])
    # The source uses one definition for four instances. Keep a distinct
    # machined part definition until the four stock face patterns agree.
    local=BRepBuilderAPI_Transform(new.wrapped,e[2].Inverted().Transformation(),True).Shape()
    definition=rename(tool.AddShape(local,False),
                      f'{label} - stock 5.5 mm cross drilling')
    assert BRepCheck_Analyzer(new.wrapped).IsValid() and len(new.Solids())==1
    color.SetColor(definition,Quantity_ColorRGBA(.18,.20,.22,1),XCAFDoc_ColorGen)
    tool.RemoveComponent(e[0])
    instance=rename(tool.AddComponent(posts,definition,e[2]),label)
    XCAFDoc_Location.Set_s(instance,e[2])
print('Stock Ø5.5 access pattern applied at', locations,flush=True)
_,joint_group,_=pick(options,'06 -')
for e in children(joint_group):
    if name(e[1]).startswith('Transfer template'):
        g=shape(e)
        starts=bbox(g)
        for z in (340,400):
            g=g.cut(cyl(2.75,10,starts[0]-1,240,z,(1,0,0)))
        replace(e,g,'Reference gauge - 5.5 mm lower roof and upper base hole centers')

# The top roof uses the same clips and gasket stack as the divider. Keep
# the dock parts seated on the stock acrylic while accounting for the
# same 0.70 mm gasket compression.
from OCP.XCAFDoc import XCAFDoc_Location
_,roof,_=pick(root,'Upper roof')
roof_components=list(children(roof))
seats=[e for e in roof_components if 'foam gasket' in (name(e[0])+' '+name(e[1])).lower()]
assert len(seats)==1, [(name(i),name(d)) for i,d,l in roof_components]
seat=seats[0]
if abs(bbox(shape(seat))[5]-352.3)>.01:
    new=shape(seat).intersect(block(500,400,2.3,-100,-40,350))
    replace(seat,new,'Foam gasket - 3 mm stock, 2.3 mm installed thickness')
moved_count=0
for i,d,l in roof_components:
    if not i.IsEqual(seat[0]):
        XCAFDoc_Location.Set_s(i,shift(-.7)*l)
        assert abs(ST.GetLocation_s(i).Transformation().TranslationPart().Z()-l.Transformation().TranslationPart().Z()+.7)<.001
        moved_count+=1
print('Upper roof uses the same compressed gasket; shifted',moved_count,'roof parts',flush=True)
