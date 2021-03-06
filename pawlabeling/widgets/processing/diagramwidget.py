import logging
from collections import defaultdict
import numpy as np
from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pubsub import pub
from ...functions import utility
from ...settings import settings
from ...models import model


class DiagramWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(DiagramWidget, self).__init__(parent)
        self.label = QtGui.QLabel("Gait Diagram")
        self.parent = parent
        self.active = False

        self.diagram = DiagramView(self, "Gait Diagram")

        self.gait_diagram_layout = QtGui.QVBoxLayout()
        self.gait_diagram_layout.addWidget(self.diagram)

        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.gait_diagram_layout)
        self.setLayout(self.main_layout)

        pub.subscribe(self.change_frame, "processing.change_frame")
        pub.subscribe(self.active_widget, "active_widget")

    def change_frame(self, frame):
        self.diagram.change_frame(frame)

    def active_widget(self, widget):
        self.active = False
        if self == widget:
            self.active = True
            progress = 0
            pub.sendMessage("update_progress", progress=progress)
            self.diagram.draw()
            pub.sendMessage("update_progress", progress=100)


class DiagramView(QtGui.QWidget):
    def __init__(self, parent, label):
        super(DiagramView, self).__init__(parent)
        self.label = QtGui.QLabel(label)
        self.parent = parent
        self.model = model.model
        self.degree = settings.settings.interpolation_results()
        self.colors = settings.settings.colors
        self.image_color_table = utility.ImageColorTable()
        self.color_table = self.image_color_table.create_color_table()

        self.frame = -1
        self.length = 0
        self.ratio = 1

        self.dpi = 100
        # This figsize may not always work out!
        self.fig = Figure(dpi=self.dpi) # figsize=(10.0, 5.0)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)

        self.vertical_line = self.axes.axvline(linewidth=4, color='r')
        self.vertical_line.set_xdata(0)

        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.canvas, stretch=3)
        self.setLayout(self.main_layout)

        pub.subscribe(self.draw, "put_measurement")
        pub.subscribe(self.draw, "update_current_contact")
        pub.subscribe(self.clear_cached_values, "clear_cached_values")

    def draw(self):
        self.clear_cached_values()
        self.update_gait_diagram()

    def update_gait_diagram(self):
        if not self.model.contacts:
            return

        self.clear_axes()
        na = False

        for contact in self.model.contacts[self.model.measurement_name]:
            min_z = contact.min_z
            length = contact.length

            contact_label = contact.contact_label
            if contact_label < 0:
                if settings.__human__:
                    contact_label = 2
                else:
                    contact_label = 4
                na = True

            self.axes.barh(bottom=contact_label, left=float(min_z), width=length, height=0.5,
                           align='center', color=settings.settings.matplotlib_color[contact_label])

        self.length = self.model.measurement.number_of_frames
        self.axes.set_xlim([0, self.length])
        if na:
            if settings.__human__:
                self.axes.set_yticks(range(0, 2))
                self.axes.set_yticklabels(['Left', 'Right', 'NA'])
            else:
                self.axes.set_yticks(range(0, 5))
                self.axes.set_yticklabels(['Left Front', 'Left Hind', 'Right Front', 'Right Hind', 'NA'])
        else:

            if settings.__human__:
                self.axes.set_yticks(range(0, 2))
                self.axes.set_yticklabels(['Left', 'Right'])
            else:
                self.axes.set_yticks(range(0, 4))
                self.axes.set_yticklabels(['Left Front', 'Left Hind', 'Right Front', 'Right Hind'])
        self.axes.set_xlabel('Frames Since Beginning of Measurement')
        self.axes.yaxis.grid(True)
        self.axes.set_title('Periods of Contacts')

        self.vertical_line = self.axes.axvline(linewidth=4, color='r')
        self.vertical_line.set_xdata(self.frame)
        self.canvas.draw()

    def change_frame(self, frame):
        self.frame = frame
        if self.frame < self.length:
            self.vertical_line.set_xdata(self.frame)
            self.canvas.draw_idle()

    def clear_axes(self):
        self.axes.cla()
        self.canvas.draw()

    def clear_cached_values(self):
        self.clear_axes()
        self.frame = -1
