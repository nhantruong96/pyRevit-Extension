__title__ = "Add Parameters"

import os
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

dir_path = os.path.dirname(os.path.realpath(__file__))
app.SharedParametersFilename = dir_path + "\SharedParameterFile.txt"
definition_File = app.OpenSharedParameterFile()
if definition_File:
    groups = definition_File.Groups
    definitions = map(lambda x: x.Definitions, groups)

    # Create Category Set and Insert Category of Structural Columns to it
    categories = app.Create.NewCategorySet()
    category = doc.Settings.Categories.get_Item(BuiltInCategory.OST_StructuralColumns)
    categories.Insert(category)
    instanceBinding = app.Create.NewInstanceBinding(categories)
    bindingMap = doc.ParameterBindings

    trans = Transaction(doc, "Binding Parameters to Categories")
    trans.Start()
    for defis in definitions:
        for d in defis:
            bindingMap.Insert(d,instanceBinding, BuiltInParameterGroup.PG_DATA)
    trans.Commit()
else:
    print("Can't open shared parameter file")
    