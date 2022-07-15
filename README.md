# The Plugin

## How to install

To install get the repository at https://github.com/LEB-EPFL/eda-napari.git in your computer
Then open it and install it through the command
```sh
pip install eda-napari
```
## How to activate it

In the napari interface, click the plugin button which is in the menubar in the high-left of the screen.
Then it should appear the eda-napari button. Clicking on it you will see the two widgets that you can apply: the frame rate widget and the time scroller widget. Click on the one that you want to use.

![where the plugins can be activated](resources/eda-napari_activation_example.png)

## Features

### Frame rate plugin

This widget reads metadata from tif files originating from microscope imaging. From a time-lapse image stack, the widget reads the capture time of each individual image. This time data is stored and the frame rate is approximated from this data.
This plugin make three plots visibles:
One of the actual elapsed time in the video against the actual frame number.
One of the frame rate as a funtion of the time elapsed.
One of the frame rate as a function of the frame number.
In all plots the actual frame number and time are pointed out by a red vertical line.


### Time scroll plugin

This widget is to animate the time-lapse linearly in time. This is useful because napari’s scroll bar animates individual frames with a constant time interval without taking into account the actual time from the metadata. In the time scroller it is also possible to modify the speed of the animation thanks to a speed up and a speed down button.