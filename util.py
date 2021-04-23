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
PLATFORM = "Windows"  # TODO theres a command like get_os u can call to automatically tell u

# Root Directories
PCL_SRC_PATH = os.path.dirname(os.path.realpath(__file__)) # where all the code is loaded
PCL_EXP_PATH = os.path.join(PCL_SRC_PATH, "experiments") # path to pcl experiments. doesnt have to be relative to source dir.

# Relative Paths
MAIN_WINDOW_UI_PATH = os.path.join(PCL_SRC_PATH, "resources", "ui", "PlotCamLiteUI_monitor.ui")
ICON_IMAGE_PATH = os.path.join(PCL_SRC_PATH, "resources", "icons", "cameraleaf.png")
TARGET_ICON_PATH = os.path.join(PCL_SRC_PATH, "resources", "icons", "target_png_375.png")
ALERT_AUDIO_PATH = os.path.join(PCL_SRC_PATH, "resources", "audio", "bell_alert.wav")

# Constants
QT_FEED_WIDTH = 720 # width of the QT video image
QT_FEED_HEIGHT = 1280 # height of the QT video image
FRAME_NCHANNELS = 3 # number of channels in the image
NBYTE_PER_FRAME = QT_FEED_WIDTH * QT_FEED_HEIGHT * FRAME_NCHANNELS # bytes in a frame
SM_BUF_SIZE = 1  # num of frames to store in shared memory
QT_STREAM_FPS = 15 # frame rate limiter for the QT GUI
PLOT_NUMBER_PADDING = 3  # How many numbers the plot number must occupy, for example 1 will need to be 001 and 11 will need to be 011

LEVEL_TOLERANCE = 0.2  # the absolute value which the accelerometer must return for the camera to be level
ACCELEROMETER_PERIOD_MS = 50  # in ms, how frequent the accelerometer is read

IMG_SAVE_REQ_Q_SIZE = 100  # max size of queue storing pending frames to save.
NWORKERS = 5  # num of worker processes crunching thru the frames-to-save queue.
RS_FEED_WIDTH = 1280
RS_FEED_HEIGHT = 720
RS_STREAM_FPS = 15

METADATA_UPDATE_PERIOD_SEC = 60  # save metadata to disk every minute

DEFAULT_FONT = QFont('Times', 15)

# String constants
LOG_FILENAME = "plotcamlite_log.txt"
PLOT_NUM_DEFAULT_TEXT = "Enter Plot Number here"

# Advanced variables
sampleMetaData = {
    "time": "10:24:26 AM",
    "air": "20.9",
    "light": "306",
    "lattitude": "45.234008",
    "longitude": "75.42955",
    "battery": "13.0",
    "zeroingvalue": "1754",
    "plantheight": "665",
}


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
