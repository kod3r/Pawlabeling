from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import utility

class PawsWidget(QWidget):
    def __init__(self, parent, degree, nmin, nmax):
        super(PawsWidget, self).__init__(parent)
        self.parent = parent
        self.degree = degree

        self.left_front = PawWidget(self, degree, nmin, nmax)
        self.left_hind = PawWidget(self, degree, nmin, nmax)
        self.right_front = PawWidget(self, degree, nmin, nmax)
        self.right_hind = PawWidget(self, degree, nmin, nmax)
        self.current_paw = PawWidget(self, degree, nmin, nmax)

        self.paws_list = [self.left_front, self.left_hind,
                          self.right_front, self.right_hind,
                          self.current_paw]
        # This sets every widget to a zero image and initializes paws
        self.clear_paws()

        self.left_paws_layout = QVBoxLayout()
        self.left_paws_layout.addWidget(self.left_front)
        self.left_paws_layout.addWidget(self.left_hind)
        self.current_paw_layout = QVBoxLayout()
        self.current_paw_layout.addWidget(self.current_paw)
        self.right_paws_layout = QVBoxLayout()
        self.right_paws_layout.addWidget(self.right_front)
        self.right_paws_layout.addWidget(self.right_hind)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.left_paws_layout)
        self.mainLayout.addLayout(self.current_paw_layout)
        self.mainLayout.addLayout(self.right_paws_layout)
        self.setLayout(self.mainLayout)

    def update_current_paw(self, data, paw_label, index):
        # Make sure that each paw is only mapped to exactly one paw
        self.paws[index] = (paw_label, data)
        data_list = []
        for index, item in self.paws.items():
            label, data = item
            if label == paw_label:
                data_list.append(data.mean(axis=2))
        widget = self.paws_list[paw_label]
        widget.update(data_list)

    def clear_paws(self):
        self.paws = {}
        for paw in self.paws_list:
            paw.clear_paws()


class PawWidget(QWidget):
    def __init__(self, parent, degree, nmin, nmax):
        super(PawWidget, self).__init__(parent)
        self.parent = parent
        self.degree = degree
        self.nmin = nmin
        self.nmax = nmax

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.image = QGraphicsPixmapItem()
        self.scene.addItem(self.image)
        self.view.centerOn(self.image)

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.addWidget(self.view)
        self.setLayout(self.mainLayout)

    def update(self, data_list):
        # Calculate an average paw from the list of arrays
        data = utility.averagecontacts(data_list)
        self.data = np.rot90(np.rot90(data))
        self.image.setPixmap(utility.getQPixmap(self.data, self.degree, self.nmin, self.nmax))

    def clear_paws(self):
        self.data = None
        # Put the screen to black
        self.image.setPixmap(utility.getQPixmap(np.zeros((30,30)), self.degree, self.nmin, self.nmax))