import logging
from pubsub import pub
from pawlabeling.models import table
from pawlabeling.settings import settings


class PlateModel(object):
    def __init__(self):
        self.settings = settings.settings
        self.database_file = self.settings.database_file()
        self.plates_table = table.PlatesTable(database_file=self.database_file)
        self.logger = logging.getLogger("logger")

        plates = self.settings.setup_plates()
        # If not all plates are in the plates table, add them
        if len(self.plates_table.plates_table) != len(plates):
            for plate in plates:
                self.create_plate(plate)

        # Keep a dictionary with all the plates with their id as the key
        self.plates = {}
        for plate in self.plates_table.get_plates():
            self.plates[plate["plate_id"]] = plate

    def create_plate(self, plate):
        """
        This function takes a plate dictionary object and stores it in PyTables
        """
        # Check if the plate is already in the table
        p = self.plates_table.get_plate(brand=plate["brand"], model=plate["model"])
        if p:
            return p["plate_id"]

        # Create a subject id
        plate_id = self.plates_table.get_new_id()
        plate["plate_id"] = plate_id

        self.plates_table.create_plate(**plate)

    def get_plates(self):
        plates = self.plates_table.get_plates()
        return plates

    # I'm not sure I want to put such information
    def put_plate(self, plate):
        self.plate = plate
