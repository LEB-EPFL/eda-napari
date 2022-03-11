
from napari.utils.notifications import show_info

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import FigureCanvas
from qtpy.QtWidgets import QDialog, QWidget, QVBoxLayout
import magicgui
from magicgui import magic_factory
from typing import Union
import qtpy
from qtpy.QtWidgets import QPushButton, QVBoxLayout
import napari 


#install tiff file reader plugin
from napari_tifffile_reader import napari_get_reader
import tifffile
import xmltodict

#import ctypes
                                               

Widget = Union["magicgui.widgets.Widget", "qtpy.QtWidgets.QWidget"] 
#Union is a type: it forms the math union. 
#It means the widget could be a magicgui widget or a qtpy widget.


class MyWidget(QWidget):
   def __init__(self, napari_viewer):
   #def __init__(self, viewer: 'napari.viewer.Viewer'):
      super().__init__()
      self._viewer = napari_viewer
      self.run_function=QPushButton('Plot frame times')
      self.run_function.clicked.connect(self.plot_times)
      self.layout=QVBoxLayout(self)
      self._init_mpl_widgets()
      self.layout.addWidget(self.run_function)
      #open up tiff file
      self.image_path = self._viewer.layers[0].source.path #only works if file has been added to layer, possible to find current layer?

   def _init_mpl_widgets(self):
      """Method to initialise a matplotlib figure canvas and the VoxelPlotter UI.

      This method generates a matplotlib.backends.backend_qt5agg.FigureCanvas and populates it with a
      matplotlib.figure.Figure and further matplotlib artists. The canvas is added to a QVBoxLayout afterwards.
     """
      # set up figure and axe objects
      self.fig = Figure()
      self.canvas = FigureCanvas(self.fig)
      self.ax = self.fig.add_subplot(111)
      self.ax.set_ylabel('Time [ms]')
      self.ax.set_xlabel('Frame number')
      self.ax.set_title('Evolution of elapsed time between frames')
      self.layout.addWidget(self.canvas)
      self.setWindowTitle('Voxel Plotter')

   def plot_line(self):
      self.ax.plot([1,2,3,4])
      self.fig.canvas.draw()

   def load_times(self,image_stack_path,channel=0):
      """load frame times in ms from .ome.tif file for a certain channel"""
      times=[]
      #print(self.image_path)
      with tifffile.TiffFile(image_stack_path) as tif:
         XML_metadata= tif.ome_metadata #returns an  OME XML file, without () invokes the function without calling it, calling it causes an error
         dict_metadata=xmltodict.parse(XML_metadata) #converts the xml to a dictionary to be readable
         num_pages=len(tif.pages) #the number of images stacked
         for frame in range(0,num_pages):
            #time should be in either s or ms
            if float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@TheC'])==channel: #checks if correct channel
               frame_time_unit=dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaTUnit']
               if frame_time_unit== 's' :
                  convert_unit_to_ms=1000
                  times.append(convert_unit_to_ms*float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaT']))
               elif frame_time_unit == 'ms':
                  convert_unit_to_ms=1
                  times.append(convert_unit_to_ms*float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaT']))
               else:
                  print('Time units not in ms or s but in '+ frame_time_unit+'. A conversion to ms or s must be done.')
      
      return times
         
   def plot_times(self):
      times=self.load_times(self.image_path)
      #times = times-times[0] #start at 0 but error because list can't do the - operation
      self.ax.plot(times)
      self.fig.canvas.draw()



from magicgui import magic_factory
# decorate your function with the @magicgui decorator
@magic_factory #what does this do? with it doesn't work for me
def show_plot(
    image: "napari.types.ImageData", threshold: int
   ) -> "napari.types.LabelsData":
    """magicgui allows to quickly create a widget after defining an input and output type.
    This test creates thresholded image.

    This pattern uses magicgui.magic_factory directly to turn a function
    into a callable that returns a widget.
    """
    return (image > threshold).astype(int)



