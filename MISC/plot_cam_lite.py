####################################################
# plot_cam_lite.py v0.1
####################################################
"""
This code runs the Plot Cam Lite Module
@author Ruaa Abdulmajeed
@date January 20th, 2020
"""
# Sys module provides functions to manipulate Python runtime environment
import sys

# CV2 for OpenCV
import cv2

# numpy for image manipulation
import numpy as np

# Python wrapper for the RS Cam
import pyrealsense2 as rs

# PyQt Core for slots, signals, and threads
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot

# PyQt Widgets for the applicaton and layout
from PyQt5.QtWidgets import QApplication, QWidget, \
    QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLabel,\
    QDialog

# PyQt GUI for GUI components
from PyQt5.QtGui import QIcon, QImage, QPixmap

# PyQt SVG for SVG images
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget

# PyQt UIC for UI methods
from PyQt5.uic import loadUi

# Figure Canvas for adding Figure as a widget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# Figure for the plot figure
from matplotlib.figure import Figure

# PyPlot for creating the plot
import matplotlib.pyplot as plt

import random
# RPI flag for if the program is being used for RPI or Windows
# False for Windows and True for RPI
RPI = False

class Window(QWidget):
    """Window class is used to generate UI of the main program.
    Window is the top class, it encompasses the rest of the classes and UI

    Args:
        QWidget (QWidget): Base class of all UI objects
    """

    def __init__(self): # runs everytime a window object is created
        """ Initalizes the window class by introducing the variables needed """
        super().__init__()
        if RPI:
            self.title = "PlotCam Lite - RPI and PyQt5"
        else:
            self.title = "PlotCam Lite - Windows and PyQt5"

        self.width = 2000 # width of window
        self.height = 800 # height of window
        self.left = 100 # distance from left
        self.top = 100 # distance from top

        # Initalizes grid for UI
        self.horizontal_group_box = QGroupBox("Grid")

        # 
        self.image_label = QLabel(self)

        # Initalizes target SVG
        #self.target_svg = QSvgWidget(r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Qt for Python\Code\HOLD\Windows-Code\svg_target.svg")
        
        # a figure instance to plot on
        self.figure = Figure()
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        self.init_ui() # run the method which sets up the UI

    def init_ui(self):
        """ Initalizes the UI and camera feed processing thread """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('cameraleaf.png')) #sets icon in top left of screen, optional

        #set up grid layout, can be modified later
        self.create_grid_layout()
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.horizontal_group_box)
        self.setLayout(window_layout)
        camera_thread1 = CameraThread(self)
        camera_thread1.changePixmap.connect(self.set_image)
        camera_thread1.start()

        # accelerometer_thread = AccelerometerThread(self)
        # accelerometer_thread.changeTarget.connect(self.set_target)
        # accelerometer_thread.start()


        self.show()

    def create_grid_layout(self):
        """ Creates 3x3 grid layout to use as main UI and adds the UI components """

        # horizontal group to contain the grid layout
        layout = QGridLayout()
        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        layout.setRowStretch(2, 4)

        # button to add new file
        new_file_btn = QPushButton("New File", self)
        
        #new_file_btn.clicked.connect(execute_new_file_dialog) # will add again once accelerometer is complete

        # Add Figure for Accelerometer plot


        layout.addWidget(new_file_btn,0,0)
        layout.addWidget(self.canvas, 2, 0)
        layout.addWidget(self.image_label, 2, 2)

        self.horizontal_group_box.setLayout(layout)

    @pyqtSlot(QImage)
    def set_image(self, image):
        """ Updates video stream

        Args:
            image (QImage): Video stream
        """
        pix = QPixmap.fromImage(image)
        self.image_label.setPixmap(pix)


class CameraThread(QThread):
    """CameraThread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changePixmap = pyqtSignal(QImage)

    def run(self):
        """ Runs a pipeline which checks for image changing and enables stream """
        rotate_image = True
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)

        while True: # while loop gets image
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())

            if rotate_image:
                color_image = np.rot90(color_image, 1).copy()

            height, width, channel = color_image.shape
            bytes_per_line = channel * width

            q_img = QImage(color_image.data, width, height, bytes_per_line, QImage.Format_BGR888) # RGB555 is cool, RGB888 is blue, BGR88 is the best option

            self.changePixmap.emit(q_img) # triggers the signal, which updates the image

class NewFilePage(QDialog):
    """ Pop up dialog to select files to write data to.

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """
    def __init__(self):
        super(NewFilePage, self).__init__()
        loadUi('NewFileDialog.ui', self)
        #self.setUpLayout()
        self.show()

def execute_new_file_dialog():
    """ Creates an instance of the new file dialog page """
    newFile_page = NewFilePage()
    newFile_page.exec_()

def print_camera_serial():
    """Returns the number of cameras connected to the OS

    Returns:
        int: number of Intel RealSense cameras connected
    """
    ctx = rs.context()
    num_cameras = len(ctx.devices)
    return num_cameras

def main():
    """ Creates an instance of the PlotCamLite program """

    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_()) # the app.exec command starts the main threa, aka the GUI thread


if __name__ == '__main__':
    main()
