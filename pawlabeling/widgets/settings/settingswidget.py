import sys
import os
from PySide import QtGui, QtCore
from pubsub import pub
from pawlabeling.settings import configuration
from pawlabeling.functions import gui


class SettingsWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)

        # Set up the logger
        self.logger = configuration.setup_logging()

        self.toolbar = gui.Toolbar(self)

        self.settings_label = QtGui.QLabel("Settings")
        self.settings_label.setFont(configuration.label_font)

        self.measurement_folder_label = QtGui.QLabel("Measurements folder")
        self.measurement_folder = QtGui.QLineEdit()
        self.measurement_folder.setText(configuration.measurement_folder)
        self.measurement_folder_button = QtGui.QToolButton()
        self.measurement_folder_button.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                        "../images/folder_icon.png")))
        self.measurement_folder_button.clicked.connect(self.change_measurement_folder)

        self.database_folder_label = QtGui.QLabel("Database folder")
        self.database_folder = QtGui.QLineEdit()
        self.database_folder.setText(configuration.database_folder)
        self.database_folder_button = QtGui.QToolButton()
        self.database_folder_button.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                        "../images/folder_icon.png")))
        self.database_folder_button.clicked.connect(self.change_database_folder)


        self.database_file_label = QtGui.QLabel("Database file")
        self.database_file = QtGui.QLineEdit()
        self.database_file.setText(configuration.database_file)

        self.left_front_label = QtGui.QLabel("Left Front Shortcut")
        self.left_front = QtGui.QLineEdit()
        self.left_front.setText(configuration.left_front.toString())

        self.left_hind_label = QtGui.QLabel("Left Hind Shortcut")
        self.left_hind = QtGui.QLineEdit()
        self.left_hind.setText(configuration.left_hind.toString())

        self.right_front_label = QtGui.QLabel("Right Front Shortcut")
        self.right_front = QtGui.QLineEdit()
        self.right_front.setText(configuration.right_front.toString())

        self.right_hind_label = QtGui.QLabel("Right Hind Shortcut")
        self.right_hind = QtGui.QLineEdit()
        self.right_hind.setText(configuration.right_hind.toString())

        self.interpolation_entire_plate_label = QtGui.QLabel("Interpolation: Entire Plate")
        self.interpolation_entire_plate = QtGui.QLineEdit()
        self.interpolation_entire_plate.setText(str(configuration.interpolation_entire_plate))

        self.interpolation_contact_widgets_label = QtGui.QLabel("Interpolation: Contact Widgets")
        self.interpolation_contact_widgets = QtGui.QLineEdit()
        self.interpolation_contact_widgets.setText(str(configuration.interpolation_contact_widgets))

        self.interpolation_results_label = QtGui.QLabel("Interpolation: Results")
        self.interpolation_results  = QtGui.QLineEdit()
        self.interpolation_results.setText(str(configuration.interpolation_results))


        self.widgets = [["measurement_folder_label","measurement_folder", "measurement_folder_button"],
                        ["database_folder_label", "database_folder", "database_folder_button"],
                        ["database_file_label", "database_file"],
                        ["left_front_label", "left_front", "", "right_front_label", "right_front"],
                        ["left_hind_label", "left_hind", "", "right_hind_label", "right_hind"],
                        ["interpolation_entire_plate_label", "interpolation_entire_plate", "",
                        "interpolation_contact_widgets_label", "interpolation_contact_widgets", "",
                        "interpolation_results_label", "interpolation_results"]
        ]

        self.settings_layout = QtGui.QGridLayout()
        self.settings_layout.setSpacing(10)

        # This neatly fills the QGridLayout for us
        for row, widgets in enumerate(self.widgets):
            for column, widget_name in enumerate(widgets):
                if widget_name:
                    widget = getattr(self, widget_name)
                    self.settings_layout.addWidget(widget, row, column)


        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.settings_label)
        bar_1 = QtGui.QFrame(self)
        bar_1.setFrameShape(QtGui.QFrame.Shape.HLine)
        self.main_layout.addWidget(bar_1)
        self.main_layout.addLayout(self.settings_layout)

        self.setLayout(self.main_layout)

        #pub.subscribe(self.change_status, "update_statusbar")
        #pub.subscribe(self.launch_message_box, "message_box")

    # TODO: changes here should propagate to the rest of the application (like the database screen)
    # So make sure things update if a relevant thing changes
    def save_settings(self, evt=None):
        """
        Store the changes to the widgets to the config.yaml file
        This function should probably do some validation
        """
        pass

    def change_measurement_folder(self, evt=None):
        # Open a file dialog
        self.file_dialog = QtGui.QFileDialog(self,
                                             "Select the folder containing your measurements",
                                             configuration.measurement_folder)

        self.file_dialog.setFileMode(QtGui.QFileDialog.Directory)
        #self.file_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        self.file_dialog.setViewMode(QtGui.QFileDialog.Detail)

        # Store the default in case we don't make a change
        folder = self.measurement_folder.text()
        # Change where configuration.measurement_folder is pointing too
        if self.file_dialog.exec_():
            folder = self.file_dialog.selectedFiles()[0]

        # Then change that, so we always keep our 'default' measurements_folder
        configuration.measurement_folder = folder
        self.measurement_folder.setText(folder)

    def change_database_folder(self, evt=None):
        # Open a file dialog
        self.file_dialog = QtGui.QFileDialog(self,
                                             "Select the folder containing your database",
                                             configuration.database_folder)

        self.file_dialog.setFileMode(QtGui.QFileDialog.Directory)
        self.file_dialog.setViewMode(QtGui.QFileDialog.Detail)

        # Store the default in case we don't make a change
        folder = self.database_folder.text()
        # Change where configuration.measurement_folder is pointing too
        if self.file_dialog.exec_():
            folder = self.file_dialog.selectedFiles()[0]

        # Then change that, so we always keep our 'default' measurements_folder
        configuration.database_folder = folder
        self.database_folder.setText(folder)


    def create_toolbar_actions(self):
        self.save_settings_action = gui.create_action(text="&Save Settings",
                                                        shortcut=QtGui.QKeySequence("CTRL+S"),
                                                        icon=QtGui.QIcon(
                                                            os.path.join(os.path.dirname(__file__),
                                                                         "../images/save_icon.png")),
                                                        tip="Save settings",
                                                        checkable=True,
                                                        connection=self.save_settings
        )

        self.actions = [self.save_settings_action]

        for action in self.actions:
            self.toolbar.addAction(action)