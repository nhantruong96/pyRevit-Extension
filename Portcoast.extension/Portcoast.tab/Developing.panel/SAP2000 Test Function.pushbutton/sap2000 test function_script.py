#! python3
import sys

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Get Revit active UI document
uidoc = __revit__.ActiveUIDocument

# Get Revit current document
doc = uidoc.Document

# Get Revit application
app = __revit__.Application

filterCollector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
framingList = []
for i in filterCollector:
    if not i.IsHidden(doc.ActiveView):
        framingList.append(i)
        print(i)