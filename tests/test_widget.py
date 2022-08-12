"""
test module eda-napari.
"""
from re import X
from tkinter import E
from leb.eda_napari._widget import Frame_rate_Widget, Time_scroller_widget, connect_eda, get_times
from unittest.mock import MagicMock
import pytest
import os
#import time

test_image_tif_path= str(os.path.dirname(os.path.dirname(__file__)))+'/images/example_image.tif'
test_image_ngff_path= str(os.path.dirname(os.path.dirname(__file__)))+'/images/steven_5.ome.zarr/Images'

#####Fixtures#####
@pytest.fixture
def plot_widget(make_napari_viewer):  #creates Frame_rate_Widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_after_load_tif(make_napari_viewer):  #creates Frame_rate_Widget for the viewer loads data then return the widget
    viewer = make_napari_viewer(show=False)
    viewer.open(test_image_tif_path)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_after_load_ngff(make_napari_viewer):  #creates Frame_rate_Widget for the viewer loads data then return the widget
    viewer = make_napari_viewer(show=False)
    viewer.open(test_image_ngff_path)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def time_widget(make_napari_viewer): #creates Time_scroller_widget_widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Time_scroller_widget(viewer) 

@pytest.fixture
def time_widget_loaded(make_napari_viewer): #loads image to viewer then creates widget
    viewer = make_napari_viewer(show=False)
    viewer.open(test_image_tif_path)
    yield Time_scroller_widget(viewer)

#######TESTS########


#####TIME SCROLL BAR

#basic test

def test_time_widget_attribute(time_widget: Time_scroller_widget):
    assert time_widget.channel==0 , "channel attribute doesn't init with 0"

def test_time_widget_open_image(time_widget: Time_scroller_widget):
    assert time_widget.image_path == None, 'path Attribute no init with None'
    time_widget._viewer.open(test_image_tif_path)
    assert  time_widget.image_path != None,'path Attribute not updated from None'
    assert  time_widget.time_data != None,'time Attribute not updated from None'

def test_add_time_widget(time_widget_loaded: Time_scroller_widget):
        assert time_widget_loaded.image_path != None,'path Attribute not updated from None'
        assert  time_widget_loaded.time_data != None,'time Attribute not updated from None'

#speed up test

def test_x2speed_lowst (time_widget_loaded: Time_scroller_widget): #tests for the x2speed button or showtime under the critical
    time_widget_loaded.show_time = time_widget_loaded.critical_ms//2
    alpha = time_widget_loaded.step
    time_widget_loaded.speed_animation()
    assert time_widget_loaded.step == alpha*2, 'step not doubled'

def test_x2speed_highst_whenstopped (time_widget_loaded: Time_scroller_widget): #tests for the x2speed button or showtime over the critical
    time_widget_loaded.show_time = time_widget_loaded.critical_ms*21
    alpha = time_widget_loaded.show_time
    time_widget_loaded.speed_animation()
    assert time_widget_loaded.show_time == alpha*0.5, 'showtime not halved'

def test_x2speed_highst_whenplay (time_widget_loaded: Time_scroller_widget): #tests for the x2speed button or showtime over the critical
    time_widget_loaded.show_time = time_widget_loaded.critical_ms*21
    if time_widget_loaded.play_button_txt == 'Play >>':
        time_widget_loaded.play()
    faketimer = MagicMock()
    time_widget_loaded.timer = faketimer
    alpha = time_widget_loaded.show_time
    time_widget_loaded.speed_animation()
    assert time_widget_loaded.show_time == alpha*0.5, 'showtime not halved'
    time_widget_loaded.timer.stop.assert_called()
    time_widget_loaded.timer.start.assert_called()

    #speed down tests

def test_halfspeed_lowst (time_widget_loaded: Time_scroller_widget): #tests for the x0.5speed button for step = 1
    time_widget_loaded.step = 1
    alpha = time_widget_loaded.show_time
    time_widget_loaded.slow_animation()
    assert time_widget_loaded.show_time == alpha*2, 'showtime not doubled'

def test_halfspeed_highst_whenstopped (time_widget_loaded: Time_scroller_widget): #tests for the x0.5speed button or showtime over the critical
    time_widget_loaded.step = 10
    alpha = time_widget_loaded.step
    time_widget_loaded.slow_animation()
    assert time_widget_loaded.step == alpha*0.5, 'step not halved'

