import logging
from pubsub import pub
from pawlabeling.models import table
from pawlabeling.settings import settings

class MissingIdentifier(Exception):
    pass

class SubjectModel(object):
    def __init__(self):
        self.settings = settings.settings
        self.database_file = self.settings.database_file()
        self.subjects_table = table.SubjectsTable(database_file=self.database_file)
        self.logger = logging.getLogger("logger")

    def create_subject(self, subject):
        """
        This function takes a subject dictionary object and stores it in PyTables
        """
        # TODO Add some other validation to see if the input values are correct
        # Check if the subject is already in the table
        result = self.subjects_table.get_subject(plate=subject["first_name"],
                                                   last_name=subject["last_name"],
                                                   birthday=subject["birthday"])
        if result:
            return result["subject_id"]

        # Create a subject id
        subject_id = self.subjects_table.get_new_id()
        subject["subject_id"] = subject_id
        self.subject_group = self.subjects_table.create_subject(**subject)
        return subject_id

    def get_subjects(self):
        subjects = self.subjects_table.get_subjects()
        return subjects
