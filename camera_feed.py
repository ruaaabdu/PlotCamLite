####################################################
# camera_feed.py v0.3
####################################################
"""
This code handles camera feed functions
@author Ruaa Abdulmajeed
@date February 23rd, 2021
"""

# Python wrapper for the RS Cam
import pyrealsense2 as rs

# OS module provides functions related to the OS
import os 

# Numpy for array functions
import numpy as np

# CV2 for resizing image
#import cv2

# A deque is a list where we can remove from beginning and end, writing will add to right and reading will take from the front
from collections import deque

# QImage for sending RGB image as a QImage
from PyQt5.QtGui import QImage

# PyQt Core for slots, signals, and threads
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot

from threading import Thread

tosave_buffer = deque([]) # Initalize empty deque to write and read values from

def save_pictures():
    while tosave_buffer:
        image_data = tosave_buffer.popleft()

        image = image_data[0]
        depth_frame = image_data[1]
        filepath = image_data[2]
        filename = image_data[3]
        
        save_rgb_640(filepath + "\RGB\\" + filename, image)
        save_depth_640(filepath + "\depth\\" + filename, depth_frame)


def save_rgb_640(filename_to_save, image):
    image.save(filename_to_save + ".bmp")

def save_depth_640(filename_to_save, depth_frame):
    frame_height = depth_frame.get_height()
    frame_width = depth_frame.get_width()
    with open(str(filename_to_save + ".txt"), 'w') as outfile:
        for y in range(0, frame_height):
            for x in range(0, frame_width):
                pixel_depth = depth_frame.get_distance(x, y)
                #outfile.write("x = " + str(x) + " y = " + str(y) + " Depth = " + str(pixel_depth) + "\n")
                outfile.write(str(pixel_depth) + "\n")


class CameraThread(QThread):
    """CameraThread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changePixmap = pyqtSignal(QImage)
    q_img = None
    def __init__(self, parent=None):
        super(CameraThread, self).__init__(parent)
        self.runs = False
        self.saveThread = None

    def run(self):
        self.runs = True
        self.commence_working()
        self.stop()

    def stop(self):
        self.runs = False

    def commence_working(self):
        """ Runs a pipeline which checks for image changing and enables stream """
        rotate_image = True
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
        config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
        pipeline.start(config)

        while self.runs == True:  # while thread is running and loop gets image
            self.frames = pipeline.wait_for_frames()
            color_frame = self.frames.get_color_frame()

            if not color_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())

            if rotate_image:
                color_image = np.rot90(color_image, 1).copy()

            self.color_image_1280 = color_image

            #color_image = cv2.resize(color_image, dsize = (480, 640), interpolation=cv2.INTER_CUBIC)

            height, width, channel = color_image.shape
            bytes_per_line = channel * width

            # RGB555 is cool looking, RGB888 is blue, BGR88 is the best option
            self.q_img = QImage(color_image.data, width, height,
                           bytes_per_line, QImage.Format_BGR888)
            self.changePixmap.emit(self.q_img)

    @pyqtSlot(str)
    def take_picture(self, filepath, filename):
        """ Saves RGB image and Depth data

        Args:
            filepath (str): Directory path leading to experiment
            filename (str): Experiment name
        """
        depth_frame = self.frames.get_depth_frame()
        #saveThread = None
        image_data = (self.q_img, depth_frame, filepath, filename)
        tosave_buffer.append(image_data)
        if not self.saveThread or not self.saveThread.is_alive():
            self.saveThread = Thread(target=save_pictures)
            self.saveThread.start()


