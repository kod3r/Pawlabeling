import sys, os

from mainwidget import MainWidget
import utility
from PyQt4.QtCore import *
from PyQt4.QtGui import *

base_folder = "C:\Dropbox\Public\Examples\\"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        desktop = True
        if desktop:
            # Set the size to something nice and large
            self.setGeometry(QRect(0, 25, 2250, 1000))
        else:
            self.setGeometry(QRect(0, 25, 1400, 800))

        path = "C:\\Exports\\"
        store_path = "C:\\LabelsStored\\"
        # Add the folder for the store_path data if it doesn't exist
        if not os.path.exists(store_path):
            os.mkdir(store_path)

        self.main_widget = MainWidget(path, store_path, desktop, self)
        self.setCentralWidget(self.main_widget)
        self.toolbar = Toolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self.setWindowTitle("Paw labeling tool")

        self.track_contacts = self.create_action(text="&Track Contacts",
                                                shortcut="CTRL+F",
                                                icon=QIcon(
                                                    os.path.join(os.path.dirname(__file__), "images/editzoom.png")),
                                                tip="Using the tracker to find contacts",
                                                checkable=False,
                                                connection=self.main_widget.track_contacts
        )

        self.store_status = self.create_action(text="&Store",
                                              shortcut="CTRL+S",
                                              icon=QIcon(
                                                  os.path.join(os.path.dirname(__file__), "images/save-icon.png")),
                                              tip="Mark the tracking as correct",
                                              checkable=False,
                                              connection=self.main_widget.store_status
        )

        self.slide_to_left = self.create_action(text="Slide Left",
                                            shortcut=Qt.Key_Left,
                                            icon=QIcon(
                                                os.path.join(os.path.dirname(__file__), "images/arrow-left-icon.png")),
                                            tip="Move the slider to the left",
                                            checkable=False,
                                            connection=self.main_widget.slide_to_left
        )

        self.slide_to_right = self.create_action(text="Slide Right",
                                             shortcut=Qt.Key_Right,
                                             icon=QIcon(os.path.join(os.path.dirname(__file__),
                                                                     "images/arrow-right-icon.png")),
                                             tip="Move the slider to the right",
                                             checkable=False,
                                             connection=self.main_widget.slide_to_right
        )

        self.fast_backward = self.create_action(text="Fast Back",
                                               shortcut=QKeySequence(Qt.CTRL + Qt.Key_Left),
                                               icon=QIcon(os.path.join(os.path.dirname(__file__),
                                                                       "images/arrow-left-icon.png")),
                                               tip="Move the slider to the left faster",
                                               checkable=False,
                                               connection=self.main_widget.fast_backward
        )

        self.fast_forward = self.create_action(text="Fast Left Right",
                                              shortcut=QKeySequence(Qt.CTRL + Qt.Key_Right),
                                              icon=QIcon(os.path.join(os.path.dirname(__file__),
                                                                      "images/arrow-right-icon.png")),
                                              tip="Move the slider to the right faster",
                                              checkable=False,
                                              connection=self.main_widget.fast_forward
        )

        self.front_left = self.create_action(text="Select Left Front",
                                             shortcut=QKeySequence(Qt.Key_7),
                                             icon=QIcon(os.path.join(os.path.dirname(__file__), "images/LF-icon.png")),
                                             tip="Select the Left Front paw",
                                             checkable=False,
                                             connection=self.main_widget.select_left_front
        )

        self.hind_left = self.create_action(text="Select Left Hind",
                                            shortcut=QKeySequence(Qt.Key_1),
                                            icon=QIcon(os.path.join(os.path.dirname(__file__), "images/LH-icon.png")),
                                            tip="Select the Left Hind paw",
                                            checkable=False,
                                            connection=self.main_widget.select_left_hind
        )

        self.front_right = self.create_action(text="Select Right Front",
                                              shortcut=QKeySequence(Qt.Key_9),
                                              icon=QIcon(os.path.join(os.path.dirname(__file__), "images/RF-icon.png")),
                                              tip="Select the Right Front paw",
                                              checkable=False,
                                              connection=self.main_widget.select_right_front
        )

        self.hind_right = self.create_action(text="Select Right Hind",
                                             shortcut=QKeySequence(Qt.Key_3),
                                             icon=QIcon(os.path.join(os.path.dirname(__file__), "images/RH-icon.png")),
                                             tip="Select the Right Hind paw",
                                             checkable=False,
                                             connection=self.main_widget.select_right_hind
        )

        self.previous_paw = self.create_action(text="Select Previous Paw",
                                               shortcut=[QKeySequence(Qt.Key_4), Qt.Key_Down],
                                               icon=QIcon(
                                                   os.path.join(os.path.dirname(__file__), "images/backward.png")),
                                               tip="Select the previous paw",
                                               checkable=False,
                                               connection=self.main_widget.previous_paw
        )

        self.next_paw = self.create_action(text="Select Next Paw",
                                           shortcut=[QKeySequence(Qt.Key_6), Qt.Key_Up],
                                           icon=QIcon(os.path.join(os.path.dirname(__file__), "images/forward.png")),
                                           tip="Select the next paw",
                                           checkable=False,
                                           connection=self.main_widget.next_paw
        )

        self.delete_label = self.create_action(text="Delete Label From Paw",
                                               shortcut=Qt.Key_5,
                                               icon=QIcon(
                                                   os.path.join(os.path.dirname(__file__), "images/cancel-icon.png")),
                                               tip="Delete the label from the paw",
                                               checkable=False,
                                               connection=self.main_widget.delete_label
        )

        self.invalid_paw = self.create_action(text="Mark Paw as Invalid",
                                              shortcut=Qt.Key_Delete,
                                              icon=QIcon(
                                                  os.path.join(os.path.dirname(__file__), "images/trash-icon.png")),
                                              tip="Mark the paw as invalid",
                                              checkable=False,
                                              connection=self.main_widget.invalid_paw
        )

        self.undo_label = self.create_action(text="Undo Label From Paw",
                                             shortcut=QKeySequence(Qt.CTRL + Qt.Key_Z),
                                             icon=QIcon(
                                                 os.path.join(os.path.dirname(__file__), "images/undo-icon.png")),
                                             tip="Delete the label from the paw",
                                             checkable=False,
                                             connection=self.main_widget.undo_label
        )

        self.actions = [self.store_status, self.track_contacts, self.front_left, self.hind_left,
                        self.front_right, self.hind_right, self.previous_paw, self.next_paw,
                        self.delete_label, self.invalid_paw, self.undo_label]

        for action in self.actions:
            action.setShortcutContext(Qt.ApplicationShortcut)
            self.toolbar.addAction(action)

        # Not adding the forward/backward buttons to the toolbar
        self.non_toolbar_actions = [self.slide_to_left, self.slide_to_right, self.fast_backward, self.fast_forward]
        for action in self.non_toolbar_actions:
            action.setShortcutContext(Qt.ApplicationShortcut)

        # Install an event filter
        self.arrowFilter = utility.arrow_filter()
        self.installEventFilter(self.arrowFilter)

        self.main_widget.load_file(event=None)


    def create_action(self, text, shortcut=None, icon=None,
                      tip=None, checkable=False, connection=None):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(icon)
        if shortcut is not None:
            if type(shortcut) == list:
                action.setShortcuts(shortcut)
            else:
                action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)
        if connection:
            action.triggered.connect(connection)
        return action


class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super(Toolbar, self).__init__(parent)
        # I don't want to see it floating
        self.setFloatable(False)
        # I don't want it moved
        self.setMovable(False)
        # I want nice and big icons
        self.setIconSize(QSize(50, 50))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    app.exec_()










            
