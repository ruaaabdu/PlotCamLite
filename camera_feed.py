## Camera Thread 
# Python wrapper for the RS Cam
import pyrealsense2 as rs

import os 

import numpy as np

import imageio

import threading

import cv2

from PyQt5.QtGui import QImage

from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot

from time import sleep
class CameraThread(QThread):
    """CameraThread runs the thread which handles the camera stream

    Args:
        QThread (QThread): Manages the thread
    """
    changePixmap = pyqtSignal(QImage)
    #color_image = np.array([])
    q_img = None
    def __init__(self, parent=None):
        super(CameraThread, self).__init__(parent)
        self.runs = False

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
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
        pipeline.start(config)

        while self.runs == True and True:  # while thread is running and loop gets image
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

            #log.info("Camera: Camera updated")
            # triggers the signal, which updates the image
            self.changePixmap.emit(self.q_img)

    @pyqtSlot(str)
    def take_picture(self, filename_to_save):
        
        self.save_rgb_640(filename_to_save)
        self.save_depth_640(filename_to_save)
                    
    def save_rgb_1280(self, filename_to_save):
        # actions to save rgb as 1280x720
        height, width, channel = self.color_image_1280.shape
        bytes_per_line = channel * width

        # RGB555 is cool looking, RGB888 is blue, BGR88 is the best option
        self.q_img2 = QImage(self.color_image_1280.data, width, height, bytes_per_line, QImage.Format_BGR888)
        if self.q_img2 == None:
           return
        self.q_img2.save(filename_to_save)
        

    def save_depth_1280(self, filename_to_save):
        ## actions to save depth
        depth_frame = self.frames.get_depth_frame()
        frame_height = depth_frame.get_height()
        frame_width = depth_frame.get_width()
        with open(str(filename_to_save + ".txt"), 'w') as outfile:
            for y in range(0, frame_height):
                for x in range(0, frame_width):
                    pixel_depth = depth_frame.get_distance(x, y)
                    outfile.write("x = " + str(x) + " y = " + str(y) + " Depth = " + str(pixel_depth) + "\n")
        

    def save_rgb_640(self, filename_to_save):
        # actions to save rgb as 640x480
        self.q_img.save(filename_to_save)

    def save_depth_640(self, filename_to_save):
        ## actions to save depth as 640x480
        depth_frame = self.frames.get_depth_frame()
        frame_height = depth_frame.get_height()
        frame_width = depth_frame.get_width()
        with open(str(filename_to_save + ".txt"), 'w') as outfile:
            for y in range(0, frame_height):
                for x in range(0, frame_width):
                    pixel_depth = depth_frame.get_distance(x, y)
                    outfile.write("x = " + str(x) + " y = " + str(y) + " Depth = " + str(pixel_depth) + "\n")


