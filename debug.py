import napari
import os

viewer = napari.Viewer() 
path=str(os.path.dirname(__file__))+'/images/example_image.tif'
viewer.open(path,plugin="aicsimageio-in-memory")
viewer.window.add_plugin_dock_widget('eda-napari','Plot frame rate') #'Add time scroller'
napari.run()