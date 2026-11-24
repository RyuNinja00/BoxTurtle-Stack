from pathlib import Path
from math import radians
import cadquery as cq
from OCP.Quantity import Quantity_ColorRGBA
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.XCAFDoc import XCAFDoc_ColorGen
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from xcad import *

SOURCE = 'revised/BoxTurtle-V1-Dual-Tier.step'
TARGET = 'audited/BoxTurtle-V1-Dual-Tier.step'
doc, tool, (root,) = open_step(SOURCE)
color = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
print('Loaded current assembly', flush=True)

def rename(label, title):
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(title))
    return label

def loc(x=0,y=0,z=0):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x,y,z))
    return TopLoc_Location(t)

def add(parent, piece, title, where=TopLoc_Location()):
    return rename(tool.AddComponent(parent,piece,where),title)

def group(parent,title,where=TopLoc_Location()):
    definition = rename(tool.NewShape(),title)
    return definition, add(parent,definition,title,where)

def block(dx,dy,dz,x,y,z):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))

def cylinder(radius,height,x,y,z,direction=(0,1,0)):
    return cq.Solid.makeCylinder(radius,height,cq.Vector(x,y,z),cq.Vector(*direction))

def piece(parent,shape,title,rgba):
    assert BRepCheck_Analyzer(shape.wrapped).IsValid(), title
    assert len(shape.Solids()) == 1, (title,len(shape.Solids()))
    definition = rename(tool.AddShape(shape.wrapped,False),title)
    color.SetColor(definition,Quantity_ColorRGBA(*rgba),XCAFDoc_ColorGen)
    add(parent,definition,title)
    return definition

def add_hole_y(shape,x,z,y0,depth,r=1.7):
    return shape.cut(cylinder(r,depth,x,y0,z))

def add_hole_x(shape,y,z,x0,depth,r=2.65):
    return shape.cut(cylinder(r,depth,x0,y,z,(1,0,0)))

def place_on_tiers(parent,definition,title):
    for tier,z in [('Lower',0),('Upper',400)]:
        add(parent,definition,f'{tier} - {title}',loc(z=z))

# The tested service pose opens the lower door from the stock 35 degrees
# to 80 degrees about its measured dowel axis.
lower_instance, lower, _ = next(e for e in children(root) if name(e[1]).startswith('Lower BoxTurtle'))
door_instance, door_definition, door_loc = next(e for e in children(lower) if name(e[0]).startswith('Lower stock door'))
turn = gp_Trsf()
turn.SetRotation(gp_Ax1(gp_Pnt(-57,-11.5,0),gp_Dir(0,0,1)),radians(-45))
tool.RemoveComponent(door_instance)
add(lower,door_definition,'Lower stock door - 80 deg service pose',TopLoc_Location(turn)*door_loc)
rename(lower,'Lower BoxTurtle - 80 deg service pose')
rename(lower_instance,'Lower BoxTurtle - 80 deg service pose')

opts,_ = group(root,'OPTIONS - use visibility to show each group')
groups = []
def option(name):
    definition, instance = group(opts,name)
    groups.append((definition,instance))
    return definition

teal=(.17,.60,.59,1)
green=(.38,.69,.37,1)
orange=(.86,.53,.18,1)
gray=(.43,.47,.52,1)
yellow=(.90,.78,.25,1)
rubber=(.30,.33,.36,1)
steel=(.55,.60,.66,1)

# Each bin has a captive lid; mesh or sieve cloth can sit under the lid
# if the media is smaller than the 1 mm slots.
bins = option('01 - Molecular sieve - front-pull cassettes and rail hangers')
bin_module = rename(tool.NewShape(),'Molecular sieve cassettes - 2 x 0.31 L gross per tier')
width,depth,height = 145,68,38
y0,z0 = 14,286
shell = block(width,depth,height,0,y0,z0).cut(block(141,64,36,2,y0+2,z0+2))
pull = block(35,8,9,55,y0-8,z0+3).cut(block(25,6,10,60,y0-5,z0+2))
shell = shell.fuse(pull).clean()
lid = block(width,depth,1.6,0,y0,z0+height)
lid = lid.fuse(block(140.5,63.5,1,2.25,y0+2.25,z0+height-1)).clean()
for slot in range(12):
    lid = lid.cut(block(128,1,4,8,y0+5+5*slot,z0+height-2))
