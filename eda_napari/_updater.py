from importlib.resources import read_text

import os
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox, QLineEdit
from qtpy.QtCore import  QTimer
import time
import ome_zarr
import ome_zarr.reader
import napari
import collections


label_style = read_text("eda_napari", "q_label_stylesheet.qss")

class Zarr_update_widget(QWidget):
   """Widget that updates the data in Zarr storages at a specificied rate."""

   def __init__(self, napari_viewer: napari.Viewer):
      """Construct the widget to display."""
      super().__init__()
      self._viewer = napari_viewer
      self.layout=QVBoxLayout(self)
      self.update_check = QCheckBox("Update data")
      self.update_check.setChecked(False)
      self.update_check.stateChanged.connect(self.update_check_changed)
      self.interval_label = QLabel("Update Interval [s]")
      self.update_interval = QLineEdit('10')
      self.update_interval.editingFinished.connect(self.update_interval_value)
      self.update_button = QPushButton("Update now")
      self.update_button.clicked.connect(self.update)
      self.layout.addWidget(self.update_check)
      self.layout.addWidget(self.interval_label)
      self.layout.addWidget(self.update_interval)
      self.layout.addWidget(self.update_button)

      self.layers_to_update = collections.defaultdict()
      self.current_sources = collections.defaultdict(lambda: collections.defaultdict(list))

      self._viewer.layers.events.inserted.connect(self.add_source)
      self._viewer.layers.events.removing.connect(self.remove_layer)

      self.setMaximumHeight(200)

      self.timer=QTimer()
      self.timer.setInterval(10_000)
      self.timer.timeout.connect(self.update)

   def add_source(self, layer):
      reader = ome_zarr.reader.Reader(ome_zarr.io.parse_url(layer.source[-1].source.path))
      self.current_sources[layer.source[-1].source.path]['reader'] = reader
      self.current_sources[layer.source[-1].source.path]['layers'].append(layer.source[-1].name)
      if all([os.path.exists(
         os.path.join(os.path.dirname(layer.source[-1].source.path), "EDA", "nn_images")),
              "EDA" not in [layer.name for layer in self._viewer.layers]]):
         self._viewer.open(
            os.path.join(os.path.dirname(layer.source[-1].source.path), "EDA"),
            plugin='napari-ome-zarr', blending='additive', colormap='viridis')
      print(self.current_sources)

   def update(self):
      if self.update_check.isChecked():
         t0 = time.perf_counter()
         for path, source in self.current_sources.items():
            for channel, layer in enumerate(source['layers']):
               self._viewer.layers[layer].data = list(source['reader']())[0].data[0][:, channel, :, :, :]
         print(time.perf_counter() - t0)

   def update_interval_value(self):
      """Number changed in the GUI. Update the QTimer"""
      self.timer.stop()
      self.timer.setInterval(int(self.update_interval.text())*1000)
      self.timer.start()

   def update_check_changed(self):
      print(self.timer.isActive())
      if self.timer.isActive():
         self.timer.stop()
      else:
         self.timer.start()

   def remove_layer(self, layer):
      print(layer)
      self.current_sources[layer.source[layer.index].source.path]['layers'].remove(layer.source[layer.index].name)
      # Check if list is empty and delete source completely
      if not self.current_sources[layer.source[layer.index].source.path]['layers']:
         del self.current_sources[layer.source[layer.index].source.path]
