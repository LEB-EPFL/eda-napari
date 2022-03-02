
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


Widget = Union["magicgui.widgets.Widget", "qtpy.QtWidgets.QWidget"]


class MyWidget(QWidget):
   def __init__(self, napari_viewer):
   #def __init__(self, viewer: 'napari.viewer.Viewer'):
      super().__init__()
      self._viewer = napari_viewer
      self.run_function=QPushButton('Run function')
      self.run_function.clicked.connect(self.plot_line)
      self.layout=QVBoxLayout(self)
      self._init_mpl_widgets()
      self.layout.addWidget(self.run_function)
        
   def _init_mpl_widgets(self):
      """Method to initialise a matplotlib figure canvas and the VoxelPlotter UI.

      This method generates a matplotlib.backends.backend_qt5agg.FigureCanvas and populates it with a
      matplotlib.figure.Figure and further matplotlib artists. The canvas is added to a QVBoxLayout afterwards.
     """
      # set up figure and axe objects
      self.fig = Figure()
      self.canvas = FigureCanvas(self.fig)
      # TODO: find a way to include the toolbar with a compatible style
      #self.toolbar = NavigationToolbar(self.canvas, self)
      # self.toolbar.setStyleSheet("color:Black;")
      self.ax = self.fig.add_subplot(111)
      self.ax.annotate('Hold "Shift" while moving over the image'
                        '\nto plot pixel signal over time',
                        (0.5, 0.5),
                        ha='center',
                        va='center',
                        size=15,
                        bbox=dict(facecolor=(0.9, 0.9, 0.9), alpha=1, boxstyle='square'))

      # layout.addWidget(self.toolbar)
      self.layout.addWidget(self.canvas)
      self.setWindowTitle('Voxel Plotter')

   def plot_line(self):
      self.ax.plot([1,2,3,4])
      self.fig.canvas.draw()
      

from magicgui import magic_factory
@magic_factory #what does this do? with it doesn't work for me
def show_plot(
    image: "napari.types.ImageData", threshold: int
   ) -> "napari.types.LabelsData":
    """Generate thresholded image.

    This pattern uses magicgui.magic_factory directly to turn a function
    into a callable that returns a widget.
    """
    return (image > threshold).astype(int)
