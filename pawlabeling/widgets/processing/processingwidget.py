import os
from collections import defaultdict
import logging
import numpy as np
from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from pubsub import pub
from pawlabeling.functions import io, gui
from pawlabeling.settings import settings
from pawlabeling.widgets.processing import contactswidget
from pawlabeling.widgets.processing import entireplatewidget
from pawlabeling.models import model


class ProcessingWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ProcessingWidget, self).__init__(parent)

        self.logger = logging.getLogger("logger")
        self.model = model.model

        # Create a label to display the measurement name
        self.subject_name_label = QtGui.QLabel(self)
        self.session_name_label = QtGui.QLabel(self)
        self.measurement_name_label = QtGui.QLabel(self)

        self.label_layout = QtGui.QHBoxLayout()
        self.label_layout.addWidget(self.subject_name_label)
        self.label_layout.addWidget(self.session_name_label)
        self.label_layout.addWidget(self.measurement_name_label)
        self.label_layout.addStretch(1)

        self.settings = settings.settings
        self.colors = self.settings.colors()
        self.contact_dict = self.settings.contact_dict()

        self.toolbar = gui.Toolbar(self)
        # Create all the toolbar actions
        self.create_toolbar_actions()

        # Create a list widget
        self.measurement_tree = QtGui.QTreeWidget(self)
        self.measurement_tree.setMaximumWidth(300)
        self.measurement_tree.setMinimumWidth(300)
        #self.measurement_tree.setMaximumHeight(200)
        self.measurement_tree.setColumnCount(5)
        self.measurement_tree.setHeaderLabels(["Name", "Label", "Length", "Surface", "Force"])
        self.measurement_tree.itemActivated.connect(self.put_measurement)

        # Set the widths of the columns
        for column in xrange(self.measurement_tree.columnCount()):
            self.measurement_tree.setColumnWidth(column, 55)

        self.entire_plate_widget = entireplatewidget.EntirePlateWidget(self)
        self.entire_plate_widget.setMinimumWidth(self.settings.entire_plate_widget_width())
        self.entire_plate_widget.setMaximumHeight(self.settings.entire_plate_widget_height())

        self.contacts_widget = contactswidget.ContactWidgets(self)

        self.layout = QtGui.QVBoxLayout()
        self.layout.addLayout(self.label_layout)
        self.layout.addWidget(self.entire_plate_widget)
        self.layout.addWidget(self.contacts_widget)
        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.addWidget(self.measurement_tree)
        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addLayout(self.layout)
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addLayout(self.horizontal_layout)
        self.setLayout(self.main_layout)

        self.subscribe()
        pub.subscribe(self.clear_cached_values, "clear_cached_values")
        pub.subscribe(self.changed_settings, "changed_settings")
        pub.subscribe(self.put_subject, "put_subject")
        pub.subscribe(self.put_session, "put_session")

    # I've added subscribe/unsubscribe, such that when we're in the analysis tab, we don't want to respond to
    # everything it sends/receives
    def subscribe(self):
        pub.subscribe(self.update_measurements_tree, "update_measurement_status")
        pub.subscribe(self.stored_status, "stored_status")

    def unsubscribe(self):
        pub.unsubscribe(self.update_measurements_tree, "update_measurement_status")
        pub.unsubscribe(self.stored_status, "stored_status")

    def put_subject(self, subject):
        subject_name = "{} {}".format(subject.first_name, subject.last_name)
        self.subject_name_label.setText("Subject: {}\t".format(subject_name))

    def put_session(self, session):
        self.session_name_label.setText("Session: {}\t".format(session.session_name))

    def update_measurements_tree(self):
        self.measurement_tree.clear()
        # Create a green brush for coloring stored results
        green_brush = QtGui.QBrush(QtGui.QColor(46, 139, 87))

        for measurement in self.model.measurements.values():
            measurement_item = QtGui.QTreeWidgetItem(self.measurement_tree, [measurement])
            measurement_item.setText(0, measurement.measurement_name)
            measurement_item.setFirstColumnSpanned(True)
            measurement_item.setExpanded(True)
            for contact in self.model.contacts[measurement.measurement_name]:
                contact_item = QtGui.QTreeWidgetItem(measurement_item)
                contact_item.setText(0, str(contact.contact_id))
                contact_item.setText(1, self.contact_dict[contact.contact_label])
                contact_item.setText(2, str(contact.length))  # Sets the frame count
                max_surface = np.max(contact.surface_over_time)
                contact_item.setText(3, str(int(max_surface)))
                max_force = np.max(contact.force_over_time)
                contact_item.setText(4, str(int(max_force)))

                for idx in xrange(contact_item.columnCount()):
                    color = self.colors[contact.contact_label]
                    color.setAlphaF(0.5)
                    contact_item.setBackground(idx, color)

            # If several contacts have been labeled, marked the measurement
            if measurement.processed:
                for idx in xrange(measurement_item.columnCount()):
                    measurement_item.setForeground(idx, green_brush)

            # Initialize the current contact index, which we'll need for keep track of the labeling
            self.model.current_contact_index = 0
            self.model.current_measurement_index = 0

            measurement_item = self.get_current_measurement_item()
            self.measurement_tree.setCurrentItem(measurement_item, True)

    # TODO Change this so it first checks what we clicked on and then calls the right function
    def put_measurement(self):
        # Check if the tree aint empty!
        if not self.measurement_tree.topLevelItemCount():
            return

        current_item = self.measurement_tree.currentItem()
        # Only put the measurement if we selected a measurement
        if current_item.parent():
            return
        self.model.current_measurement_index = self.measurement_tree.indexOfTopLevelItem(current_item)
        # Notify the model to update the subject_name + measurement_name if necessary
        self.measurement_name = current_item.text(0)
        self.measurement_name_label.setText("Measurement name: {}".format(self.measurement_name))

        measurement = {"measurement_name": self.measurement_name}
        self.model.put_measurement(measurement=measurement)

    def get_current_measurement_item(self):
        return self.measurement_tree.topLevelItem(self.model.current_measurement_index)

    def update_current_contact(self):
        if (self.model.current_contact_index <= len(self.model.contacts[self.model.measurement_name]) and
                    len(self.model.contacts[self.model.measurement_name]) > 0):

            # Get the currently selected measurement
            measurement_item = self.get_current_measurement_item()
            for index, contact in enumerate(self.model.contacts[self.model.measurement_name]):
                contact_label = contact.contact_label
                # Get the current row from the tree
                contact_item = measurement_item.child(index)
                contact_item.setText(1, self.contact_dict[contact_label])

                # Update the colors in the contact tree
                for idx in xrange(contact_item.columnCount()):
                    if contact_label >= 0:
                        contact_item.setBackground(idx, self.colors[contact_label])

            self.model.update_current_contact()


    def undo_label(self):
        self.previous_contact()
        self.remove_label()

    def remove_label(self):
        # Check if we have any contacts available, else don't bother
        if not self.contacts_available():
            return

        # Check if any other contact has the label -1, if so change it to -2
        for index, contact in self.model.contacts[self.model.measurement_name]:
            if contact.contact_label == -1:
                contact.contact_label = -2

        # Remove the label
        current_contact = self.get_current_contact()
        current_contact.contact_label = -1
        # Update the screen
        self.update_current_contact()

    def invalid_contact(self):
        # Check if we have any contacts available, else don't bother
        if not self.contacts_available():
            return

        # I've picked -3 as the label for invalid contacts
        current_contact = self.get_current_contact()
        current_contact.contact_label = -3
        # Update the screen
        self.update_current_contact()

    def get_current_contact(self):
        current_contact = self.model.contacts[self.model.measurement_name][self.model.current_contact_index]
        return current_contact

    def select_left_front(self):
        current_contact = self.get_current_contact()
        if current_contact.contact_label != -3:
            current_contact.contact_label = 0
        self.next_contact()

    def select_left_hind(self):
        current_contact = self.get_current_contact()
        if current_contact.contact_label != -3:
            current_contact.contact_label = 1
        self.next_contact()

    def select_right_front(self):
        current_contact = self.get_current_contact()
        if current_contact.contact_label != -3:
            current_contact.contact_label = 2
        self.next_contact()

    def select_right_hind(self):
        current_contact = self.get_current_contact()
        if current_contact.contact_label != -3:
            current_contact.contact_label = 3
        self.next_contact()

    def contacts_available(self):
        """
        This function checks if there is a contact with index 0, if not, the tree must be empty
        """
        return True if self.model.contacts[self.model.measurement_name] else False

    def check_label_status(self):
        results = []
        for contact in self.model.contacts[self.model.measurement_name]:
            if contact.contact_label == -2:
                results.append(True)
            else:
                results.append(False)
        return any(results)

    def previous_contact(self):
        if not self.contacts_available():
            return

        # We can't go to a previous contact
        if self.model.current_contact_index == 0:
            return

        # If we haven't labeled the current contact yet, mark it as unselected
        current_contact = self.get_current_contact()
        if current_contact.contact_label == -1:
            current_contact.contact_label = -2

        self.model.current_contact_index -= 1
        current_contact = self.get_current_contact()
        # If we encounter an invalid contact and its not the first contact, skip this one
        if current_contact.contact_label == -3 and self.check_label_status():
            self.previous_contact()

        measurement_item = self.get_current_measurement_item()
        contact_item = measurement_item.child(self.model.current_contact_index)
        self.measurement_tree.setCurrentItem(contact_item)
        self.update_current_contact()

    def next_contact(self):
        if not self.contacts_available():
            return

        # We can't go further so return
        if self.model.current_contact_index == len(self.model.contacts[self.model.measurement_name]) - 1:
            return

        # If we haven't labeled the current contact yet, mark it as unselected
        current_contact = self.get_current_contact()
        if current_contact.contact_label == -1:
            current_contact.contact_label = -2

        self.model.current_contact_index += 1
        current_contact = self.get_current_contact()
        # If we encounter an invalid contact and its not the last contact, skip this one
        if current_contact.contact_label == -3 and self.check_label_status():
            self.next_contact()

        measurement_item = self.get_current_measurement_item()
        contact_item = measurement_item.child(self.model.current_contact_index)
        self.measurement_tree.setCurrentItem(contact_item)
        self.update_current_contact()

    def switch_contacts(self):
        item = self.contacts_tree.selectedItems()[0]
        self.model.current_contact_index = int(item.text(0))
        self.update_current_contact()

    def track_contacts(self, event=None):
        # Make the model track new contacts
        self.model.repeat_track_contacts()
        # Make sure every widget gets updated
        self.update_current_contact()

    def store_status(self, event=None):
        self.model.store_contacts()

    def stored_status(self, success):
        # If we were successful, change the color of the tree
        if success:
            current_item = self.measurement_tree.currentItem()
            green_brush = QtGui.QBrush(QtGui.QColor(46, 139, 87))
            current_item.setForeground(0, green_brush)

    def clear_cached_values(self):
        pass

    def changed_settings(self):
        self.colors = self.settings.colors()
        self.contact_dict = self.settings.contact_dict()
        # Update all the keyboard shortcuts
        self.left_front_action.setShortcut(self.settings.left_front())
        self.left_hind_action.setShortcut(self.settings.left_hind())
        self.right_front_action.setShortcut(self.settings.right_front())
        self.right_hind_action.setShortcut(self.settings.right_hind())
        self.previous_contact_action.setShortcut(self.settings.previous_contact())
        self.next_contact_action.setShortcut(self.settings.next_contact())
        self.invalid_contact_action.setShortcut(self.settings.invalid_contact())
        self.remove_label_action.setShortcut(self.settings.remove_label())

    def create_toolbar_actions(self):
        self.track_contacts_action = gui.create_action(text="&Track Contacts",
                                                       shortcut=QtGui.QKeySequence("CTRL+F"),
                                                       icon=QtGui.QIcon(
                                                           os.path.join(os.path.dirname(__file__),
                                                                        "../images/edit_zoom.png")),
                                                       tip="Using the tracker to find contacts",
                                                       checkable=False,
                                                       connection=self.track_contacts
        )

        self.store_status_action = gui.create_action(text="&Store",
                                                     shortcut=QtGui.QKeySequence("CTRL+S"),
                                                     icon=QtGui.QIcon(
                                                         os.path.join(os.path.dirname(__file__),
                                                                      "../images/save_icon.png")),
                                                     tip="Mark the tracking as correct",
                                                     checkable=False,
                                                     connection=self.store_status
        )

        self.left_front_action = gui.create_action(text="Select Left Front",
                                                   shortcut=self.settings.left_front(),
                                                   icon=QtGui.QIcon(
                                                       os.path.join(os.path.dirname(__file__),
                                                                    "../images/LF_icon.png")),
                                                   tip="Select the Left Front contact",
                                                   checkable=False,
                                                   connection=self.select_left_front
        )

        self.left_hind_action = gui.create_action(text="Select Left Hind",
                                                  shortcut=self.settings.left_hind(),
                                                  icon=QtGui.QIcon(
                                                      os.path.join(os.path.dirname(__file__),
                                                                   "../images/LH_icon.png")),
                                                  tip="Select the Left Hind contact",
                                                  checkable=False,
                                                  connection=self.select_left_hind
        )

        self.right_front_action = gui.create_action(text="Select Right Front",
                                                    shortcut=self.settings.right_front(),
                                                    icon=QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                                  "../images/RF_icon.png")),
                                                    tip="Select the Right Front contact",
                                                    checkable=False,
                                                    connection=self.select_right_front
        )

        self.right_hind_action = gui.create_action(text="Select Right Hind",
                                                   shortcut=self.settings.right_hind(),
                                                   icon=QtGui.QIcon(
                                                       os.path.join(os.path.dirname(__file__),
                                                                    "../images/RH_icon.png")),
                                                   tip="Select the Right Hind contact",
                                                   checkable=False,
                                                   connection=self.select_right_hind
        )

        self.previous_contact_action = gui.create_action(text="Select Previous contact",
                                                         shortcut=[self.settings.previous_contact(),
                                                                   QtGui.QKeySequence(QtCore.Qt.Key_Down)],
                                                         icon=QtGui.QIcon(
                                                             os.path.join(os.path.dirname(__file__),
                                                                          "../images/backward.png")),
                                                         tip="Select the previous contact",
                                                         checkable=False,
                                                         connection=self.previous_contact
        )

        self.next_contact_action = gui.create_action(text="Select Next contact",
                                                     shortcut=[self.settings.next_contact(),
                                                               QtGui.QKeySequence(QtCore.Qt.Key_Up)],
                                                     icon=QtGui.QIcon(
                                                         os.path.join(os.path.dirname(__file__),
                                                                      "../images/forward.png")),
                                                     tip="Select the next contact",
                                                     checkable=False,
                                                     connection=self.next_contact
        )

        self.remove_label_action = gui.create_action(text="Delete Label From contact",
                                                     shortcut=self.settings.remove_label(),
                                                     icon=QtGui.QIcon(
                                                         os.path.join(os.path.dirname(__file__),
                                                                      "../images/cancel_icon.png")),
                                                     tip="Delete the label from the contact",
                                                     checkable=False,
                                                     connection=self.remove_label
        )

        self.invalid_contact_action = gui.create_action(text="Mark contact as Invalid",
                                                        shortcut=self.settings.invalid_contact(),
                                                        icon=QtGui.QIcon(
                                                            os.path.join(os.path.dirname(__file__),
                                                                         "../images/trash_icon.png")),
                                                        tip="Mark the contact as invalid",
                                                        checkable=False,
                                                        connection=self.invalid_contact
        )

        self.undo_label_action = gui.create_action(text="Undo Label From contact",
                                                   shortcut=QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Z),
                                                   icon=QtGui.QIcon(
                                                       os.path.join(os.path.dirname(__file__),
                                                                    "../images/undo_icon.png")),
                                                   tip="Delete the label from the contact",
                                                   checkable=False,
                                                   connection=self.undo_label
        )

        # TODO Not all actions are editable yet in the settings
        self.actions = [self.store_status_action, self.track_contacts_action,
                        self.left_front_action, self.left_hind_action,
                        self.right_front_action, self.right_hind_action,
                        self.previous_contact_action, self.next_contact_action,
                        self.remove_label_action, self.invalid_contact_action, self.undo_label_action]

        for action in self.actions:
            #action.setShortcutContext(Qt.WindowShortcut)
            self.toolbar.addAction(action)


