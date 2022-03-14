
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
from functools import partial

#import ctypes
                                               

Widget = Union["magicgui.widgets.Widget", "qtpy.QtWidgets.QWidget"] 
#Union is a type: it forms the math union. 
#It means the widget could be a magicgui widget or a qtpy widget.


class MyWidget(QWidget):
   def __init__(self, napari_viewer):
   #def __init__(self, viewer: 'napari.viewer.Viewer'):
      super().__init__()
      self._viewer = napari_viewer
      #self._viewer.layers.events.inserted.connect(image_arithmetic.reset_choices)
      self.run_button_times=QPushButton('Plot frame times')
      self.run_button_times.clicked.connect(self.plot_times)
      self.run_button_frame_r=QPushButton('Plot frame rate')
      self.run_button_frame_r.clicked.connect(lambda: self.plot_frame_rate('Hz')) #connect signal to a lamda to allow default arguments of function to be called
      self.layout=QVBoxLayout(self)
      self._init_mpl_widgets()
      self.layout.addWidget(self.run_button_times)
      self.layout.addWidget(self.run_button_frame_r)
      self.image_path = self._viewer.layers[0].source.path #only works if file has been added to layer, possible to find current layer?

   def _init_mpl_widgets(self):
      """Method to initialise a matplotlib figure canvas and the VoxelPlotter UI.

      This method generates a matplotlib.backends.backend_qt5agg.FigureCanvas and populates it with a
      matplotlib.figure.Figure and further matplotlib artists. The canvas is added to a QVBoxLayout afterwards.
     """
      # set up figure and axe objects
      self.fig = Figure()
      self.fig2 = Figure()
      self.canvas = FigureCanvas(self.fig)
      self.canvas2 = FigureCanvas(self.fig2)
      self.ax = self.fig.add_subplot(111)
      self.ax2 = self.fig2.add_subplot(111)
      self.layout.addWidget(self.canvas)
      self.layout.addWidget(self.canvas2)
      self.setWindowTitle('Plot frame rate or frame times')

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
   
   
   def get_times(self,channel=0):
      """This function gets frame capture times for a specific channel and starts with time=0"""
      times=self.load_times(self.image_path,channel)
      times = [x - times[0] for x in times] #start at time 0
      return times


   def plot_times(self):
      self.ax.clear() #clear plot before plotting
      self.ax.set_ylabel('Time [ms]')
      self.ax.set_xlabel('Frame number')
      self.ax.set_title('Evolution of elapsed time between frames')
      times=self.get_times()
      self.ax.plot(times)
      self.fig.canvas.draw()


   
   def plot_frame_rate(self,unit_frame_r='Hz'):
      """ The frame rate is calculate for each frame. Since the system is discrete it must be approximated.
       For the first and last frame the last interval will be taken. For the others the avg of the previous 
       and next interval will approximate the frame rate."""
      if unit_frame_r=='Hz':
         conversion_factor =1000
      elif unit_frame_r=='kHz':
         conversion_factor=1
      else:
         print('unit of frame rate not reconised: please use Hz or kHz')

      self.ax2.clear() #clear plot before plotting
      self.ax2.set_ylabel('Frame rate ['+unit_frame_r+']')
      self.ax2.set_xlabel('Frame number')
      self.ax2.set_title('Evolution of the Frame rate ')
      times=self.get_times()
      N_frames= len(times)
      frame_rate=[1/abs(times[1]-times[0])]#for the first frame rate no avg can be computed
      for i in range(1,N_frames-1):
         avg_rate=0.5*(1/abs(times[i+1]-times[i]) + 1/abs(times[i]-times[i-1]))
         frame_rate.append(avg_rate)
      frame_rate.append(1/abs(times[1]-times[0])) #last frame rate
      frame_rate = [x * conversion_factor for x in frame_rate] #convert to Hz or kHz
      self.ax2.plot(frame_rate)
      self.fig2.canvas.draw()

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



