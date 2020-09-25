# -*- coding: utf-8 -*-
# =============================================================================
# 
# =============================================================================


__title__ = "Tranfer"
__Author__ = "Nhan Truong"

org = "Portcoast Consultant Corporation"
na = "Nhan Truong"
em = "nhan.tnt@portcoast.com.vn"
mo = "+84 379197306"


# =============================================================================
# 
# =============================================================================


import os
import sys
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB.BuiltInCategory import * 
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

#find the path of ui.xaml
import pyrevit
from pyrevit import script
from pyrevit import UI
xamlfile = script.get_bundle_file('ui.xaml')

import wpf
import System
from System import Windows
from System.Windows.Media. Imaging import BitmapImage
from System import Uri, UriKind


# =============================================================================
# Functions
# =============================================================================


def get_ViewType(document):
    view_class_collector = DB.FilteredElementCollector(document).OfCategory(OST_Views)
    list_ViewType = list()
    for i in view_class_collector:
        if i.GetType() not in list_ViewType:
            list_ViewType.append(i.GetType())
    return list_ViewType

  
# =============================================================================
# End Get View Type
# =============================================================================


dir_name = os.path.dirname(__file__)
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application


# =============================================================================
# Some Dialog
# =============================================================================


footer_Text = '<a href="https://www.portcoast.com.vn/">@ 2020 Portcoast Consultant Corporation </a>'

creditDialog = UI.TaskDialog("About")
creditDialog.TitleAutoPrefix = False
creditDialog.Title = "About"
creditDialog.MainInstruction = "Tranfer View Filters Tool"
creditDialog.MainContent = """This Add-in is made possible pyRevit open source project
and Windows Presentation Foundation (WPF).\n\nAuthor: {}\nEmail: {}\nTel: {}""".format(na, em, mo)
creditDialog.FooterText = footer_Text


ErroDialog = UI.TaskDialog("Error Message")
ErroDialog.TitleAutoPrefix = False
ErroDialog.CommonButtons = UI.TaskDialogCommonButtons.Ok
ErroDialog.FooterText = footer_Text


warningDialog = UI.TaskDialog("Warning Message")
warningDialog.TitleAutoPrefix = False
warningDialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconWarning
warningDialog.FooterText = footer_Text


# =============================================================================
# 
# =============================================================================


