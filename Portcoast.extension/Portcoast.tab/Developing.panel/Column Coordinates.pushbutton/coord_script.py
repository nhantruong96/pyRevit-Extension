import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.BuiltInCategory import *
from Autodesk.Revit.UI import *

import pyrevit
from pyrevit import DB, UI

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

selection = uidoc.Selection

selectedIDs = selection.GetElementIds()



print(selectedIDs)