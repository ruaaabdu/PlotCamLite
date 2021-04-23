"""
Main GUI of the PlotCamLite copyright LLC all rights reserved.
"""
import logging
import os
import time
import multiprocessing
from multiprocessing import Process, Value, shared_memory
from datetime import datetime
from ntpath import basename
import numpy as np

from Phidget22.Devices.Accelerometer import *
from Phidget22.Phidget import *

from PyQt5 import QtCore
from PyQt5.QtCore import QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QGridLayout, QMainWindow, QSizePolicy, QWidget, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtMultimedia import QSound

from util import (ACCELEROMETER_PERIOD_MS, FRAME_NCHANNELS, ICON_IMAGE_PATH, ALERT_AUDIO_PATH,
                  LEVEL_TOLERANCE, PCL_EXP_PATH, PLATFORM, PLOT_NUMBER_PADDING,
                   SM_BUF_SIZE, TARGET_ICON_PATH, disable_logging,
                  frame_to_pixmap, within_tolerance, pcl_config)

from .depth_camera_feed import generate_frames
from .metadata import Metadata
from .new_experiment_dialog import NewExperimentPage
from .target import Target


log = logging.getLogger("pcl_mainwindow")

class PlotCamLiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # init variables
        self.depth_cam_proc = None
        self.accelerometer = None
        self.metadata = None

        self.experiment_path = None
        self.is_streaming = multiprocessing.Value('i', False)

        self.current_plot_number = 0
        self.x = 0.0
        self.y = 0.0

        self.init_ui()
        self.title = "PlotCam Lite - %s and PyQt5" % PLATFORM

    def init_ui(self):
        """
        Initalizes the UI.
        Connects methods to the buttons and begins the background processes.
        """
        if pcl_config["vr"]:
            self.setFixedSize(850,630)

        with disable_logging(logging.DEBUG):
            loadUi(pcl_config["main_window_ui_path"], self)

        self.setWindowIcon(QIcon(ICON_IMAGE_PATH))
        # Start the camera stream
        self.start_stream()

        # Start the accelerometer
        self.start_accelerometer()

        # Connect buttons to methods
        self.take_picture_button.clicked.connect(self.take_picture)
        self.exit_button.clicked.connect(self.close)
        self.new_file_button.clicked.connect(self.new_experiment_dialog)

        self.load_experiment_button.clicked.connect(self.browse_files)

        # disable the take pic btn until an experiment is set
        self.take_picture_button.setEnabled(False)

        self.alert = QSound(ALERT_AUDIO_PATH)

    def start_stream(self):
        """
        Start the camera stream.
        Creates a seperate process for the stream, and interacts with the frames through shared memory.
        Uses a QTimer to maintain a stable frame rate.
        """
        # grab config variables
        STREAM_HEIGHT = pcl_config["stream_height"]
        STREAM_WIDTH = pcl_config["stream_width"]
        STREAM_FPS = pcl_config["stream_fps"]

        # set up the label
        camera_size_policy = QSizePolicy(STREAM_WIDTH, STREAM_HEIGHT)
        self.camera_label.setSizePolicy(camera_size_policy)

        # create shared memory to hold a single frame for inter process communication,
        # wrap it in a numpy array
        nbyte_per_frame = STREAM_WIDTH * STREAM_HEIGHT * FRAME_NCHANNELS # bytes in a frame
        log.debug("Allocating %i x %i bytes of shared memory"% (SM_BUF_SIZE, nbyte_per_frame))
        self.frame_shm = shared_memory.SharedMemory(create=True, size=nbyte_per_frame*SM_BUF_SIZE)
        shm_shape = (SM_BUF_SIZE, STREAM_HEIGHT, STREAM_WIDTH, FRAME_NCHANNELS)
        self.frame_buffer = np.ndarray(shm_shape, dtype=np.uint8, buffer=self.frame_shm.buf)

        # spawn the child depth cam process
        self.frame_in_use = Value("i", False)
        self.pending_frame = Value("i", False)
        read_pipe, write_pipe = multiprocessing.Pipe()
        self.camera_communication_pipe = write_pipe
        self.depth_cam_proc = Process(
            target=generate_frames,
            args=(
                self.frame_shm.name,
                shm_shape,
                STREAM_HEIGHT,
                STREAM_WIDTH, 
                STREAM_FPS,
                self.frame_in_use,
                self.pending_frame,
                read_pipe,
                self.is_streaming
            ),
        )
        self.depth_cam_proc.start()
        log.info("Created depth camera process, pId = %i" %self.depth_cam_proc.pid)

        # create a QTimer to manage frame updates
        self.fps_timer = QtCore.QTimer()
        self.fps_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.fps_timer.timeout.connect(self.update_stream)
        self.fps_timer.setInterval(round(1000.0 / STREAM_FPS))
        self.fps_timer.start()
        log.debug("Timer limiting FPS to %i" %STREAM_FPS)

        # just for some stats
        self.frameUpdateCount = 0
        self.stream_start_time = time.time()

        # for camera depending on accelerometer
        self.waitingForLevel = False

    def update_stream(self):
        """
        Updates the GUI to display the current video frame.
        """
        self.frame_in_use.value = True
        pix = frame_to_pixmap(self.frame_buffer[0])
        self.camera_label.setPixmap(pix)
        self.frame_in_use.value = False
        self.frameUpdateCount += 1

    def take_picture(self):
        """
        Notifies camera process to save the next frame.
        Disables the take picture button & posts the image name and experiment path onto the shared pipe.
        (SUS) Waits till image is saved to enable the button again.
        """
        
        if not self.is_streaming.value:
            log.info("Cant save pic - no stream !!")
            return

        # disable take pic btn until its done 
        self.take_picture_button.setEnabled(False)

        if not within_tolerance(self.x, self.y, LEVEL_TOLERANCE):
            log.info("Waiting till camera is level to take the picture")
            self.waitingForLevel = True
            return

        # write save image info to pipe
        plot_num_str = str(self.current_plot_number).zfill(PLOT_NUMBER_PADDING)
        img_name = "%s_%s" % (self.experiment_name, plot_num_str)
        log.debug("Queueing image <%s> to be saved..." %img_name)
        self.pending_frame.value = True
        self.camera_communication_pipe.send((self.experiment_path, img_name)) 

        # wait for image to be saved
        while (self.pending_frame.value):
            pass
        
        self.update_metadata()
        self.save_metadata()
            # resume normal operations
        log.debug("Image <%s> successfully saved" %img_name)
        self.update_plot_number(self.current_plot_number + 1)
        self.take_picture_button.setEnabled(True)

        self.alert.play()
        
        self.waitingForLevel = False


       
    def start_accelerometer(self):
        """
        Creates Phidget22 accelerometer and polls it at a fixed rate using a QTimer.
        """
        # set up the target image
        self.setup_target()

        # create the accelerometer, and wait 1 sec for connection
        # TODO does the open wait for attachment throw an error
        try:
            self.accelerometer = Accelerometer()
            self.accelerometer.openWaitForAttachment(1000)
            log.info("Created accelerometer")
        except:
            log.warning("No accelerometer connected")
            self.accelerometer = None
            return


        # create QTimer to periodically monitor the acceleration
        self.accelerometer_timer = QtCore.QTimer()
        self.accelerometer_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.accelerometer_timer.timeout.connect(self.update_target)
        self.accelerometer_timer.setInterval(ACCELEROMETER_PERIOD_MS)
        self.accelerometer_timer.start()
        log.debug("Timer limiting accelerometer update frequency to %f Hz" % (1000.0/ACCELEROMETER_PERIOD_MS))

    def setup_target(self):
        """
        Sets up the target graphic of the GUI.
        """        
        self.wrapper = QWidget()
        self.target_layout = QGridLayout()
        self.target_layout.addWidget(self.wrapper)
        self.target_widget.setLayout(self.target_layout)
        self.target = Target()
        self.target.pixmap = QPixmap(TARGET_ICON_PATH)
        self.target.setGeometry(40, 0, 150, 150)
        self.target.setParent(self.wrapper)
        self.target.show()

    def update_target(self):
        """
        Update the coordinate on the GUI's target.
        """
        # TODO try-catch error
        acceleration = self.accelerometer.getAcceleration()

        

        self.x = acceleration[0]
        self.y = acceleration[1]

        self.target.coordinate = QPointF(self.x, self.y)
        if within_tolerance(self.x, self.y, LEVEL_TOLERANCE):
            if self.waitingForLevel:
                self.take_picture()
            self.camera_level_label.setText("Camera is Level")
            self.camera_level_label.setStyleSheet("color: green;")
        else:
            self.camera_level_label.setText("Camera is not Level")
            self.camera_level_label.setStyleSheet("color: red;")


    def new_experiment_dialog(self):
        """
        Open the "New Experiment" Dialog and connect methods to update file name and plot number labels.
        """
        new_exp_page = NewExperimentPage()
        new_exp_page.expirementCreated.connect(self.update_experiment)
        new_exp_page.changePlotNumber.connect(self.update_plot_number)
        new_exp_page.exec_()
        new_exp_page.show()

    def browse_files(self):
        """
        Opens up experiment folder directory so that an existing experiment can be chosen
        """
        loaded_filename = QFileDialog.getExistingDirectory(self, 'Select Experiment Folder', PCL_EXP_PATH)
        self.update_experiment(basename(loaded_filename))

    @pyqtSlot(str)
    def update_experiment(self, new_exp_name):
        """
        Updates the working experiment.
        Modifys all relevant variables and paths. 
        Sets up metadata to be periodically saved to file.
        Enables button if experiment is set.
        Args:
            new_exp_name (str): The new experiment name
        """

        # make sure this is a valid experiment before updating
        new_exp_path = os.path.join(PCL_EXP_PATH, new_exp_name)
        if not self.validate_experiment(new_exp_path):
            return

        self.experiment_name = new_exp_name
        self.file_name_label.setText(self.experiment_name)
        self.experiment_path = new_exp_path

        # save old metadata before opening new experiment
        self.save_metadata()
        metadata_path = os.path.join(self.experiment_path, "Metadata", "%s.json" % self.experiment_name)
        self.metadata = Metadata(metadata_path)
        last_index = self.metadata.get_last_index()

        if last_index != -1:
            self.update_plot_number(last_index + 1)

        self.take_picture_button.setEnabled(True)

        log.info("Opened experiment %s" %self.experiment_name)

    def validate_experiment(self, exp_path):
        """
        Validates experiment at the given path.
        If no experiment exists or the experiment structure is faulty,
        Displays an error message dialog.

        Args:
            exp_path (path): path to a plotcam experiment
        Returns:
            bool: true if experiment is valid
        """
        # TODO would u want to create RGB and depth folders if they r missing
        valid = True
        errorMsg = ""
        if not os.path.exists(exp_path):
            valid = False
            errorMsg = "No experiment at %s" % exp_path
        elif not os.path.exists(os.path.join(exp_path, "Depth")):
            valid = False
            errorMsg = "Experiment missing depth data directory"
        elif not os.path.exists(os.path.join(exp_path, "RGB")):
            valid = False
            errorMsg = "Experiment missing rgb data directory"

        # dont need to validate metadata, the path will be created if it doenst exist on update exp
        if not valid:
            # error pop up
            log.info(errorMsg)
            pass

        return valid

    @pyqtSlot(int)
    def update_plot_number(self, new_plot_number):
        """ 
        Updates plot number.

        Args:
            new_plot_number (int): The new plot number
        """
        self.plot_number_label.setText("Plot #: " + str(new_plot_number).zfill(PLOT_NUMBER_PADDING))
        self.current_plot_number = new_plot_number

    def update_metadata(self):
        """ 
        Updates metadata with new entry.
        """        
        num = str(self.current_plot_number).zfill(PLOT_NUMBER_PADDING)
        t = datetime.now().strftime('%H:%M:%S')
        date = datetime.now().strftime('%d/%m/%Y')
        name = self.experiment_name
        self.metadata.add_entry(num, t, date, self.x, self.y, name)

    def save_metadata(self):
        """
        Saves the metadata file to disk.
        """        
        if self.metadata is None:
            return
            
        log.info("Saving metadata")
        self.metadata.save()

    def closeEvent(self, event):
        """ 
        Overrides systems "self.close" method so that the program can terminate properly.
        Teardown all running threads and processes.
        """
        # tear down accelerometer
        if self.accelerometer:
            pass

        # tear down camera process
        if self.depth_cam_proc:
            log.debug(
                "Stream's Average FPS: %.2f"
                % (self.frameUpdateCount / (time.time() - self.stream_start_time))
            )

            # end depth cam process and wait for it to complete
            # TODO end the fps Qtimer
            self.is_streaming.value = False
            self.frame_in_use.value = False
            self.depth_cam_proc.join()

            # free shared memory
            self.frame_shm.close()
            self.frame_shm.unlink()
            log.info("Terminated camera process")  

        log.info("PlotCamLite says goodbye :[")