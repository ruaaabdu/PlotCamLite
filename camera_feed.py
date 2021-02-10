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
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        pipeline.start(config)

        while self.runs == True and True:  # while thread is running and loop gets image
            frames = pipeline.wait_for_frames()
            frameset = pipeline.
            color_frame = frames.get_color_frame()
            self.depth_frame = frames.get_depth_frame()
            self.depth_frame.keep()

            if not color_frame or not self.depth_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())

            if rotate_image:
                color_image = np.rot90(color_image, 1).copy()

            self.color_image_1280 = color_image

            color_image = cv2.resize(color_image, dsize = (480, 640), interpolation=cv2.INTER_CUBIC)

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
        height, width, channel = self.color_image_1280.shape
        bytes_per_line = channel * width

        # # RGB555 is cool looking, RGB888 is blue, BGR88 is the best option
        self.q_img2 = QImage(self.color_image_1280.data, width, height, bytes_per_line, QImage.Format_BGR888)
        if self.q_img2 == None:
            return
        self.q_img2.save(filename_to_save)
        # with open(str(filename_to_save + ".txt"), 'w') as outfile:
        #     for r in range(0, 1280):
        #         for c in range(0, 720):
        #             pixel_depth = self.depth_frame.get_distance(c, r)
        #             outfile.write(str(pixel_depth) + "\n")



