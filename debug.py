import napari
from eda_napari import _widget



with napari.gui_qt():  #what is this why can't open directly?
    viewer = napari.Viewer() 
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    widget=_widget.Frame_rate_Widget(viewer)
    #dock_widget = viewer.window.add_dock_widget(widget, area='right')
    #viewer.addDockWidget(qtpy.RightDockWidgetArea, _widget.Frame_rate_Widget(viewer)) #creates plots but not in napari
    #napari.components.ViewerModel.open(viewer)