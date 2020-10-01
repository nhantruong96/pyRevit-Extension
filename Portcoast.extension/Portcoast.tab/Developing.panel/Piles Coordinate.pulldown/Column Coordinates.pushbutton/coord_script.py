__title__ = "Add Coordinate Values"

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
    
    selected_ElementIDs = uidoc.Selection.GetElementIds()
    selected_Elements = map(lambda x: doc.GetElement(x), selected_ElementIDs)
    
    # Filter to get Structural Columns
    piles_list = list(filter(lambda x: x.Category.Name == "Structural Columns", selected_Elements))
    points_list = []
    angle_list = []
    for i in piles_list:
        location = i.Location
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
    a0 = project_base_point.GetParameters("Angle to True North")[0].AsDouble()
    
    shared_base_point = FilteredElementCollector(doc).OfCategory(OST_SharedBasePoint).ToElements()[0]
    y_survey_global = shared_base_point.GetParameters("N/S")[0].AsDouble()
    x_survey_global = shared_base_point.GetParameters("E/W")[0].AsDouble()
    survey_vec_negate = shared_base_point.Position.Negate()
    y_survey_local_negate = survey_vec_negate.Y
    x_survey_local_negate = survey_vec_negate.X
    
    # Get Lengths
    lengths = map(lambda x: x.GetLength(), points_list)

    # New Angles List
    new_angles_list = map(lambda a1 : a1 - a0 +(a0//math.pi)*2*math.pi, angle_list)

    # New Coords
    x_list = []
    y_list = []
    for i in range(len(points_list)):
        x = lengths[i] * math.cos(new_angles_list[i]) + (x_survey_local_negate + x_survey_global)
        y = lengths[i] * math.sin(new_angles_list[i]) + (y_survey_local_negate + y_survey_global)
        x_list.append(x)
        y_list.append(y)
        
    x_param_list = map(lambda e: e.LookupParameter("X"), piles_list)
    y_param_list = map(lambda e: e.LookupParameter("Y"), piles_list)
    
    trans = Transaction(doc, "Set X Value")
    trans.Start()
    for px, py, x, y in zip(x_param_list, y_param_list, x_list, y_list):
        pxOk = px.Set(x)
        pxOk = py.Set(y)
    trans.Commit()
except Exception as error:
    TaskDialog.Show("Error",str(error))