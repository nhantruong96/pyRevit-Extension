__title__ = "Add Coordinate Values"

try:
    import System
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
    
    selected_Elements = map(lambda x: doc.GetElement(x), uidoc.Selection.GetElementIds())
    
    # Filter to get Structural Columns
    piles_list = list(filter(lambda x: x.Category.Name == "Structural Columns", selected_Elements))
    
    # Get Project Base Point
    project_base_point = FilteredElementCollector(doc).OfCategory(OST_ProjectBasePoint).ToElements()[0]
    a0 = -1*project_base_point.GetParameters("Angle to True North")[0].AsDouble()
    
    shared_base_point = FilteredElementCollector(doc).OfCategory(OST_SharedBasePoint).ToElements()[0]
    y_survey_global = shared_base_point.GetParameters("N/S")[0].AsDouble()
    x_survey_global = shared_base_point.GetParameters("E/W")[0].AsDouble()
    vec_survey_global = XYZ(x_survey_global, y_survey_global, 0)
    survey_vec_negate = shared_base_point.Position.Negate()

    # New Coords
    vec_pile_local = []
    for i in piles_list:
        location = i.Location
        if type(location) == LocationCurve:
            if location.Curve.Direction.Z > 0:
                vec_pile_local.append(location.Curve.GetEndPoint(1))
            if location.Curve.Direction.Z < 0:
                vec_pile_local.append(location.Curve.GetEndPoint(0))
        elif type(location) == LocationPoint:
            top_level = i.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).AsDouble() + i.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).AsDouble()
            point = location.Point
            vec_pile_local.append(location.Point.Add(XYZ(0,0,top_level)))

    vec_pile_global = []
    for i in vec_pile_local:
        vec_StoP = i.Add(survey_vec_negate)
        x_StoP = vec_StoP.X
        y_StoP = vec_StoP.Y
        rotated_vec_StoP = XYZ(x_StoP * math.cos(a0) - y_StoP * math.sin(a0), x_StoP * math.sin(a0) + y_StoP * math.cos(a0), 0)
        vec = rotated_vec_StoP.Add(vec_survey_global)
        vec_pile_global.append(vec)    
    
    x_guid = System.Guid("b864344b-a63a-4521-be59-8948b2fcb440")
    y_guid = System.Guid("73e0567a-dce6-45f4-9240-2bb164a59fab")
    
    
    x_param_list = map(lambda e: e.get_Parameter(x_guid), piles_list)
    y_param_list = map(lambda e: e.get_Parameter(y_guid), piles_list)
    
    trans = Transaction(doc, "Set X Value")
    trans.Start()
    px_error_list = []
    py_error_list = []
    for px, py, vec in zip(x_param_list, y_param_list, vec_pile_global):
        pxOk = px.Set(vec.X)
        pyOk = py.Set(vec.Y)
        if not pxOk:
            px_error_list.append(px)
        if not pyOk:
            py_error_list.append(py)
    trans.Commit()
    if not px_error_list or not py_error_list:
        TaskDialog.Show("Succeed","Mission's completed!")
except Exception as error:
    TaskDialog.Show("Error",str(error))