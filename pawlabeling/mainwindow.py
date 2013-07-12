#-----------------------------------------------------------------------------
# Copyright (c) 2013, Paw Labeling Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *
from settings import configuration
from functions import gui
from widgets import processingwidget, analysiswidget

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(configuration.main_window_size)

        self.processing_widget = processingwidget.ProcessingWidget(self)
        self.analysis_widget = analysiswidget.AnalysisWidget(self)

        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self.setWindowTitle("Paw Labeling tool")

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.processing_widget, "Processing")
        self.tab_widget.addTab(self.analysis_widget, "Analysis")

        self.setCentralWidget(self.tab_widget)

        # Load all the measurements into the measurement tree
        self.processing_widget.add_measurements()
        # Then load the first measurement
        self.processing_widget.load_first_file()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    app.exec_()


if __name__ == "__main__":
    main()










            
