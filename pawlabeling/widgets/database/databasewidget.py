import os
import logging
from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from pubsub import pub
from ...functions import io, gui
from ...widgets.database import subjectwidget, sessionwidget, measurementwidget


class DatabaseWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseWidget, self).__init__(parent)

        self.toolbar = gui.Toolbar(self)

        self.subject_widget = subjectwidget.SubjectWidget(self)
        self.session_widget = sessionwidget.SessionWidget(self)
        self.measurement_widget = measurementwidget.MeasurementWidget(self)
        # Create all the toolbar actions
        self.create_toolbar_actions()

        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.addWidget(self.subject_widget)
        self.horizontal_layout.addWidget(self.session_widget)
        self.horizontal_layout.addWidget(self.measurement_widget)

        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addLayout(self.horizontal_layout)
        self.setLayout(self.main_layout)

    def create_toolbar_actions(self):
        self.something_action = gui.create_action(text="&Something",
                                                  shortcut=QtGui.QKeySequence("CTRL+F"),
                                                  icon=QtGui.QIcon(
                                                      os.path.join(os.path.dirname(__file__),
                                                                   "../images/edit_zoom.png")),
                                                  tip="Search for subject",
                                                  checkable=False,
                                                  connection=self.subject_widget.get_subjects
        )

        self.clear_subject_fields_action = gui.create_action(text="&Clear",
                                                             shortcut=QtGui.QKeySequence("CTRL+Q"),
                                                             icon=QtGui.QIcon(
                                                                 os.path.join(os.path.dirname(__file__),
                                                                              "../images/clear_fields.png")),
                                                             tip="Clear all the subject text fields",
                                                             checkable=False,
                                                             connection=self.subject_widget.clear_subject_fields
        )

        self.create_subject_action = gui.create_action(text="&Create New Subject",
                                                       shortcut=QtGui.QKeySequence("CTRL+S"),
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/add_subject.png")),
                                                       tip="Create a new subject",
                                                       checkable=False,
                                                       connection=self.subject_widget.create_subject
        )

        self.create_session_action = gui.create_action(text="&Create New Session",
                                                       shortcut=QtGui.QKeySequence("CTRL+SHIFT+S"),
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/add_session.png")),
                                                       tip="Create a new session",
                                                       checkable=False,
                                                       connection=self.session_widget.create_session
        )

        self.add_measurements_action = gui.create_action(text="&Add Measurements",
                                                         shortcut=QtGui.QKeySequence("CTRL+V"),
                                                         icon=QtGui.QIcon(
                                                             os.path.join(os.path.dirname(__file__),
                                                                          "../images/add_measurement.png")),
                                                         tip="Add measurements to the session",
                                                         checkable=False,
                                                         connection=self.measurement_widget.add_measurements
        )

        self.delete_subject_action = gui.create_action(text="&Delete Subject",
                                                       shortcut=None,
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/delete_subject.png")),
                                                       tip="Delete Subject",
                                                       checkable=False,
                                                       connection=self.subject_widget.delete_subject
        )

        self.delete_session_action = gui.create_action(text="&Delete Session",
                                                       shortcut=None,
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/delete_session.png")),
                                                       tip="Delete Session",
                                                       checkable=False,
                                                       connection=self.session_widget.delete_session
        )

        self.delete_measurement_action = gui.create_action(text="&Delete Measurement",
                                                       shortcut=None,
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/delete_measurement.png")),
                                                       tip="Delete Measurement",
                                                       checkable=False,
                                                       connection=self.measurement_widget.delete_measurement
        )


        self.actions = [self.something_action, self.clear_subject_fields_action,
                        "separator",
                        self.create_subject_action, self.create_session_action, self.add_measurements_action,
                        "separator",
                        self.delete_subject_action, self.delete_session_action, self.delete_measurement_action]

        for action in self.actions:
            if action == "separator":
                self.toolbar.addSeparator()
            else:
                self.toolbar.addAction(action)


