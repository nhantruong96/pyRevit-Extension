import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

def get_Elements(doc, Enum):
    filterCollector = FilteredElementCollector(doc).OfCategory(Enum).WhereElementIsNotElementType().ToElements()
    elementList = []
    for i in filterCollector:
        if not i.IsHidden(doc.ActiveView):
            elementList.append(i)
    return elementList