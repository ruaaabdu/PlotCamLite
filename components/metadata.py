####################################################
# metadata.py v0.2
####################################################
"""
This code handles the metadata functions
@author Ruaa Abdulmajeed
@date February 23rd, 2020
"""
import json
import os
from datetime import datetime

class Metadata:
    """
    An instance of this class creates/reads a file in the given directory to store a metadata file. This class also contains
    functions to manipulate the data.
    """

    def __init__(self, metadata_fpath):
        """Constructor for Metadata class.

        Args:
            metadata_fpath (str): File path of metadata file
        """

        self.filepath = metadata_fpath
        self.new_data = False
        self.load_data()

    def load_data(self):
        """
        Prepare metadata information from the filepath.
        If file exists, the existing information is stored, else creates a new file.
        """
        
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath,) == 0:
            with open(self.filepath, "w") as fp:
                self.metadata = []
        else:
            with open(self.filepath, "r") as f:
                self.metadata = json.load(f)
    
    # def load_existing_experiment_metadata(self, existing_filepath):


    def add_entry(self, number, time, date, xpos, ypos, name):
        """Appends plot data to metadata.

        Args:
            number (str): The plot number, padded by 0s on the left so that its always 3 digits
            time (str): The time the image was taken at
            date (str): The date the image was taken 
            xpos (int): The x coordinate
            ypos (int): The y coordinate
            name (int): Experiment name
        """
        image_data = {
            "number": number,
            "time": time,
            "date": date,
            "xpos": xpos,
            "ypos": ypos,
            "name": name,
        }
        self.metadata.append(image_data)
        self.new_data = True

    def get_last_index(self):
        """Returns the plot number of the last plot captures

        Returns:
            int: The plot number of the last element
        """
        if len(self.metadata) == 0:  # file is empty
            return -1

        return int(self.metadata[-1]["number"])

    def save(self):
        """
        Save metadata to file.
        """    
        if not self.new_data:
            return
        
        with open(self.filepath, 'w') as f:
            # Saves metadata entry and formatting using indent=4
            json.dump(self.metadata, f, indent=4)
        
        self.new_data = False