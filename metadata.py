import json
import os

class Metadata:
    """[summary]
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.load_data()
        self.count = 0

    def load_data(self):
        with open(self.filepath, 'r') as f:
            if os.path.getsize(self.filepath,) == 0:
                self.metadata = []
                self.count = 0
            else:
                self.metadata = json.load(f)
                self.count = len(self.metadata)

    def add_entry(self, number, time, air, light, lat, lon, batt, zero, plantheight):
        image_data = {
            "number" : number,
            "time" : time,
            "air" : air,
            "light": light,
            "lattitude" : lat,
            "longitue" : lon,
            "battery" : batt,
            "zeroingvalue" : batt,
            "plantheight" : plantheight
        }
        self.metadata.append(image_data)
        with open(self.filepath, 'w') as f:
            json.dump(self.metadata, f, indent=4)
    
    def get_value(self, elementkey):
        return self.metadata[-1][elementkey]


def main():
    """ Creates an instance of the PlotCamLite program """
    ex = Metadata(r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Working Directory\CameraData\22222222\Metadata\haha.json")
    ex.add_entry(1, 2, 3, 4, 5, 6, 7, 8, 9)
    print(ex.get_value("number"))

if __name__ == '__main__':
    main()