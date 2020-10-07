#! python3

import sys

import os
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

import comtypes
from comtypes import client

import _revit

AttachToInstance = True

# Full path to the model

APIPath = 'C:\CSIAPIExample'

if not os.path.exists(APIPath):
    try:
        os.makedirs(APIPath)
    except OSError:
        pass
    
ModelPath = APIPath + os.sep + 'test.sdb'

# Get Revit API object

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

framingList = _revit.get_Elements(doc, BuiltInCategory.OST_StructuralFraming)

# Create API helper object

helper = comtypes.client.CreateObject('SAP2000v1.Helper')

helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

# Attach to a running instance of SAP2000
# get the active SapObject

mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")

if mySapObject == None:
    
    #create an instance of the SAPObject from the latest installed SAP2000
    
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

# Start SAP2000 application    

mySapObject.ApplicationStart()    

# Create SapModel object

SapModel = mySapObject.SapModel

# Initialize model

SapModel.InitializeNewModel()

# Create new blank model

ret = SapModel.File.NewBlank()

# Define material property

# Define section property

# Add frame object

# Assign point object restraint

# Refresh view

# Add load pattern

# Assign loading for load pattern

# Assign combination

# Save model

ret = SapModel.File.Save(ModelPath)

# Close SAP2000 application

ret = mySapObject.ApplicationExit(False)

SapModel = None

mySapObject = None