####################################################
# util.py v0.1
####################################################
"""
This code stores constant variables and important paths so that they are easily accessible.
@author Ruaa Abdulmajeed
@date February 24th, 2021
"""

import logging
import os
from argparse import ArgumentParser
from contextlib import contextmanager

from PyQt5.QtGui import QImage, QPixmap, QFont



# VARIABLES
# System info
# Root Directories
PCL_SRC_PATH = os.path.dirname(os.path.realpath(__file__)) # where all the code is loaded
PCL_EXP_PATH = os.path.join(PCL_SRC_PATH, "experiments") # path to pcl experiments. doesnt have to be relative to source dir.
ICON_IMAGE_PATH = os.path.join(PCL_SRC_PATH, "resources", "icons", "cameraleaf.png")
TARGET_ICON_PATH = os.path.join(PCL_SRC_PATH, "resources", "icons", "target_png_375.png")
ALERT_AUDIO_PATH = os.path.join(PCL_SRC_PATH, "resources", "audio", "camera-shutter-click.wav")
ABOUT_DIALOG_PATH = os.path.join(PCL_SRC_PATH, "resources", "ui", "PlotCamLiteUI_AboutDialog.ui")

FRAME_NCHANNELS = 3 # number of channels in the image

SM_BUF_SIZE = 1  # num of frames to store in shared memory

PLOT_NUMBER_PADDING = 3  # How many numbers the plot number must occupy, for example 1 will need to be 001 and 11 will need to be 011

LEVEL_TOLERANCE = 0.2  # the absolute value which the accelerometer must return for the camera to be level
ACCELEROMETER_PERIOD_MS = 50  # in ms, how frequent the accelerometer is read

IMG_SAVE_REQ_Q_SIZE = 100  # max size of queue storing pending frames to save.
NWORKERS = 5  # num of worker processes crunching thru the frames-to-save queue.

METADATA_UPDATE_PERIOD_SEC = 60  # save metadata to disk every minute

DEFAULT_FONT = QFont('Times', 15)

# String constants
LOG_FILENAME = "plotcamlite_log.txt"
PLOT_NUM_DEFAULT_TEXT = "Enter Plot Number here"
PLATFORM = "Windows"  # TODO theres a command like get_os u can call to automatically tell u


# for variables which can change
pcl_config = {"vr": False,
                "platform" : "Windows",
                "main_window_ui_path" : os.path.join(PCL_SRC_PATH, "resources", "ui", "PlotCamLiteUI_monitor.ui"), 
                "stream_width" : 720,
                "stream_height" : 1280,
                "stream_fps": 30} # frame rate limiter 


resolution_width = {1280:720, 640:480} # dict to resolve resolutions


# Utility functions
def configure_plotcamlite():
    """
    Configures the PlotCamLite.
    Retrieve PlotCamLite configuration info from command line arguments, and configures Logging according to input.
    Creates the PCL_EXP_PATH directory if doesnt exist.
    """

    # command line argument parsing
    parser = ArgumentParser(
        prog="python plotcam-lite.py",
        description="PlotCamLite (2021). Realtime plot monitoring system. By Rua'a Abdulmajeed, PhD in parsley agriculture.")


    # running on headset or not
    parser.add_argument(
        '-vr',
        dest="vr",
        action='store_true',
        help="add this option for it to format properly on VR headset",
    )

    # change stream resolution
    parser.add_argument(
        '-res',
        dest="res",
        type=int,
        default=1280,
        choices=[1280, 640],
        help="change the stream's resolution, either 1280x720(default) or 640x480",
    )

    # change the stream fps
    parser.add_argument(
        '-fps',
        dest="fps",
        type=int,
        default=30,
        choices=[15, 30],
        help="set the stream's fps, either 15 or 30",
    )

    # Log Level
    parser.add_argument(
        '-l', '--log',
        dest="log_level",
        type=str,
        default=None,
        choices=["debug", "info", "warning", "error"],
        help="specify level of logging, defaults to no logging",
    )

    args = parser.parse_args()

    # handle VR 
    pcl_config["vr"] = args.vr
    if pcl_config["vr"]:
        pcl_config["main_window_ui_path"] = os.path.join(PCL_SRC_PATH, "resources", "ui", "PlotCamLiteUI_VR.ui")
            
    # handle fps
    pcl_config["stream_fps"] = args.fps

    # handle resolution
    pcl_config["stream_height"] = args.res
    pcl_config["stream_width"] = resolution_width[pcl_config["stream_height"]]

    # handle logging
    configure_logging(log_level=args.log_level, log_fpath=os.path.join(PCL_SRC_PATH, LOG_FILENAME))

    # create the main path directory
    if not os.path.exists(PCL_EXP_PATH):
        os.makedirs(PCL_EXP_PATH)


def configure_logging(log_level=None, log_fpath=None):
    """
    Configures logging globally through root logger.
    If no log_level specified, logging will be disabled.
    Logs print to console, if log file specified logs will be written there as well.
    Args:
        log_level (str): log_level, one of [debug, info, warning, critical]
        log_fpath (str): path to write logs to.
    """

    # disable logging
    if not log_level:
        logging.disable()
        return

    log_level = log_level.upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # create formatter for the logs
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s")

    # create console logging handler and set its formatting, add it to the root logger
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

    # create file logging handler and set its formatting, add it to the root logger
    if log_fpath:
        fh = logging.FileHandler(log_fpath)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        root_logger.addHandler(fh)

    # print first log
    if log_fpath is None:
        root_logger.info("First log: logging to console at %s level." % logging.getLevelName(root_logger.getEffectiveLevel()))
    else:
        root_logger.info("First log: logging to console and %s at %s level" %(log_fpath, logging.getLevelName(root_logger.getEffectiveLevel())))

@contextmanager
def disable_logging(log_level):
    """
    Context manager to disable logging for a region of code.
    Args:
        log_level: level of log to be ignored
    """    
    try:  
        logging.disable(log_level)
        yield
    finally:
        logging.disable(logging.NOTSET)
            
def frame_to_pixmap(color_image):
    """
    Converts image frame to QPixmap
    Args:
        color_image (ndarray): BGR frame in array format

    Returns:
        QPixmap: image as a QPixmap
    """    
    height, width, channel = color_image.shape
    bytes_per_line = channel * width

    q_img = QImage(color_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
    return QPixmap.fromImage(q_img)

# TODO is this meant to be an "is in circle" check?
def within_tolerance(x, y, tolerance):
    """
    Tests whether position is within the given tolerance

    Args:
        x (float): position's x coordinate
        y (float): position's y coordinate
        tolerance (float): tolerance level

    Returns:
        bool: true if the position is within the tolerance
    """    
    return abs(x) <= tolerance and abs(y) <= tolerance