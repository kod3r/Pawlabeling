#-----------------------------------------------------------------------------
# Copyright (c) 2013, Paw Labeling Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

from PySide.QtCore import *
from PySide.QtGui import *
import utility


class EntirePlateWidget(QWidget):
    def __init__(self, degree, size, parent=None):
        super(EntirePlateWidget, self).__init__(parent)
        self.parent = parent
        self.resize(size[0], size[1])
        self.layout = QVBoxLayout(self)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)
        self.image = QGraphicsPixmapItem()
        self.scene.addItem(self.image)

        # This pen is used to draw the polygons
        self.pen = QPen(Qt.white)
        # I can also draw with a brush
        self.brush = QBrush(Qt.white)
        # A cache to store the polygons of the previous frame
        self.previous_polygons = []
        self.bounding_boxes = []
        self.current_box = None
        self.gait_lines = []
        self.colors = [
            QColor(Qt.green),
            QColor(Qt.darkGreen),
            QColor(Qt.red),
            QColor(Qt.darkRed),
            QColor(Qt.gray),
            QColor(Qt.white),
            QColor(Qt.yellow),
        ]

        self.degree = degree
        self.image_color_table = utility.ImageColorTable()
        self.color_table = self.image_color_table.create_color_table()

    def new_measurement(self, measurement):
        # Clear the bounding boxes + the line
        self.clear_bounding_box()
        self.clear_gait_line()
        # Update the measurement
        self.measurement = measurement
        self.height, self.width, self.numFrames = self.measurement.shape
        self.n_max = self.measurement.max()
        self.change_frame(frame=-1)
        #self.cop_x, self.cop_y = utility.calculate_cop(self.measurement)

    def new_paws(self, paws):
        # Update the paws
        self.paws = paws

    def change_frame(self, frame):
        # Set the frame
        self.frame = frame
        if frame == -1:
            self.data = self.measurement.max(axis=2).T
        else:
            # Slice out the data from the measurement
            self.data = self.measurement[:, :, self.frame].T
            # Update the pixmap
        self.image.setPixmap(utility.get_QPixmap(self.data, self.degree, self.n_max, self.color_table))

    def clear_bounding_box(self):
        # Remove the old ones and redraw
        for box in self.bounding_boxes:
            self.scene.removeItem(box)
        self.bounding_boxes = []

    def clear_gait_line(self):
        # Remove the gait line
        for line in self.gait_lines:
            self.scene.removeItem(line)
        self.gait_lines = []

    def draw_bounding_box(self, paw, paw_label):
        color = self.colors[paw_label]
        self.bounding_box_pen = QPen(color)
        self.bounding_box_pen.setWidth(3)

        if paw_label == -1:
            current_paw = 0.5
        else:
            current_paw = 0

        polygon = QPolygonF(
            [QPointF((paw.total_min_x - current_paw) * self.degree, (paw.total_min_y - current_paw) * self.degree),
             QPointF((paw.total_max_x + current_paw) * self.degree, (paw.total_min_y - current_paw) * self.degree),
             QPointF((paw.total_max_x + current_paw) * self.degree, (paw.total_max_y + current_paw) * self.degree),
             QPointF((paw.total_min_x - current_paw) * self.degree, (paw.total_max_y + current_paw) * self.degree)])

        self.bounding_boxes.append(self.scene.addPolygon(polygon, self.bounding_box_pen))

    def update_bounding_boxes(self, paw_labels, current_paw_index):
        self.clear_bounding_box()

        for index, paw_label in paw_labels.items():
            # Mark unlabeled paws white if they're not the current paw
            #if index != current_paw_index and paw_label == -1:
            #    paw_label = -2

            self.draw_bounding_box(self.paws[index], paw_label)
            if current_paw_index == index:
                self.draw_bounding_box(self.paws[index], paw_label=-1)


    def draw_gait_line(self):
        self.gait_line_pen = QPen(Qt.white)
        self.gait_line_pen.setWidth(2)
        self.gait_line_pen.setColor(Qt.white)

        self.clear_gait_line()

        for index in range(1, len(self.paws)):
            prevPaw = self.paws[index - 1]
            curPaw = self.paws[index]
            polygon = QPolygonF(
                [QPointF(prevPaw.total_centroid[0] * self.degree, prevPaw.total_centroid[1] * self.degree),
                 QPointF(curPaw.total_centroid[0] * self.degree, curPaw.total_centroid[1] * self.degree)])
            self.gait_lines.append(self.scene.addPolygon(polygon, self.gait_line_pen))

            # It seems that COP is really a poor indicator in most cases, unless perhaps I can use the shape
            # points = []
            # for cop_x, cop_y in zip(self.cop_x, self.cop_y):
            #     points.append(QPointF(cop_y * self.degree, cop_x * self.degree))
            #
            # polygon = QPolygonF(points)
            # self.gait_lines.append(self.scene.addPolygon(polygon, self.gait_line_pen))