def test_halfspeed_highst_whenplay (time_widget_loaded: Time_scroller_widget): #tests for the x2speed button or showtime over the critical
    time_widget_loaded.step = 1
    if time_widget_loaded.play_button_txt == 'Play >>':
        time_widget_loaded.play()
    faketimer = MagicMock()
    time_widget_loaded.timer = faketimer
    alpha = time_widget_loaded.show_time
    time_widget_loaded.slow_animation()
    assert time_widget_loaded.show_time == alpha*2, 'showtime not doubled'
    time_widget_loaded.timer.stop.assert_called()
    time_widget_loaded.timer.start.assert_called()

    # play_step test

def test_play_step(time_widget_loaded: Time_scroller_widget):
    alpha = time_widget_loaded.time_scroller.value()
    time_widget_loaded.play_step()
    assert time_widget_loaded.time_scroller.value() == alpha + int(time_widget_loaded.step), 'time scroller value nut updated'

def test_play_step_last(time_widget_loaded: Time_scroller_widget):
    time_widget_loaded._viewer.dims.set_current_step(0, time_widget_loaded.number_frames-1)
    time_widget_loaded.play_step()
    assert time_widget_loaded._viewer.dims.current_step[0] == 0, 'video not reinitialized'

    #play test

def test_play_on_play (time_widget_loaded:Time_scroller_widget):
    faketimer = MagicMock()
    time_widget_loaded.timer = faketimer
    time_widget_loaded.play()
    assert time_widget_loaded.play_button_txt == 'Stop'
    time_widget_loaded.timer.start.assert_called()

def test_play_on_stop (time_widget_loaded:Time_scroller_widget):
    time_widget_loaded.play_button_txt = 'Stop'
    faketimer = MagicMock()
    time_widget_loaded.timer = faketimer
    time_widget_loaded.play()
    assert time_widget_loaded.play_button_txt == 'Play >>'
    time_widget_loaded.timer.stop.assert_called()

#test update scroller from dims

def test_up_scroller_dims (time_widget_loaded: Time_scroller_widget):
    fakelabel = MagicMock()
    time_widget_loaded.axis_label1 = fakelabel
    time_widget_loaded.update_scroller_from_dims()
    time_widget_loaded.axis_label1.setText.assert_called()


######FRAME RATE WIDGET

# initial tests

def test_plot_widget_attribute(plot_widget: Frame_rate_Widget):
    assert plot_widget.frame_x_axis_time == True

def test_add_time_widget_frame(plot_widget_after_load_tif: Frame_rate_Widget):
        assert plot_widget_after_load_tif.image_path != None,'path Attribute not updated from None'
        assert plot_widget_after_load_tif.time_data != None,'time Attribute not updated from None'

def test_plot_widget_open_image(plot_widget_after_load_tif: Frame_rate_Widget):
    assert plot_widget_after_load_tif.image_path != None, 'path Attribute not loaded'


# test init after timer

def test_init_after_imer(plot_widget_after_load_tif: Frame_rate_Widget):
    ftime = MagicMock()
    plot_widget_after_load_tif.timer = ftime
    plot_widget_after_load_tif.init_after_timer()
    plot_widget_after_load_tif.timer.start.assert_called_with(plot_widget_after_load_tif.Twait)

# test get frame rate

def test_update_widget(plot_widget_after_load_tif: Frame_rate_Widget):
    evv = MagicMock()
    evv.source = []
    vieww = MagicMock()
    plot_widget_after_load_tif._viewer=vieww
    plot_widget_after_load_tif.update_widget(evv)
    plot_widget_after_load_tif._viewer.window.remove_dock_widget.assert_called()
    assert plot_widget_after_load_tif.image_path == None


######### General functions

def test_connect_eda():
    widi = MagicMock()
    widi.image_path = '/aaaaaa'
    connect_eda(widi)
    widi._viewer.open.assert_called_with('/EDA', plugin = "napari-ome-zarr")

def test_get_times_tif(plot_widget_after_load_tif: Frame_rate_Widget):
    assert len(plot_widget_after_load_tif.time_data) == 20

def test_get_times_ngff(plot_widget_after_load_ngff: Frame_rate_Widget):
    assert len(plot_widget_after_load_ngff.time_data) == 50