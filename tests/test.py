"""
test module eda-napari.
"""
from eda_napari._widget import Frame_rate_Widget
import numpy as np


# fixture for LayerSelector class tests
@pytest.fixture
def widget(make_napari_viewer):
    _sync = None
    viewer = make_napari_viewer(show=False)
    yield Frame_rate_Widget(viewer)

# test fixtures
def test_widget(widget: Frame_rate_Widget):
    assert widget.frame_x_axis_time == True