class MyWindow(Windows.Window):
    
    filter_source = list()
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)
        
        self.Icon = BitmapImage(Uri(dir_name + "\\portcoast.ico", UriKind.Relative))
        
        global viewType_Source
        viewType_Source = get_ViewType(doc)
        global viewType_Source_Name
        viewType_Source_Name = map(lambda x: x.Name, viewType_Source)
        self.cbbViewType.ItemsSource = viewType_Source_Name
        self.cbbViewType2.ItemsSource = viewType_Source_Name
        global view_Source
        view_Collector = DB.FilteredElementCollector(doc).\
                        OfCategory(OST_Views).ToElements()
        view_Source = map(lambda x: x, view_Collector)
        global view_Source_Name
        view_Source_Name = map(lambda i: "{}: {}".\
                               format(i.ViewType, i.Name) ,view_Source)
        
        self.lbViewNames.ItemsSource = view_Source_Name
    
    def cbbViewType_Select(self, sender, args):
        viewType = viewType_Source[viewType_Source_Name.\
                                   index(self.cbbViewType.SelectedItem)]
        views_list1 = DB.FilteredElementCollector(doc).OfClass(viewType).ToElements()
        self.cbbViewName.ItemsSource = map(lambda i: "{}: {}".\
                                           format(i.ViewType, i.Name), views_list1)
        self.cbbViewName.SelectedItem = self.cbbViewName.ItemsSource[0]
    
    def cbbViewName_Select(self, sender, args):
        global viewInstance
        view_Instance_Name = self.cbbViewName.SelectedItem
        if view_Instance_Name in view_Source_Name:
            viewInstance = view_Source[view_Source_Name.index(view_Instance_Name)]
        global filter_source
        filter_source = viewInstance.GetFilters()
        global filter_names
        filter_names = map(lambda i: doc.GetElement(i).Name, filter_source)
        self.lbFiltersName.ItemsSource = filter_names
    
    def cbbViewType2_Select(self, sender, args):
        viewType2 = viewType_Source[viewType_Source_Name.\
                                    index(self.cbbViewType2.SelectedItem)]
        views_list2 = DB.FilteredElementCollector(doc).\
                        OfClass(viewType2).ToElements()
        self.lbViewNames.ItemsSource = map(lambda i: "{}: {}".\
                                           format(i.ViewType, i.Name), views_list2)
    
    def btnOK_Click(self, sender, args):
        UI.TaskDialog.Show("Information Message","Coming Soon!")
        
    def btnTranfer_Click(self, sender, args):
        selected_Views_Index = map(lambda v: view_Source_Name.index(v),\
                                   self.lbViewNames.SelectedItems)
        selected_Views = map(lambda s: view_Source[s], selected_Views_Index)
        
        global selected_Filters_Name
        selected_Filters_Name = self.lbFiltersName.SelectedItems
        global selected_Filters
        selected_Filters = map(lambda f: filter_source[filter_names.index(f)],\
                               selected_Filters_Name)
        
        trans = Transaction(doc, "Transfer Filter")
        dupplicatedFilters = []
        succeedFilters = []
        trans.Start()
        for v in selected_Views:
            for f in selected_Filters:
                if v.IsFilterApplied(f):
                    dupplicated_Filters_Name = doc.GetElement(f).Name
                    dupplicatedFilters.append(dupplicated_Filters_Name)
                elif not v.IsFilterApplied(f):
                    v.AddFilter(f)
                    v.SetFilterOverrides(f, viewInstance.GetFilterOverrides(f))
                    succeed_Filters_Name = doc.GetElement(f).Name
                    succeedFilters.append(succeed_Filters_Name)
        trans.Commit()
        
        if dupplicatedFilters:
            ErroDialog.Title = "Warning"
            ErroDialog.MainInstruction = "Warning Message"
            ErroDialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconWarning
            ErroDialog.MainContent = "{} is dupplicated.\n{} is tranfered.".\
                                    format(dupplicatedFilters, succeedFilters)
            ErroDialog.Show()
        elif not dupplicatedFilters:
            ErroDialog.Title = "Information"
            ErroDialog.MainInstruction = "Information Message"
            ErroDialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconInformation
            ErroDialog.MainContent = "Succeed"
            ErroDialog.Show()
        
    def btnCancel_Click(self, sender, args):
        self.Close()
        
    def btnDeleteFilters_Click(self, sender, args):
        selected_Filters_Name = self.lbFiltersName.SelectedItems #cant use global?
        selected_Filters = map(lambda f: filter_source[filter_names.index(f)],
                               selected_Filters_Name) #cant use global?
        if not selected_Filters:
            warningDialog.MainContent = "No Filter is selected!"
            warningDialog.DefaultButton = UI.TaskDialogResult.Cancel
            warningDialog.Show()
        else:
            warningDialog.MainContent = "{} will be deleted.\n Are you sure?".\
                                        format(map(lambda x: x,\
                                                   selected_Filters_Name))
            warningDialog.CommonButtons = UI.TaskDialogCommonButtons.Yes\
                                        | UI.TaskDialogCommonButtons.No
            warnDialog = warningDialog.Show()
            if warnDialog == UI.TaskDialogResult.Yes:
                trans = Transaction(doc, "Delete Filters")
                trans.Start()
                map(lambda x: viewInstance.RemoveFilter(x), selected_Filters)
                trans.Commit()
        
        #Update Filters List
        view_Instance_Name_ = self.cbbViewName.SelectedItem
        if view_Instance_Name_ in view_Source_Name:
            filter_Source_ = view_Source[view_Source_Name.\
                                         index(view_Instance_Name_)].GetFilters()
        self.lbFiltersName.ItemsSource = map(lambda i: doc.GetElement(i).Name,\
                                             filter_Source_)

    def mnCredit_Click(self, sender, args):
        creditDialog.Show()
        
MyWindow().ShowDialog()