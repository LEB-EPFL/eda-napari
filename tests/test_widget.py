"""
test module eda-napari.
"""
from eda_napari._widget import Frame_rate_Widget
import numpy as np
import pytest


# fixture for Frame_rate_widget class tests
@pytest.fixture
def widget(make_napari_viewer):
    viewer = make_napari_viewer(show=False)
    yield Frame_rate_Widget(viewer)

# test fixtures
def test_widget_attribute(widget: Frame_rate_Widget):
    assert widget.frame_x_axis_time == True

def test_path(widget: Frame_rate_Widget):
    #check no initial path
    assert widget.image_path == None, 'path Attribute no init with None'
    widget._viewer.open("/Users/stevenbrown/software/images/napari_example2/steven_2_MMStack_Pos0.ome.tif")
    assert widget.image_path != None,'path Attribute not updated from None'
    print('Image path = '+ widget.image_path )
   
