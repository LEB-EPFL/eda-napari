

import npe2
from test_widget import test_image_ngff_path
from eda_napari._updater import Zarr_update_widget
import time
import pytest


@pytest.fixture
def updater_after_ngff_load(make_napari_viewer):  #creates Frame_rate_Widget for the viewer loads data then return the widget
    viewer = make_napari_viewer(show=False)
    pm = npe2.PluginManager.instance()
    pm.discover(include_npe1=True)
    pm.index_npe1_adapters()
    my_widget = Zarr_update_widget(viewer)
    viewer.open(test_image_ngff_path, plugin='napari-ome-zarr')
    time.sleep(4)
    yield my_widget


def test_updater_channels(updater_after_ngff_load):
    assert len(updater_after_ngff_load._viewer.layers) == 3
    for i in range(3):
        updater_after_ngff_load._viewer.layers.pop(0)
        time.sleep(0.5)
    assert len(updater_after_ngff_load._viewer.layers) == 0