bin_unit = rename(tool.NewShape(),'Front-pull bin - 145 x 68 x 38 mm')
piece(bin_unit,shell,'Print - sieve cassette with finger pull - 0.31 L gross',teal)
piece(bin_unit,lid,'Print - removable lid - 1 mm slots, optional fine mesh',green)
for layout,xx in [('Left',-27),('Right',182)]:
    add(bin_module,bin_unit,layout+' cassette',loc(x=xx))
    for side,rail_x,foot_x in [('left',xx-4,xx-4),('right',xx+145.45,xx+143.45)]:
        wall=block(3.5,68,7,rail_x,14,283)
        foot=block(5.5,68,3,foot_x,14,283)
        outer=(layout=='Left' and side=='left') or (layout=='Right' and side=='right')
        stop=block(5.5,3,9,foot_x,82,283)
        if outer:
            left_outer=layout=='Left'
            stem_x=-30 if left_outer else rail_x
            stem_w=2.5 if left_outer else 330-rail_x
            stem=block(stem_w,8,61,stem_x,40,284)
            pad=block(4,19,14,-30 if left_outer else 326,34.5,333)
            bar=wall.fuse(foot,stem,pad,stop).clean()
            bar=add_hole_x(bar,44,340,-31 if left_outer else 325,6)
        else:
            hanger=block(3.5,5,61,rail_x,10,284)
            pad=block(15,4,14,rail_x-5.5,10,333)
            bar=wall.fuse(foot,hanger,pad,stop).clean()
            bar=add_hole_y(bar,rail_x+1.75,340,9,8,2.65).clean()
        piece(bin_module,bar,f'{layout} cassette - {side} slide rail and rear stop - M5 T-nut',gray)
place_on_tiers(bins,bin_module,'two front-access sieve cassettes')

# Use the bezel as the locating feature; no vendor cutout diameter is assumed.
meters = option('02 - Hygrometers - 45 mm bezel cradles behind the clear doors')
meter_group = rename(tool.NewShape(),'Hygrometer cradle and sample meter')
ring = cylinder(26,4,150,2,297).cut(cylinder(22.8,4,150,2,297))
# Slide the meter in from the rear, against three front stop tabs. The
# bottom tray supports the case and the back remains open for the sensor.
stop_left=block(4,1.4,6,124,2,294)
stop_right=block(4,1.4,6,172,2,294)
stop_bottom=block(8,1.4,4,146,2,271)
tray=block(18,17,3,141,3,271)
arm=block(12,5,20,144,6,319)
pad=block(22,4,15,139,10,332.5)
cradle=ring.fuse(stop_left,stop_right,stop_bottom,tray,arm,pad).clean()
# The arm sits against the pad and rear of the ring.
web=block(12,3,14,144,4,320)
cradle=cradle.fuse(web).clean()
for screw_x in (125,175):
    post=block(4,16,8,screw_x-2,4,293)
    cradle=cradle.fuse(post)
    cradle=add_hole_y(cradle,screw_x,297,15,7,1.05)
cradle=cradle.cut(block(26,6,23,137,4,330))
cradle=add_hole_y(cradle,150,340,8,8,2.65)
keeper=cylinder(27,3,150,20,297).cut(cylinder(18,4,150,19.5,297))
for screw_x in (125,175):
    keeper=add_hole_y(keeper,screw_x,297,19.5,4,1.4)
piece(meter_group,keeper,'Print - vented rear keeper - 2 x M2.5 screws',orange)
piece(meter_group,cradle,'Print - 45.6 mm bezel pocket - M5 rail mount and M2.5 keeper',orange)
meter_body = cylinder(21,14,150,5.45,297)
meter_bezel = cylinder(22.5,2,150,3.45,297)
piece(meter_group,meter_body.fuse(meter_bezel),'Reference - 45 mm bezel x 16 mm depth - verify body and clips',(.23,.24,.25,1))
place_on_tiers(meters,meter_group,'meter readable through front acrylic')

guides = option('03 - Rear PTFE routing - removable four-lane guide combs')
routing = rename(tool.NewShape(),'Four-lane comb and removable cap')
comb=block(316,10,11,-8,283,59)
for x in (15,105,195,285):
    comb=comb.cut(cylinder(2.4,12,x,282,70))
for x in (0,300):
    comb=comb.cut(cylinder(1.7,12,x,288,58,(0,0,1)))
piece(routing,comb,'Print - four 4 mm PTFE channels on 90 mm pitch',teal)
cap=block(316,10,4,-8,283,70)
for x in (15,105,195,285):
    cap=cap.cut(cylinder(2.4,12,x,282,70))
for x in (0,300):
    cap=cap.cut(cylinder(1.7,8,x,288,69,(0,0,1)))
piece(routing,cap,'Print - M3 removable cap - keeps slots accessible',green)
for x in (-15,315):
    arm=block(15,39,6,x-7.5,250,53).fuse(block(15,4,32,x-7.5,250,53))
    arm=add_hole_y(arm,x,80,249,6,2.65)
    side_boss=block(22,10,6,min(x,0) if x<0 else 298,280,53)
    joint_x=0 if x<0 else 300
    arm=arm.fuse(side_boss).cut(cylinder(1.7,10,joint_x,288,52,(0,0,1))).clean()
    piece(routing,arm,'Print - rear rail standoff and threaded-insert tab',gray)
place_on_tiers(guides,routing,'rear clip-on tube guide above buffer outlets')

