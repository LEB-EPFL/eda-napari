#This file is the code for automatic loading of napari with images and specified plugin
#The file can be used for saving time during tests and when wanting to visulaise multiple times the same image file.
import napari
import os

viewer = napari.Viewer() 
path=  str(os.path.dirname(__file__))+'/images/steven_5.ome.zarr/Images'#"https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.3/9836842.zarr/"
#viewer.open(path, plugin = 'napari-ome-zarr')
#path2=  str(os.path.dirname(__file__))+'/images/steven_5.ome.zarr/EDA'#"https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.3/9836842.zarr/"
#viewer.open(path2, plugin = 'napari-ome-zarr')
#viewer.window.add_plugin_dock_widget('eda-napari','Plot frame rate') #'Add time scroller'
napari.run()