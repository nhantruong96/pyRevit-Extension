import wpf

from System import Uri, UriKind
from System.Windows import Window
from System.Windows.Controls import Image
from System.Windows.Media.Imaging import BitmapImage
#find the path of ui.xaml
import pyrevit
from pyrevit import script
from pyrevit import UI
xamlfile = script.get_bundle_file('New_App_UI.xaml')

class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)
        logo = Image()
        bi = BitmapImage()
        bi.BeginInit()
        bi.UriSource = Uri("/logo-portcoast.png", UriKind.Relative)
        bi.EndInit()
        logo.Source = bi
MyWindow().ShowDialog()
