####################################################
# plot_cam_lite.py v0.1
####################################################
"""
This code runs the Plot Cam Lite Module. It will allow the user to view the camera feed of an
Intel Realsense D415 camera as well as capture the RGB and depth data from the camera at anytime.
@author Ruaa Abdulmajeed
@date January 26th, 2020 (Last Updated)
"""
# Sys module provides functions to manipulate Python runtime environment
import sys

import logging

import os

# CV2 for OpenCV
#import cv2

# Python threading program
from threading import Thread

# Python wrapper for the RS Cam
import pyrealsense2 as rs

# PyQt Core for slots, signals, and threads
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QRunnable, QThreadPool

# PyQt Widgets for the applicaton and layout
from PyQt5.QtWidgets import QApplication, QWidget, \
    QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLabel,\
    QDialog

# for wait
from PyQt5 import QtTest

# PyQt GUI for GUI components
from PyQt5.QtGui import QIcon, QImage, QPixmap

# PyQt SVG for SVG images
#from PyQt5.QtSvg import QSvgRenderer, QSvgWidget

# PyQt UIC for UI methods
from PyQt5.uic import loadUi

# Figure Canvas for adding Figure as a widget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# Figure for the plot figure
from matplotlib.figure import Figure

# PyPlot for creating the plot
#import matplotlib.pyplot as plt

# Accelerometer write file handles the accelerometer
from accelerometer_write import Position, buffer, start_accelerometer

# numpy for image manipulation
import numpy as np

import time
#import random

# ----------------------GLOBAL VARIABLES----------------------
# RPI flag for if the program is being used for RPI or Windows
# Set RPI to False for Windows and True for RPI
RPI = False

# Log variable for logging
log = None

# Number of cameras connected
NUMBER_CAMERAS = 0

take_picture = False

# Start accelerometer thread using Python threading
accelerometer_write_thread = Thread(target=start_accelerometer)

class CameraWorker(QRunnable):
    @pyqtSlot()
    def run(self):
        print("Camera Thread start")
        time.sleep(5)
        print("Camera Thread complete")

class Window(QWidget):
    """Window class is used to generate UI of the main program.
    Window is the top class, it encompasses the rest of the classes and UI

    Args:
        QWidget (QWidget): Base class of all UI objects
    """

    def __init__(self):  # runs everytime a window object is created
        """ Initalizes the window class by introducing the variables needed """
        super().__init__()
        if RPI:
            self.title = "PlotCam Lite - RPI and PyQt5"
        else:
            self.title = "PlotCam Lite - Windows and PyQt5"

        self.width = 2000  # width of window
        self.height = 800  # height of window
        self.left = 100  # distance from left
        self.top = 100  # distance from top

        # Sets number of cameras connected to computer
        NUMBER_CAMERAS = print_number_of_cameras()

        if NUMBER_CAMERAS < 1:
            log.error("MISSON ABORT. There are no cameras connected")
            exit()
        elif NUMBER_CAMERAS == 1:
            log.info("There is " + str(NUMBER_CAMERAS) +
                     " Realsense camera connected")
        else:
            log.info("There are " + str(NUMBER_CAMERAS) +
                     " Realsense cameras connected")

        # Initalizes grid for UI
        self.horizontal_group_box = QGroupBox("Grid")

        # Initalizes image label which will store the camera feed
        self.image_label = QLabel(self)

        # this is the Canvas Widget that displays the `figure`
        self.target_canvas = Canvas(self, width=5, height=4, dpi=100)

        log.info("Main: Program Launched, Window class initialized")
        self.init_ui()  # run the method which sets up the UI

    def init_ui(self):
        """ Initalizes the UI and camera feed processing thread """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Sets icon in top left of screen, optional
        self.setWindowIcon(QIcon('cameraleaf.png'))

        # Set up grid layout, can be modified later
        self.create_grid_layout()
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.horizontal_group_box)
        self.setLayout(window_layout)
        log.info("UI: Grid layout created and widget is added to window")

        self.threadpool = QThreadPool()
        log.info("Main: Multithreading with maximum %d threads" % self.threadpool.maxThreadCount()) # we have 8 threads to work with in this threadpool
        self.create_camera_thread()

        self.show()
        

        #initial_pos = Position(0, 0)
        # self.draw_coordinate(initial_pos)
        #log.info("Target: Origin point drawn")
        # QtTest.QTest.qWait(2000)

    def create_grid_layout(self):
        """ Creates 3x3 grid layout to use as main UI and adds the UI components """

        # horizontal group to contain the grid layout
        layout = QGridLayout()
        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        layout.setRowStretch(2, 4)

        # Button to add new file
        new_file_btn = QPushButton("New File", self)
        new_file_btn.clicked.connect(execute_new_file_dialog)

        # Button to capture photo
        save_photo_btn = QPushButton("Take Picture", self)
        #save_photo_btn.clicked.connect(save_image)

        # Button to teardown
        exit_program_btn = QPushButton("Exit", self)
        exit_program_btn.clicked.connect(self.exit_program)

        # Add Figure for Accelerometer plot
        layout.addWidget(new_file_btn, 0, 0)
        layout.addWidget(save_photo_btn, 0, 2)
        layout.addWidget(exit_program_btn, 0, 1)
        #layout.addWidget(self.target_canvas, 2, 0)
        layout.addWidget(self.image_label, 2, 2)

        self.horizontal_group_box.setLayout(layout)
        log.info("UI: Grid Layout created and widgets are added")

    def exit_program(self):

        self.camera_thread1.stop()

        log.info("Main: Program Terminated")

    def create_camera_thread(self):
        camera_worker = CameraThreadQRunnable()
        #self.camera_thread1.changePixmap.connect(self.set_image)
        self.threadpool.start(camera_worker)
        camera_worker.moveTo
        pix = QPixmap.fromImage(image)
        self.image_label.setPixmap(pix)
    
    @pyqtSlot(QImage)
    def set_image(self, image):
        """ Updates video stream

        Args:
            image (QImage): Video stream
        """
        pix = QPixmap.fromImage(image)
        self.image_label.setPixmap(pix)
        #log.info("Camera: Image set")

    @pyqtSlot(Position)
    def draw_coordinate(self, new_position):
        """ Draws new coordinate on the grid

        Args:
            new_position (Position): Describes the new position of the new accelerometer
        """

        # discards the old graph
        self.target_canvas.axes.clear()
        self.target_canvas.axes.set_xlim(-3, 3)
        self.target_canvas.axes.set_ylim(-3, 3)
        self.target_canvas.axes.plot(new_position.x, new_position.y, 'o')
        log.info(" -------------------Drawing point at: " +
                 str(new_position) + " -------------------")

        self.target_canvas.draw()


