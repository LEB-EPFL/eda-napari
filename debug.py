import napari


with napari.gui_qt():  #what is this why can't open directly?
    viewer = napari.Viewer() 
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    #napari.components.ViewerModel.open()