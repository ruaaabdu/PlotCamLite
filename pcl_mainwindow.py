"""
Main GUI of the PlotCamLite copyright LLC all rights reserved.
"""

import cProfile
import time
from collections import deque
from multiprocessing import Process, Value, shared_memory

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QSizePolicy
from PyQt5.uic import loadUi

from depth_camera import frame_to_pixmap, generate_frames

QT_UI_PATH = "camera_ui.ui"

# frame dimensions
FRAME_HEIGHT = 640
FRAME_WIDTH = 480
FRAME_NCHANNELS = 3
NBYTE_PER_FRAME = FRAME_HEIGHT * FRAME_WIDTH * FRAME_NCHANNELS

# shared memory limit
# 1 img ~= 1 MB, reserving 100 MB of RAM for video feed interaction
SM_BUF_SIZE = 100
STREAM_FPS = 30


class PlotCamLiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        loadUi(QT_UI_PATH, self)
        self.start_stream()

    def start_stream(self):
        """
        Start the camera stream.
        Creates a seperate process for the stream, and communicates with the frames through shared memory.
        Uses a QTimer to have a stable frame rate.
        """      
        # set up the label
        camera_size_policy = QSizePolicy(FRAME_WIDTH, FRAME_HEIGHT)
        self.image_label.setSizePolicy(camera_size_policy)
        
        # create shared memory to hold a single frame for inter process communication,
        # wrap it in a numpy array
        self.frame_shm = shared_memory.SharedMemory(create=True, size=NBYTE_PER_FRAME)
        shm_shape = (1, FRAME_HEIGHT, FRAME_WIDTH, FRAME_NCHANNELS)
        self.current_frame = np.ndarray(shm_shape, dtype=np.uint8, buffer=self.frame_shm.buf)
        self.current_frame[0] += 1

        # spawn the child depth cam process 
        self.is_streaming = Value("i", True)
        self.frame_processed = Value("i", True)
        self.depth_cam_proc = Process(
            target=generate_frames,
            args=(self.frame_shm.name, shm_shape, self.frame_processed, self.is_streaming, FRAME_HEIGHT, FRAME_WIDTH),
        )
        self.depth_cam_proc.start()

        # create a QTimer to manage frame updates
        self.fps_timer = QtCore.QTimer()
        self.fps_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.fps_timer.timeout.connect(self.update_stream)
        self.fps_timer.setInterval(round(1000.0 / STREAM_FPS))
        self.fps_timer.start()
        
        # just for some stats  
        self.frameUpdateCount = 0
        self.stream_start_time = time.time()

    def update_stream(self):
        """
        Updates the GUI to display the current video frame.
        """        
        pix = frame_to_pixmap(self.current_frame[0])
        self.image_label.setPixmap(pix)
        self.frame_processed.value = True
        self.frameUpdateCount+= 1

    def closeEvent(self, event):
        """
        Overwrites systems "self.close" method so that the program can terminate properly
        Teardown all running threads and processes.
        """

        print(
            "Stream's Average FPS: %.2f"
            % (self.frameUpdateCount / (time.time() - self.stream_start_time))
        )

        # end depth cam process and wait for it to complete
        self.is_streaming.value = False
        self.depth_cam_proc.join()

        # free shared memory
        self.frame_shm.close()
        self.frame_shm.unlink()

