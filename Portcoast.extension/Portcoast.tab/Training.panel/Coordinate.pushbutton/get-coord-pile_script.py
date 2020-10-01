# -*- coding: utf-8 -*-

__title__ = "Piles Coordinate"

# Import library

import clr #common language runtime
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import Selection

import pyrevit

# Get target

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

app = __revit__.Application

# colection

selectedItems = uidoc.Selection.GetElementIds()

elements = map(lambda x: doc.GetElement(x), selectedItems)

param_name = "Comments"

params = map(lambda x: x.GetParameters(param_name), elements)
new_value = "abc xyz"
# Transaction

trans = Transaction(doc)
trans.Start("Set Comment")
for param in params:
    param[0].Set(new_value)
trans.Commit()