class CameraThread(QThread):
    """CameraThread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(CameraThread, self).__init__(parent)
        self.runs = True

    def run(self):
        self.commence_working()
        self.stop()

    def stop(self):
        self.runs = False
        #self.finished.emit()
    
    def commence_working(self):
        """ Runs a pipeline which checks for image changing and enables stream """
        rotate_image = True
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        log.info("Camera: Pipeline started")

        while self.runs == True and True:  # while thread is running and loop gets image
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())

            if rotate_image:
                color_image = np.rot90(color_image, 1).copy()

            height, width, channel = color_image.shape
            bytes_per_line = channel * width

            # RGB555 is cool looking, RGB888 is blue, BGR88 is the best option
            q_img = QImage(color_image.data, width, height,
                           bytes_per_line, QImage.Format_BGR888)
            #log.info("Camera: Camera updated")
            # triggers the signal, which updates the image
            if take_picture == True:
                buffer = QtCore.QBuffer(byte_array)
                buffer.open(QtCore.QIODevice.WriteOnly)
                q_img.save(buffer, 'jpg', 75)
            self.changePixmap.emit(q_img)

class CameraThreadQRunnable(QRunnable):

    #changePixmap = pyqtSignal(QImage)
    @pyqtSlot()

    def run(self):
        """ Runs a pipeline which checks for image changing and enables stream """
        rotate_image = True
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        log.info("Camera: Pipeline started")

        while True:  # while thread is running and loop gets image
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())

            if rotate_image:
                color_image = np.rot90(color_image, 1).copy()

            height, width, channel = color_image.shape
            bytes_per_line = channel * width

            # RGB555 is cool looking, RGB888 is blue, BGR88 is the best option
            q_img = QImage(color_image.data, width, height,
                           bytes_per_line, QImage.Format_BGR888)
            #log.info("Camera: Camera updated")
            # triggers the signal, which updates the image
            if take_picture == True:
                buffer = QtCore.QBuffer(byte_array)
                buffer.open(QtCore.QIODevice.WriteOnly)
                q_img.save(buffer, 'jpg', 75)
            #self.changePixmap.emit(q_img)

class AccelerometerThread(QThread):  # reading thread
    """Accelerometer Thread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changeTarget = pyqtSignal(Position)
    # Needs to emit the signal everytime there is a change

    def __init__(self, parent=None):
        super(AccelerometerThread, self).__init__(parent)
        self.runs = True

    def run(self):
        self.commence_working()
        self.stop()

    def stop(self):
        self.runs = False
        #self.finished.emit()

    def commence_working(self):
        """ Runs the accelerometer write thread """
        accelerometer_write_thread.start()
        while True:
            # If new_pos stores a coordinate  (look into reading/writing problem,
            # buffer is place to store.hold values, one thread will read one thread will write)
            if buffer:
                new_pos = buffer.popleft()
                self.changeTarget.emit(new_pos)
                QtTest.QTest.qWait(1000)


class NewFilePage(QDialog):
    """ Pop up dialog to select files to write data to.

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """

    def __init__(self):
        super(NewFilePage, self).__init__()
        loadUi('NewFileDialog.ui', self)
        # self.setUpLayout()
        self.show()


class Canvas(FigureCanvas):  # from learnpyqt
    """ Canvas sets up the figure within Figure Canvas

    Args:
        FigureCanvas (FigureCanvas): [description]
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)


def execute_new_file_dialog():
    """ Creates an instance of the new file dialog page """
    new_file_page = NewFilePage()
    new_file_page.exec_()


def print_number_of_cameras():
    """Returns the number of cameras connected to the OS

    Returns:
        int: number of Intel RealSense cameras connected
    """
    ctx = rs.context()
    num_cameras = len(ctx.devices)
    return num_cameras


def configure_logging(log_level):
    """configures logging globally through root logger.
    :param log_level: log verbosity
    :type log_level: logging.LEVEL
    """
    log_filename = "plotcamlite_log.txt"
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # create file logging handler & console logging handler
    fh = logging.FileHandler(log_filename)
    fh.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)
    root_logger.info(
        "Logging configured to console and {} at {} level".format(
            os.path.abspath(log_filename),
            logging.getLevelName(root_logger.getEffectiveLevel()),
        )
    )


def main():
    """ Creates an instance of the PlotCamLite program """
    configure_logging("INFO")
    global log
    log = logging.getLogger("PlotCamLite")

    app = QApplication(sys.argv)
    ex = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
