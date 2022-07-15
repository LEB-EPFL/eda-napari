# The Plugin

## How to install

To install get the repository at https://github.com/LEB-EPFL/eda-napari.git in your computer
Then open it and install it through the command
'''sh
pip install eda-napari
'''


## Features

### Frame rate plugin

This widget reads metadata from tif files originating from microscope imaging. From a time-lapse image stack, the widget reads the capture time of each individual image. This time data is stored and the frame rate is approximated from this data and then ploted in a dock widget in the napari viewer window The widget is implemented as a class with an initialisation, class attributes, connections to napari events and class methods.

### Time scroll plugin

Time scroller widget is the second class widget of this plugin (Figure 5). The widget creates a QScrollbar that discretizes time. The goal of the widget is to animate the time-lapse linearly in time. This is useful because napari’s scroll bar animates individual frames with a constant time interval without taking into account the actual time from the metadata. The class is code similarly to the frame rate widget and is set in a second dock widget.