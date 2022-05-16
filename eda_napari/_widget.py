
from curses.panel import bottom_panel
from napari.utils.notifications import show_info
import matplotlib.style as style
import os
style.use(str(os.path.dirname(__file__))+'/plot_stylesheet.mplstyle') #get path of parent directory of script since plot_stylesheet is in the same directory
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSlider, QHBoxLayout, QPushButton, QLabel, QGridLayout, QScrollBar
import magicgui
from magicgui import magic_factory
from typing import Union
import qtpy
from qtpy.QtCore import Qt, QTimer
import numpy as np
from pathlib import Path
import math

import napari
import tifffile
import xmltodict


from PIL import Image
from skimage.filters import threshold_otsu





stylesheet = open(str(os.path.dirname(__file__))+'/q_label_stylesheet.qss',"r")
label_style = stylesheet.read()


#Union is a type: it forms the math union.
#It means the widget could be a magicgui widget or a qtpy widget.                                             
Widget = Union["magicgui.widgets.Widget", "qtpy.QtWidgets.QWidget"] 

class Frame_rate_Widget(QWidget):
   """The Frame rate plotter widget.

      This widget is a object inheriting from QWidget. Defining Frame_rate_Widget in the manifest 
      "napari.yaml" allows Napari to reconise it's existance and display it in the plugin. Upon it's creation the __init__ function ensures
      the execution of specific functions and plots the frame rates of an OME.tiff file inserted in the napari viewer.
   """

   def __init__(self, napari_viewer):
      """Constructor of the Frame_rate_Widget.
      
      This constructor initialises two blank canvases,the class's viewer to the napari viewer and connects events to functions to allow dynamic plots.
      A newly inserted file or modification of slider position in napari causes the plot to update.
      """
      super().__init__()
      self._viewer = napari_viewer
      self.image_path=None
      self.time_data=None
      self.frame_rate_data=None
      self.channel=0
      self.frame_x_axis_time=True
      self.setStyleSheet(label_style)

      
      #main plot widget
      self.layout=QVBoxLayout(self)
      self.grid_layout = QGridLayout()
     
      self.button_txt=('Time -> Frame number')
      self.button_axis_change=QPushButton(self.button_txt)
      self.button_axis_change.clicked.connect(self.change_axis)
      

      self.grid_layout.setAlignment(Qt.AlignHCenter) #Woow possible to do this with external style sheet
      self.grid_layout.setSpacing(2)
      self.grid_layout.setColumnMinimumWidth(0, 86)
      self.grid_layout.setColumnStretch(1, 1)

      self.frame_number_label = QLabel("Frame number: ")
      self.grid_layout.addWidget(self.frame_number_label, 1, 0)
      self.frame_number_value=QLabel("-")
      self.grid_layout.addWidget(self.frame_number_value, 1, 1)


      self.frame_time_label = QLabel("Time of frame capture: ")
      self.grid_layout.addWidget(self.frame_time_label, 2, 0)
      self.frame_time_value=QLabel("-")
      self.grid_layout.addWidget(self.frame_time_value, 2, 1)

      self.frame_rate_label = QLabel("Frame rate: ")
      self.grid_layout.addWidget(self.frame_rate_label, 0, 0)
      self.frame_rate_value=QLabel("-")
      self.grid_layout.addWidget(self.frame_rate_value, 0, 1)
  
      self._init_mpl_widgets() 
      self.layout.addWidget(self.button_axis_change)
      self.layout.addLayout(self.grid_layout)

      

      #events
      self._viewer.layers.events.inserted.connect(self.plot_frame_data)
      self._viewer.dims.events.current_step.connect(self.plot_slider_position)
      self._viewer.dims.events.current_step.connect(self.update_slowMo_icon)
      self._viewer.layers.events.removed.connect(self.update_widget)



      try:
        self.image_path = self._viewer.layers[0].source.path #when MyWidget is activated it search for exisiting image
        self.time_data=get_times(self)#init times of initial image
        self.frame_rate_data=self.get_frame_rate()#init frame rate of initial image
      except (IndexError,AttributeError): # if no image is found then an index Error would occur
          pass

      

   def _init_mpl_widgets(self):
      """Method to initialise 2 matplotlib figure canvases with a basic layout and title.

      This method generates a matplotlib.backends.backend_qt5agg.FigureCanvas and populates it with a
      matplotlib.pyplot.figure. The canvas is added to the QWidget Layout afterwards.
     """
      self.fig = plt.figure()
      self.canvas = FigureCanvas(self.fig)
      self.ax = self.fig.add_subplot(211)
      self.ax2 = self.fig.add_subplot(212)
      self.layout.addWidget(self.canvas)
      #self.setWindowTitle('Plot frame rate or frame times')
      try:
         self.plot_frame_data() #automatically plot frame data when Mywidget is called
      except(IndexError): # if no image is placed yet then Errors would occur when the source is retrieved
          pass
      
      
   
   def plot_times(self):
      self.ax.clear() #clear plot before plotting
      self.ax.set_ylabel('Time [ms]')
      self.ax.set_xlabel('Frame number')
      self.ax.set_title('Evolution of elapsed time')
      self.ax.plot(self.time_data)
      self.ax.ticklabel_format(axis='y', style='scientific', scilimits=(0,0), useMathText='True')
      self.line_1=self.ax.axvline(self._viewer.dims.current_step[0],0,1,linewidth=1, color='indianred')#initilaise a vertical line
      self.fig.canvas.draw()

   def get_frame_rate(self,unit_frame_r='Hz'):
      """ Method that returns frame rate.

      Input: unit of frame rate: [kHz] or [Hz]
      Output: Vector of frame rates in [kHz] or [Hz]
      
      The frame rate is calculate for each frame. Since the system is discrete, it must be approximated.
       For the first frame, the frame rate is approximated with the second frame time.For the other frames, the rate is calculated with the previous frame time."""
     
      if unit_frame_r=='Hz':
         conversion_factor =1000     #convert to kHz to Hz
      elif unit_frame_r=='kHz':
         conversion_factor=1  #inital data is in kHz since time is diplayed in ms
      else:
         print('unit of frame rate not reconised: please use Hz or kHz')

      N_frames= len(self.time_data)
      frame_rate=[conversion_factor/abs(self.time_data[1]-self.time_data[0])]#the first frame rate
      for i in range(1,N_frames):
         frame_rate.append(conversion_factor/abs(self.time_data[i]-self.time_data[i-1]))
      return frame_rate
   
   def plot_frame_rate(self,unit_frame_r='Hz'):

      self.ax2.clear() #clear plot before plotting
      self.ax2.set_ylabel('Frame rate ['+unit_frame_r+']')
      self.ax2.ticklabel_format(axis='x', style='scientific', scilimits=(0,0), useMathText='True')
      self.ax2.set_title('Evolution of the Frame rate ')
      if self.frame_x_axis_time:
         self.ax2.set_xlabel('Time [ms]')
         self.ax2.plot(self.time_data,self.frame_rate_data)
         vline_pos=self.time_data[self._viewer.dims.current_step[0]]
         txt_text_box='Time of current frame = '+str(self.time_data[self._viewer.dims.current_step[0]])+'[ms]'
      else:
         self.ax2.set_xlabel('Frame number')
         self.ax2.plot(self.frame_rate_data)
         vline_pos=self._viewer.dims.current_step[0]
         txt_text_box='Current frame number = '+str(self._viewer.dims.current_step[0])
      

      self.ax2.set_ylim(0,self.ax2.get_ylim()[1]*1.1) #increase plot for text space
      self.line_2=self.ax2.axvline(vline_pos,0,1,linewidth=1, color='indianred')#initialise a vertical line
      props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
      self.text_box=self.ax2.text(0.05, 0.95, txt_text_box, transform=self.ax2.transAxes, fontsize=8, verticalalignment='top', bbox=props,color='red')
      self.fig.canvas.draw()

   
   def plot_frame_data(self):#,event = None)
      self.image_path = self._viewer.layers[0].source.path #update image_path
      self.time_data=get_times(self) #update time and frame rate data
      self.frame_rate_data=self.get_frame_rate()
      self.plot_times()
      self.plot_frame_rate()
      current_frame=self._viewer.dims.current_step[0]
      if self.frame_x_axis_time:
         self.line_2.set_xdata(self.time_data[current_frame])#update according to x axis (time or frame)
      else: 
         self.line_2.set_xdata(current_frame)

      self.frame_rate_value.setText(str(np.around(self.frame_rate_data[current_frame],5)) + ' [Hz]')#init Qlabels
      self.frame_number_value.setText(str(current_frame))
      self.frame_time_value.setText(str(self.time_data[current_frame])+' [ms]')
      self.create_SlowMo_icon() #WOoW
      self.slow_mo()
      
      
   def plot_slider_position(self,event): #event information stored in "event"
      """ Method plots and updates slider position on the canvas.

      Input: event of current_step from slider
      Output: -
      After moving the slider on napari this function is called to update the vertical lines. The vertical
      lines show the frame rate and capture time of the current image disaplayed napari viewer"""
      current_frame=event.source.current_step[0]
      self.line_1.set_xdata(current_frame) #update line
      if self.frame_x_axis_time:
         self.line_2.set_xdata(self.time_data[current_frame])#update according to x axis (time or frame)
         self.text_box.set_text('Time of current frame = '+str(self.time_data[current_frame])+'[ms]')
      else: 
         self.line_2.set_xdata(current_frame)
         self.text_box.set_text('Current frame number = '+str(self._viewer.dims.current_step[0]))

      self.frame_rate_value.setText(str(np.around(self.frame_rate_data[current_frame],5)) + ' [Hz]')#update Qlabels
      self.frame_number_value.setText(str(current_frame))
      self.frame_time_value.setText(str(self.time_data[current_frame])+' [ms]')
      self.fig.canvas.draw()

     

   def change_axis(self):
      self.frame_x_axis_time=not self.frame_x_axis_time
      if self.frame_x_axis_time:
         button_txt='Time -> Frame number'
         self.current_frame_txt='Current frame number = '
         
      else:
         button_txt='Frame number -> Time'
      self.button_axis_change.setText(button_txt)
      self.plot_frame_rate()

   def create_SlowMo_icon(self):
      triangle=np.array([[20, 60], [60, 60], [40, 90]])
      rectangle=np.array([[20, 40],[60, 40],[60,25],[20,25]])
      polygon=[triangle,rectangle]
      self._viewer.add_shapes(polygon, shape_type='polygon', face_color='white',edge_width=2,
                          edge_color='black', name='Slow motion')

      self.slow_mo_channel=self._viewer.layers.index('Slow motion')
      self._viewer.layers[self.slow_mo_channel].visible=False #init to invisible
      
   def update_slowMo_icon(self,event):
      if(self.slow_mo_array[event.source.current_step[0]]):
         self._viewer.layers[self.slow_mo_channel].visible=True
      else:
         self._viewer.layers[self.slow_mo_channel].visible=False

   def slow_mo(self):
      size=len(self.time_data)
      self.slow_mo_array=np.empty(size)
      thresh=threshold_otsu(np.array(self.frame_rate_data))#threshold to determine weather slow motion or fast speed
      for i in range(0,size):
         if self.frame_rate_data[i]>=thresh:
            self.slow_mo_array[i]=False
         else:
            self.slow_mo_array[i]=True


   def update_widget(self,event):
      """ Method updates the widget in case of layer deletion

      Input: event created my deleted layer
      Output: -
      If slow motion is removed then the napari viewer is disconnected to the slow motion shape.
      If all layers are removed the dock plugin is removed.
     """
      if not ('Slow motion ' in event.source):
         self._viewer.dims.events.current_step.disconnect(self.update_slowMo_icon)
      if len(event.source)==0:
         self._viewer.window.remove_dock_widget(self)



