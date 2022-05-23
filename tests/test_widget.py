"""
test module eda-napari.
"""
from tkinter import E
from eda_napari._widget import Frame_rate_Widget, Add_time_scroller
import pytest
from qtpy.QtCore import Qt, QTimer
#import time


#####Fixtures#####
@pytest.fixture
def plot_widget(make_napari_viewer):  #creates Frame_rate_Widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_after_load(make_napari_viewer):  #creates Frame_rate_Widget for the viewer loads data then return the widget
    viewer = make_napari_viewer(show=False)
    Frame_rate_Widget(viewer)
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")

    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def plot_widget_loaded(make_napari_viewer): #loads image to viewer then creates widget
    viewer = make_napari_viewer(show=False)
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    yield Frame_rate_Widget(viewer) 

@pytest.fixture
def time_widget(make_napari_viewer): #creates Add_time_scroller_widget for the viewer
    viewer = make_napari_viewer(show=False)
    yield Add_time_scroller(viewer) 

@pytest.fixture
def time_widget_loaded(make_napari_viewer): #loads image to viewer then creates widget
    viewer = make_napari_viewer(show=False)
    viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    yield Add_time_scroller(viewer) 

#######TESTS########
def test_plot_widget_attribute(plot_widget: Frame_rate_Widget):
    assert plot_widget.frame_x_axis_time == True

def test_time_widget_attribute(time_widget: Add_time_scroller):
    assert time_widget.channel==0 , "channel attribute doesn't init with 0"

def test_time_widget_open_image(time_widget: Add_time_scroller):
    assert time_widget.image_path == None, 'path Attribute no init with None'
    time_widget._viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    assert  time_widget.image_path != None,'path Attribute not updated from None'
    assert  time_widget.time_data != None,'time Attribute not updated from None'

def test_add_time_widget(time_widget_loaded: Add_time_scroller):
        assert plot_widget.image_path != None,'path Attribute not updated from None'
        assert  time_widget_loaded.time_data != None,'time Attribute not updated from None'

def test_add_time_widget(time_widget_loaded: Frame_rate_Widget):
        assert time_widget_loaded.image_path != None,'path Attribute not updated from None'
        assert time_widget_loaded.time_data != None,'time Attribute not updated from None'

def test_plot_widget_open_image(plot_widget_after_load: Frame_rate_Widget):
    assert plot_widget_after_load.image_path != None, 'path Attribute not loaded'