seals = option('04 - Air sealing - floor seam gasket and removable feedthrough bungs')
sealing = rename(tool.NewShape(),'Fit templates - verify actual floor gaps and fan airflow')
# Narrow stock floor seam templates. The electronics bay stays ventilated.
perim=block(366,224,2,-33,8,89).cut(block(352,210,4,-26,15,88))
piece(sealing,perim,'Cut from closed-cell foam - floor perimeter seam template, trim at hardware',rubber)
plugs,_=group(sealing,'Unused lanes - soft feedthrough plugs')
collars,_=group(sealing,'Active lanes - split collar fit references')
for lane,x in enumerate((15,105,195,285),1):
    bung=cylinder(.95,7,x,249.65,26.12).fuse(cylinder(4.2,2,x,256.65,26.12))
    piece(plugs,bung,f'Lane {lane} - soft plug - 1.9 mm tip for unused 2 mm bore',orange)
    collar=cylinder(4.5,3,x,259,26.12).cut(cylinder(2.1,4,x,258.5,26.12))
    collar=collar.cut(block(4,5,.65,x+1.8,258,25.795))
    piece(collars,collar,f'Lane {lane} - split collar reference - 4 mm PTFE',rubber)
place_on_tiers(seals,sealing,'floor and feedthrough seal templates')

anch = option('05 - Anti-tip anchors - upper rear metal brackets')
for x in (-40,340):
    wall=block(36,3,34,x-18,302,690)
    arm=block(36,55,3,x-18,250,690)
    post_plate=block(18,3,38,x-9,250,690)
    bracket=wall.fuse(arm,post_plate)
    for z in (703,719):
        bracket=add_hole_y(bracket,x,z,249,5,2.75)
    for xx in (x-11,x+11):
        bracket=add_hole_y(bracket,xx,708,301,5,3.2)
    piece(anch,bracket,'Metal anti-tip anchor - M5 extrusion face and wall fasteners to suit structure',steel)

joints = option('06 - Mid-frame gussets and upright drill-location reference')
for x,dr in [(-57,1),(354,-1)]:
    # Stock side roof and base rails end at the rear upright. A flat plate
    # on the outside can tie their adjacent slot faces to the post.
    yy,zz=169,329
    plate=block(3,80,74,x,yy,zz)
    plate=plate.cut(block(4,52,28,x-.5,yy-.1,zz+23))
    for y,z in [(240,370),(190,340),(190,400)]:
        plate=add_hole_x(plate,y,z,x-.5,4.5)
        start=x+3 if dr>0 else x-4
        spacer=cylinder(6,4,start,y,z,(1,0,0)).cut(cylinder(2.65,4.4,start-.2,y,z,(1,0,0)))
        piece(joints,spacer,'Metal 4 mm standoff washer - M5 clearance',steel)
    piece(joints,plate,'Metal side tie plate - 3 x 5.3 mm holes and 4 mm spacers',steel)
    jig=block(8,20,100,x-9 if dr>0 else x+4,230,329)
    for z in (340,400):
        jig=add_hole_x(jig,240,z,x-10 if dr>0 else x+3,12,2.5)
    # An alternate index at the upper base rail can be modeled without
    # changing the original undrilled extrusion.
    piece(joints,jig,'Transfer template - roof and upper base centers, locate on actual rail slots',yellow)

dryer = option('07 - Lower dryer only - paired bulkheads and gasketed drill template')
for x,title in [(91,'Lower supply'),(209,'Lower return')]:
    body=cylinder(18,16,x,241.5,309).fuse(cylinder(22,4,x,241.5,309))
    body=body.cut(cylinder(14,17,x,241,309))
    for xx in (x-18,x+18):
        body=add_hole_y(body,xx,309,241,6)
    piece(dryer,body.translate(cq.Vector(0,1.4,0)),
          title+' - 28 mm bore concept flange - requires modified rear acrylic',orange)
    gasket=cylinder(21.5,1.4,x,241.5,309).cut(cylinder(14,2,x,241.3,309))
    for xx in (x-18,x+18):
        gasket=add_hole_y(gasket,xx,309,241.2,2,1.7)
    piece(dryer,gasket,title+' - 1.4 mm gasket ring - trim to actual bulkhead',rubber)

# Check the bins and cradles against a pair of modeled spool poses.
# Their width is tested with the lane centers and maximum usable x envelope.
for y,z in [(136,181),(113,182)]:
    test = cylinder(105,340,-20,y,z,(1,0,0))
    for solid,where in [(shell,loc(x=-27)),(shell,loc(x=182)),(cradle,loc())]:
        transform = where.Transformation().TranslationPart()
        moved = solid.translate(cq.Vector(transform.X(),transform.Y(),transform.Z()))
        common = BRepAlgoAPI_Common(test.wrapped,moved.wrapped)
        assert common.IsDone()
        assert abs(cq.Shape.cast(common.Shape()).Volume())<.01, (y,z)
print('Cassette and meter clear both modeled 210 mm spool poses', flush=True)

tool.UpdateAssemblies()
for definition, instance in groups:
    color.SetVisibility(definition,False)
    color.SetVisibility(instance,False)
    # Material-bearing solids get exported with an invisibility assignment
    # even when the receiving CAD reads STEP styling only on leaf shapes.
    assert not color.IsVisible_s(instance)
writer=STEPCAFControl_Writer()
assert writer.Transfer(root)
assert writer.Write(TARGET)==IFSelect_RetDone
print('Wrote seven individually switchable groups', flush=True)