class Add_time_scroller(QWidget):
   """Add_time_scroller class is a widget that creates a time scroll bar.  The scroll bar allows to animate stacks of 
   images linearly with time. Similary to the napari scroll bar, it has a play, stop, next and previous button."""
   
   def __init__(self, napari_viewer):
      """Constructor of the Add_time_scroller.
      
      This constructor initialises the button widgets and scroll bar widget in a QHBoxlayout. It also initialise the time of the frames
      from the image data available. Some signals are also defined to allow interaction and automatic updates between the current layer and
      the Add_time_scroller widget. A Qtimer is defined to controll the animation.
      """   
      super().__init__()
      self._viewer = napari_viewer
      self.image_path=None #folder path of the image data
      self.time_data=None
      self.channel=0
      self.number_frames=None
      self.show_time=50#animation default display time ms
      self.time_interval=None # time of the discretised time interval [ms]
      self.interval_frames_index=[]#discretised time interval filled with an index the the different frames.
      self.data_is_available=False
      self.step=1
      self.critical_ms=30
   
      self.timer=QTimer(self)
      self.timer.timeout.connect(self.play_step)

      self.layout=QHBoxLayout(self) 
      self.setMinimumWidth(500)
      self.setMaximumHeight(100)

      self.create_bottom_dock_button()
      self.create_slow_down()
      self.create_play_button()
      self.create_speed_up()
      self.create_time_scroller()
      self.create_axis_label() 

      self.layout.addWidget(self.bottom_dock_button)  
      self.layout.addWidget(self.slow_down_button)   
      self.layout.addWidget(self.play_button)
      self.layout.addWidget(self.speed_up_button)
      self.layout.addWidget(self.time_scroller)
      self.layout.addWidget(self.axis_label1)
      self.layout.addWidget(self.axis_label2)

      self.init_data()
      self._viewer.layers.events.inserted.connect(self.init_data) #init data when layer is inserted
      #events
      #self._viewer.layers.events.inserted.connect(self.init_data) #init data when layer is inserted
      #self.bottom_dock_button.clicked.connect(self.move_dock_to_bottom)
      #self.slow_down_button.clicked.connect(self.slow_animation)
      #self.play_button.clicked.connect(self.play)
      #self.speed_up_button.clicked.connect(self.speed_animation)
      #self._viewer.dims.events.current_step.connect(self.update_scroller_from_dims)#link window srolle to time srolle
      #self.time_scroller.valueChanged.connect(self.update_scroller_from_scroller) #link  

   def create_bottom_dock_button(self):
      self.bottom_dock_button=QPushButton('↓↓')
      self.bottom_dock_button.setMaximumWidth(35)

   def move_dock_to_bottom(self):
     self.parentWidget().parentWidget().addDockWidget(Qt.BottomDockWidgetArea,self.parentWidget()) # init position in QDockWidget (parent) to bottom in QWindow
     self.bottom_dock_button.deleteLater()


   def create_slow_down(self):
      self.slow_down_button=QPushButton('x 0.5')
      self.slow_down_button.setMaximumWidth(50)

   def slow_animation(self):
      if self.step == 1:
         self.show_time = self.show_time*2
         if self.play_button_txt=='Stop': #if program is playing
            self.timer.stop()
            self.timer.start(self.show_time) #set new show_time
      else:
         self.step=self.step/2
   def create_speed_up(self):
      self.speed_up_button=QPushButton('x 2')
      self.speed_up_button.setMaximumWidth(50)

   def speed_animation(self):
      if self.show_time >=self.critical_ms:
         self.show_time = self.show_time*0.5
         if self.play_button_txt=='Stop':
            self.timer.stop()
            self.timer.start(self.show_time)
      else:
         self.step=self.step*2
      
   def create_time_scroller(self):
      self.time_scroller= QScrollBar(Qt.Horizontal)
      self.time_scroller.setMinimum(0)
      self.time_scroller.setSingleStep(1)
      self.time_scroller.setMinimumWidth(150)

   def create_play_button(self):
      self.play_button_txt='Play >>'
      self.play_button=QPushButton(self.play_button_txt)
      self.play_button.setMaximumWidth(60)

   def create_axis_label(self):
      self.axis_label1=QLabel('End time')
      self.axis_label2=QLabel('Current time')
      #self.axis_label1.setMargin(0)

   def init_data(self):
      
       
      """This method initialises all the additonal data after an image stack is available and readable.
      """ 
      try:
         if self.image_path!=self._viewer.layers[0].source.path: #Only inits data if the layer is new
               self.image_path = self._viewer.layers[0].source.path
               self.time_data=get_times(self)#init times of image stack
               self.number_frames=len(self.time_data)
               self.init_time_interval()
               self.set_frames_index()
               #time scroller
               self.time_scroller.setMaximum(len(self.interval_frames_index)-1)
               idx=self.interval_frames_index.index(self._viewer.dims.current_step[0])
               self.time_scroller.setValue(idx) #set init position of scroller
               #init label2
               self.axis_label2.setText('| '+str(self.time_data[-1])+' [ms]')
               width2 = self.axis_label2.fontMetrics().boundingRect(self.axis_label2.text()).width() #max width of text
               self.axis_label2.setFixedWidth(1.1*width2)
               #init Label1
               self.axis_label1.setText(str(self.time_scroller.value()*self.time_interval))
               self.axis_label1.setFixedWidth(0.7*width2)

               #events
               self.bottom_dock_button.clicked.connect(self.move_dock_to_bottom)
               self.slow_down_button.clicked.connect(self.slow_animation)
               self.play_button.clicked.connect(self.play)
               self.speed_up_button.clicked.connect(self.speed_animation)
               self._viewer.dims.events.current_step.connect(self.update_scroller_from_dims)#link window srolle to time srolle
               self.time_scroller.valueChanged.connect(self.update_scroller_from_scroller) #link  
               self._viewer.layers.events.removed.connect(self.update_widget)
               self.data_is_avable=True

      except (IndexError,AttributeError): # if no image is found then an index Error would occur
          pass

   def init_time_interval(self):
      """This method sets the time discretisation interval of the system, for the animation and scroll bar.
      self.time_interval is initiliased as the 1/4 of the minimum time between to images frames. This creates a revelant discretisation of time with
      respect to the frame rates.
      """ 
      diff=[]
      for i in range(1,self.number_frames):
         diff.append(self.time_data[i]-self.time_data[i-1])
      min_diff=min(diff)
      self.time_interval = math.floor(min_diff/4)#this makes sure a relevant discretisation of time is made for the animation
   
   
   def set_frames_index(self):
      """This method sets self.interval_frames_index with image frames numbers. Each index corresponds the appropiate image frame
      that should be displayed in the discretized time.
      """ 
      frame_index=0
      t=0
      self.interval_frames_index=[0]
      while frame_index < self.number_frames-1:
         t+=self.time_interval
         if self.time_data[frame_index+1] < t:
            frame_index+=1
         self.interval_frames_index.append(frame_index)


   def play_step(self):
      """This method advances the time of 1 time interval and takes car of updating the current displayed frame if necessary.
      """ 
      if self._viewer.dims.current_step[0]== self.number_frames-1:
         self._viewer.dims.set_current_step(0, 0)#restart at frame 0
         self.time_scroller.setValue(0)
      else:
         self.time_scroller.setValue(self.time_scroller.value()+self.step)
         if self.interval_frames_index[self.time_scroller.value()] != self._viewer.dims.current_step[0]: #update viewer
            self._viewer.dims.set_current_step(0, self.interval_frames_index[self.time_scroller.value()])
  
   def play(self): # play and stop method
      if self.play_button_txt =='Play >>': 
         self.timer.start(self.show_time)
         self.play_button_txt = 'Stop'
         self.play_button.setText(self.play_button_txt)
         self.play_button.setMaximumWidth(80)
       
      else: #stop  
         self.timer.stop()
         self.play_button_txt = 'Play >>'
         self.play_button.setText(self.play_button_txt)
       
   def update_scroller_from_dims(self):
      idx=self.interval_frames_index.index(self._viewer.dims.current_step[0])
      self.time_scroller.valueChanged.disconnect(self.update_scroller_from_scroller)#avoid double calling
      self.time_scroller.setValue(idx)
      if self._viewer.dims.current_step[0]==self.number_frames-1:
         self.axis_label1.setText(str(self.time_data[-1]))
      else:
         self.axis_label1.setText(str(self.time_scroller.value()*self.time_interval))
      self.time_scroller.valueChanged.connect(self.update_scroller_from_scroller) #reconnect

   def update_scroller_from_scroller(self):
      if self.interval_frames_index[self.time_scroller.value()] != self._viewer.dims.current_step[0]: #update viewer #one
         self._viewer.dims.events.current_step.disconnect(self.update_scroller_from_dims) #avoid double calling
         self._viewer.dims.set_current_step(0, self.interval_frames_index[self.time_scroller.value()])
         self._viewer.dims.events.current_step.connect(self.update_scroller_from_dims) #reconnect

      if self._viewer.dims.current_step[0]==self.number_frames-1:
         self.axis_label1.setText(str(self.time_data[-1]))
      else:
         self.axis_label1.setText(str(self.time_scroller.value()*self.time_interval))


   def update_widget(self,event):
      if len(event.source)==0:
         self._viewer.window.remove_dock_widget(self)


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

  
   
