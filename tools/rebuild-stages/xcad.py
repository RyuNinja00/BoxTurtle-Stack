from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopLoc import TopLoc_Location
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool as ST

def open_step(path):
    doc = TDocStd_Document(TCollection_ExtendedString("assembly"))
    reader = STEPCAFControl_Reader()
    assert reader.ReadFile(path) == IFSelect_RetDone
    assert reader.Transfer(doc)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    roots = TDF_LabelSequence()
    tool.GetFreeShapes(roots)
    return doc, tool, list(roots)

def name(label):
    attr = TDataStd_Name()
    return attr.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), attr) else ''

def children(label):
    seq = TDF_LabelSequence()
    ST.GetComponents_s(label, seq)
    for component in seq:
        definition = TDF_Label()
        assert ST.GetReferredShape_s(component, definition)
        yield component, definition, ST.GetLocation_s(component)

def walk(label, loc=TopLoc_Location(), path=()):
    for comp, definition, placement in children(label):
        current = loc * placement
        branch = (*path, name(comp))
        yield branch, comp, definition, current
        yield from walk(definition, current, branch)

if __name__ == '__main__':
    doc, tool, roots = open_step('bte/CAD/BTE V1.0.step')
    for root in roots:
        print(name(root))
        for path, comp, definition, loc in walk(root):
            t=loc.Transformation()
            v=t.TranslationPart()
            print('/'.join(path), repr(name(definition)), [round(k,3) for k in (v.X(),v.Y(),v.Z())], round(t.Value(1,2),4))
