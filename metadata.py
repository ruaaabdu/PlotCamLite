####################################################
# metadata.py v0.2
####################################################
"""
This code handles the metadata functions
@author Ruaa Abdulmajeed
@date February 23rd, 2020
"""
# JSON module provides JSON Data functions
import json

# OS module provides functions related to the OS
import os

class Metadata:
    """ An instance of this class creates/reads a file in the given directory to store a metadata file. This class also contains
    functions to manipulate the data.
    """

    def __init__(self, filepath):
        """ Constructor for Metadata class.

        Args:
            filepath (str): File path of metadata file, excluding filetype
        """
        filetype = ".json"
        self.filepath = filepath + filetype
        # Specifies the count of images taken, this is updated in load_data() if there is an existing metadata file.
        self.count = 0
        self.load_data()

    def load_data(self):
        """ Creates new file to store metadata in given directory. If file exists, the existing information is stored."""
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath,) == 0:
            with open(self.filepath, 'w') as fp:
                self.metadata = []
                self.count = 0
        else:
            with open(self.filepath, 'r') as f:
                self.metadata = json.load(f)
                self.count = len(self.metadata)

    def add_entry(self, number, time, xpos, ypos, air, light, lat, lon, batt, zero, plantheight):
        """ Appends plot data to metadata file.

        Args:
            number (str): The plot number, padded by 0s on the left so that its always 3 digits
            time (str): The time the image was taken at
            xpos (int): The x coordinate
            ypos (int): The y coordinate
            air (int): The air 
            light (int): The light
            lat (int): The lattitude where the picture was taken
            lon (int): The longitude where the picture was taken
            batt (int): The battery level 
            zero (int): The zeroing value
            plantheight (int): The average plant height 
        """
        image_data = {
            "number": number,
            "time": time,
            "xpos": xpos,
            "ypos": ypos,
            "air": air,
            "light": light,
            "lattitude": lat,
            "longitude": lon,
            "battery": batt,
            "zeroingvalue": batt,
            "plantheight": plantheight
        }

        self.metadata.append(image_data)
        with open(self.filepath, 'w') as f:
            # Saves metadata entry and formatting using indent=4
            json.dump(self.metadata, f, indent=4)

    def get_last_index(self):
        """Returns the plot number of the last plot captures

        Returns:
            str: The plot number of the last element
        """
        if len(self.metadata) == 0: # file is empty
            return 0
        return self.metadata[-1]["number"]

sampleMetaData = {
    "time": "10:24:26 AM",
    "air": "20.9",
    "light": "306",
    "lattitude": "45.234008",
    "longitude": "75.42955",
    "battery": "13.0",
    "zeroingvalue": "1754",
    "plantheight": "665"
}

if __name__ == '__main__':
    """ Testing purposes"""
    ex = Metadata(
        r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Working Directory\CameraData\22222222\Metadata\haha.json")
    print(ex.get_last_index())
