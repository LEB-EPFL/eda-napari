"""
test module eda-napari.
"""
from tkinter import E
from eda_napari._widget import Frame_rate_Widget, Time_scroller_widget
import pytest
import os
#import time

test_image_path= str(os.path.dirname(os.path.dirname(__file__)))+'/images/example_image.tif'

#####Fixtures#####
@pytest.fixture
def plot_widget(make_napari_viewer):  #creates Frame_rate_Widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_after_load(make_napari_viewer):  #creates Frame_rate_Widget for the viewer loads data then return the widget
    viewer = make_napari_viewer(show=False)
    Frame_rate_Widget(viewer)
    viewer.open(test_image_path)

    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_loaded(make_napari_viewer): #loads image to viewer then creates widget
    viewer = make_napari_viewer(show=False)
    viewer.open(test_image_path)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def time_widget(make_napari_viewer): #creates Time_scroller_widget_widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Time_scroller_widget(viewer) 

@pytest.fixture
def time_widget_loaded(make_napari_viewer): #loads image to viewer then creates widget
    viewer = make_napari_viewer(show=False)
    viewer.open(test_image_path)
    yield Time_scroller_widget(viewer) 

#######TESTS########
def test_plot_widget_attribute(plot_widget: Frame_rate_Widget):
    assert plot_widget.frame_x_axis_time == True

def test_time_widget_attribute(time_widget: Time_scroller_widget):
    assert time_widget.channel==0 , "channel attribute doesn't init with 0"

def test_time_widget_open_image(time_widget: Time_scroller_widget):
    assert time_widget.image_path == None, 'path Attribute no init with None'
    time_widget._viewer.open(test_image_path)
    assert  time_widget.image_path != None,'path Attribute not updated from None'
    assert  time_widget.time_data != None,'time Attribute not updated from None'

def test_add_time_widget(time_widget_loaded: Time_scroller_widget):
        assert plot_widget.image_path != None,'path Attribute not updated from None'
        assert  time_widget_loaded.time_data != None,'time Attribute not updated from None'

def test_add_time_widget(time_widget_loaded: Frame_rate_Widget):
        assert time_widget_loaded.image_path != None,'path Attribute not updated from None'
        assert time_widget_loaded.time_data != None,'time Attribute not updated from None'

def test_plot_widget_open_image(plot_widget_after_load: Frame_rate_Widget):
    assert plot_widget_after_load.image_path != None, 'path Attribute not loaded'
