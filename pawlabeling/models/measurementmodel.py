from ..models import table
from ..functions import io, calculations
from ..settings import settings

class Measurements(object):
    def __init__(self, subject_id, session_id):
        self.subject_id = subject_id
        self.session_id = session_id
        self.table = settings.settings.table
        self.measurements_table = table.MeasurementsTable(table=self.table,
                                                          subject_id=self.subject_id,
                                                          session_id=self.session_id)

    def create_measurement(self, measurement, plates):
        measurement_object = Measurement(subject_id=self.subject_id, session_id=self.session_id)

        # Be sure to strip the zip of if its there
        measurement_name = measurement["measurement_name"]
        if measurement_name[-3:] == "zip":
            measurement_name = measurement_name[:-4]

        # If it already exists, restore the Measurement object and return that
        result = self.measurements_table.get_measurement(measurement_name=measurement_name)
        if result:
            return

        measurement_id = self.measurements_table.get_new_id()
        # Else we create a copy of our own
        # If create_measurement raises an error, we will fail silently
        try:
            measurement_object.create_measurement(measurement_id=measurement_id,
                                                  measurement=measurement,
                                                  plates=plates)
        except Exception:
            return

        measurement = measurement_object.to_dict()
        # Finally we create the contact
        self.measurement_group = self.measurements_table.create_measurement(**measurement)
        return measurement_object

    def delete_measurement(self, measurement):
        # Delete both the row and the group
        self.measurements_table.remove_row(table=self.measurements_table.measurements_table,
                                           name_id="measurement_id",
                                           item_id=measurement.measurement_id)
        self.measurements_table.remove_group(where="/{}/{}".format(self.subject_id, self.session_id),
                                             name=measurement.measurement_id)
        # If we've removed all the sessions, clean up after yourself
        try:
            self.measurements_table.get_measurements()
        except table.ClosedNodeError:
            self.measurements_table = table.MeasurementsTable(table=self.table,
                                                              subject_id=self.subject_id,
                                                              session_id=self.session_id)

    def get_measurements(self):
        measurements = {}
        try:
            self.measurements_table.get_measurements()
        except table.ClosedNodeError:
            return measurements

        for measurement in self.measurements_table.get_measurements():
            measurement_object = Measurement(subject_id=self.subject_id,
                                             session_id=self.session_id)
            measurement_object.restore(measurement)
            measurements[measurement_object.measurement_id] = measurement_object
        return measurements

    def create_measurement_data(self, measurement, measurement_data):
        self.measurements_table.store_data(group=self.measurement_group,
                                           item_id=measurement.measurement_id,
                                           data=measurement_data)

    def get_measurement_data(self, measurement):
        group = self.measurements_table.get_group(self.measurements_table.session_group,
                                                  measurement.measurement_id)
        item_id = measurement.measurement_id
        measurement_data = self.measurements_table.get_data(group=group, item_id=item_id)
        return measurement_data

    def update_n_max(self):
        n_max = 0
        for measurement in self.measurements_table.measurements_table:
            max_value = measurement["maximum_value"]
            if max_value > n_max:
                n_max = max_value
        return n_max

    def update(self, measurement):
        self.measurements_table.update_measurement(item_id=measurement.measurement_id, **measurement.to_dict())

class Measurement(object):
    def __init__(self, subject_id, session_id):
        self.subject_id = subject_id
        self.session_id = session_id

    def create_measurement(self, measurement_id, measurement, plates):
        # Get a new id for this measurement
        self.measurement_id = measurement_id
        file_path = measurement["file_path"]
        measurement_name = measurement["measurement_name"]

        # Strip the .zip from the measurement_name
        if measurement_name[-3:] == "zip":
            self.zipped = True
            self.measurement_name = measurement_name[:-4]
        else:
            self.zipped = False
            self.measurement_name = measurement_name

        # Get the raw string from the file path
        input_file = self.load_file_path(file_path=file_path)

        # Get the plate info, so we can get the brand
        self.plate_id = measurement["plate_id"]
        self.plate = plates[self.plate_id]

        self.date = measurement["date"]
        self.time = measurement["time"]
        self.processed = False

        # Extract the measurement_data
        self.measurement_data = io.load(input_file, brand=self.plate.brand)
        # io.load only logs when there's an exception and returns None
        if self.measurement_data is None:
            raise Exception

        self.number_of_rows, self.number_of_columns, self.number_of_frames = self.measurement_data.shape
        self.orientation = calculations.check_orientation(self.measurement_data)
        self.maximum_value = self.measurement_data.max()  # Perhaps round this and store it as an int?
        self.frequency = measurement["frequency"]

    def load_file_path(self, file_path):
        # Check if the file is zipped or not and extract the raw measurement_data
        if self.zipped:
            # Unzip the file
            input_file = io.open_zip_file(file_path)
        else:
            with open(file_path, "r") as infile:
                input_file = infile.read()

            # If the user wants us to zip it, zip it so they don't keep taking up so much space!
            if settings.settings.zip_files():
                io.zip_file(file_path)

        return input_file

    def restore(self, measurement):
        for key, value in measurement.items():
            setattr(self, key, value)


    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "session_id": self.session_id,
            "measurement_id": self.measurement_id,
            "plate_id": self.plate_id,
            "measurement_name": self.measurement_name,
            "number_of_frames": self.number_of_frames,
            "number_of_rows": self.number_of_rows,
            "number_of_columns": self.number_of_columns,
            "frequency": self.frequency,
            "orientation": self.orientation,
            "maximum_value": self.maximum_value,
            "date": self.date,
            "time": self.time,
            "processed": self.processed
        }

class MockMeasurement(object):
    def __init__(self, measurement_id, data, frequency):
        self.measurement_id = measurement_id
        self.data = data
        x, y, z = data.shape
        self.number_of_rows = x
        self.number_of_columns = y
        self.number_of_frames = z
        self.orientation = True
        self.frequency = frequency