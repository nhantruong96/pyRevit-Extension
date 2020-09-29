try:
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
    print(lengths)
    
#            x = feet_to_mm(i.Location.Point.X)
#            y = feet_to_mm(i.Location.Point.Y)
#            
#            angle = i.Location.Point.AngleTo(Ox)*180/math.pi
#            
#            
#            length = feet_to_mm(i.Location.Point.GetLength())
#            print(i, "{}, {}, {}, {}".format(x, y, length, angle))

except Exception as error:
    TaskDialog.Show("Error",str(error))