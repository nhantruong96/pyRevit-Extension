import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *


uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

newCloudPoint = PointClouds.CloudPoint(0,0,0,1)

print(newCloudPoint.X)