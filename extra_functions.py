####################################################
# plot_cam_lite.py v0.1
# Extra Functions
####################################################

import pyrealsense2 as rs

import logging

import os

def get_number_of_cameras():
    """Returns the number of cameras connected to the OS

    Returns:
        int: number of Intel RealSense cameras connected
    """
    ctx = rs.context()
    num_cameras = len(ctx.devices)
    return num_cameras

def get_camera_serial():
    ctx = rs.context()
    camera_serials = []
    if len(ctx.devices) > 0: 
        for d in ctx.devices:
            #print ('Found device: ', d.get_info(rs.camera_info.name), ' ', d.get_info(rs.camera_info.serial_number))
            camera_info = (d.get_info(rs.camera_info.name), d.get_info(rs.camera_info.serial_number))
            camera_serials.append(camera_info)
            return camera_serials
    else:
        #print("No Intel Device connected")
        return None

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