def get_times(widget):
   """Method that gets the capture time from the metadata.
   
   Input:-
   Output: Vector of time metadata [ms] of images found at given image path and channel.
   The times of each image stack from a ome.tif file is read in [ms] or [s] and then returned in [ms]. 
   The times are taken from a given channel. The data can only be read from an ome.tif file. The Offset 
   from time t=0 subrtracted to the times before it is returned."""
   times=[]
   with tifffile.TiffFile(widget.image_path) as tif:
      XML_metadata= tif.ome_metadata #returns a reference to a function that accesses the metadata as a OME XML file
      dict_metadata=xmltodict.parse(XML_metadata) #converts the xml to a dictionary to be readable
      num_pages=len(tif.pages) #the number of images stacked
      for frame in range(0,num_pages):
         #time should be in either s or ms
         if float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@TheC'])==widget.channel: #checks if correct channel
            frame_time_unit=dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaTUnit']
            if frame_time_unit== 's' :
               convert_unit_to_ms=1000
               times.append(convert_unit_to_ms*float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaT']))
            elif frame_time_unit == 'ms':
               convert_unit_to_ms=1
               times.append(convert_unit_to_ms*float(dict_metadata['OME']['Image']['Pixels']['Plane'][frame]['@DeltaT']))
            else:
               print('Time units not in ms or s but in '+ frame_time_unit+'. A conversion to ms or s must be done.')
   
   times = [x - times[0] for x in times] #remove any offset from time=0
   return times
