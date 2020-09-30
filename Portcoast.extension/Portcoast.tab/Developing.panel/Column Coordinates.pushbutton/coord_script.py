try:
    import os
    import math
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

    # Define Function
    
    def feet_to_mm(x):
        """
        Convert feet to milimeters"""
        return x*304.8
    
    # Get All Selected ElementIDs
    selected_ElementIDs = uidoc.Selection.GetElementIds()
    
    # Get All Selected Elements
    selected_Elements = map(lambda x: doc.GetElement(x), selected_ElementIDs)
    
    # Filter to get Structural Columns
    piles_list = list(filter(lambda x: x.Category.Name == "Structural Columns", selected_Elements))
    points_list = []
    angle_list = []
    for i in piles_list:
        location_point = i.Location.Point
        
        # Points List
        points_list.append(location_point)
        
        # Angles List
        y = location_point.Y
        angle = i.Location.Point.AngleTo(XYZ(1,0,0))
        if y>0:
            angle_list.append(angle)
        else:
            angle_list.append(2*math.pi-angle)
    
    # Get Project Base Point
    project_base_point = FilteredElementCollector(doc).OfCategory(OST_ProjectBasePoint).ToElements()[0]
    y0 = project_base_point.GetParameters("N/S")[0].AsDouble()
    x0 = project_base_point.GetParameters("E/W")[0].AsDouble()
    a0 = project_base_point.GetParameters("Angle to True North")[0].AsDouble()

    # Get Lengths
    lengths = map(lambda x: x.GetLength(), points_list)

    # New Angles List
    new_angles_list = map(lambda a1 : a1 - a0 +(a0//math.pi)*2*math.pi, angle_list)

    # New Coords
    x_list = []
    y_list = []
    for i in range(len(points_list)):
        x = (lengths[i] * math.cos(new_angles_list[i]) + x0)
        y = (lengths[i] * math.sin(new_angles_list[i]) + y0)
        x_list.append(x)
        y_list.append(y)
    # New Definitions
 
    x_defi_options = ExternalDefinitionCreationOptions("X", ParameterType.Length)
    x_defi_options.UserModifiable = False
 
    y_defi_options = ExternalDefinitionCreationOptions("Y", ParameterType.Length)
    y_defi_options.UserModifiable = False
            
#    x_defi = Definitions()
#    x_defi.Create(x_defi_options)
    DefinitionFile = os.getcwd() + "\SharedParameterFile.txt"
    definition_File = app.OpenSharedParameterFile()
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
    
    x_param_list = map(lambda e: e.LookupParameter("X"), piles_list)
    y_param_list = map(lambda e: e.LookupParameter("Y"), piles_list)
    
    trans = Transaction(doc, "Set X Value")
    trans.Start()
    for px, py, x, y in zip(x_param_list, y_param_list, x_list, y_list):
        px.Set(x)
        py.Set(y)
    trans.Commit()
        
    
    
except Exception as error:
    TaskDialog.Show("Error",str(error))