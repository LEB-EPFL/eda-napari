import napari
from eda_napari import _widget



with napari.gui_qt():  #what is this why can't open directly?
    viewer = napari.Viewer() 
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif",plugin="aicsimageio-in-memory")
    viewer.window.add_plugin_dock_widget('eda-napari','Add time scroller') #'Add time scroller',  'Plot Frame rate'