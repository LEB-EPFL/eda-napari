import napari
import os



with napari.gui_qt():  #what is this why can't open directly?
    viewer = napari.Viewer() 
    path=str(os.path.dirname(__file__))+'/images/example_image.tif'
    viewer.open(path,plugin="aicsimageio-in-memory")
    viewer.window.add_plugin_dock_widget('eda-napari','Plot frame rate') #'Add time scroller'