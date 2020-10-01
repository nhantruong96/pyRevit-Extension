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
    x_pile_local_list = []
    y_pile_local_list = []
    for i in piles_list:
        location = i.Location
        location_point = i.Location.Point
        
        # Points List
        points_list.append(location_point)
        
        # Angles List
        y = location_point.Y
        y_pile_local_list.append(y)
        x = location_point.X
        x = x_pile_local_list.append(x)
        angle = i.Location.Point.AngleTo(XYZ(1,0,0))
        if y>0:
            angle_list.append(angle)
        else:
            angle_list.append(2*math.pi-angle)
    
    # Get Project Base Point
    project_base_point = FilteredElementCollector(doc).OfCategory(OST_ProjectBasePoint).ToElements()[0]
    a0 = -1*project_base_point.GetParameters("Angle to True North")[0].AsDouble()
    
    shared_base_point = FilteredElementCollector(doc).OfCategory(OST_SharedBasePoint).ToElements()[0]
    y_survey_global = shared_base_point.GetParameters("N/S")[0].AsDouble()
    x_survey_global = shared_base_point.GetParameters("E/W")[0].AsDouble()
    vec_survey_global = XYZ(x_survey_global, y_survey_global, 0)
    survey_vec = shared_base_point.Position
    survey_vec_negate = survey_vec.Negate()
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
        x = x_pile_local_list[i] + (x_survey_local_negate + x_survey_global)
        y = y_pile_local_list[i] + (y_survey_local_negate + y_survey_global)
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
    
    location_pile_local = []
    for i in piles_list:
        
        vec_survey_to_pile = i.Location.Point.Add(survey_vec_negate)
        rotated_vec_survey_to_pile = XYZ(vec_survey_to_pile.X * math.cos(a0)-vec_survey_to_pile.Y * math.sin(a0), vec_survey_to_pile.X * math.sin(a0) + vec_survey_to_pile.Y * math.cos(a0), 0)
        vec = rotated_vec_survey_to_pile.Add(vec_survey_global)
        print(vec.Multiply(304.8))
except Exception as error:
    TaskDialog.Show("Error",str(error))