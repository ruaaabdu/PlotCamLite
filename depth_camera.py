import cProfile
from multiprocessing import shared_memory

import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import pyrealsense2 as rs
TEST_VIDEO_PATH = "ITADOZO.mp4"


def frame_to_pixmap(color_image):
    """
    Returns QPixmap from numpy array image.
    :param color_image: the image to convert
    :type color_image: 3d numpy uint8 array
    """    
    height, width, channel = color_image.shape
    bytes_per_line = channel * width

    q_img = QImage(
        color_image.data, width, height, bytes_per_line, QImage.Format_BGR888
    )
    return QPixmap.fromImage(q_img)


def generate_frames(
    shared_mem_name,
    buffer_shape,
    frame_processed,
    is_streaming,
    rs_width=640,
    rs_height=480,
):
    """
    Depth Camera Video Feed Process.
    Configures RealSense Depth Camera for stream in an isolated process.
    Updates the shared memory with most recent frame whenever one arrives.

    :param shared_mem_name: name of shared memory, i.e. its identifier
    :param buffer_shape: tuple represents the dimensons of the array backed by the shared memory
    :param frame_processed: shared boolean variable signifies when the last frame has been processed, i.e. safe to post a new one
    :type is_streaming: multiprocessing.Value
    :param is_streaming: shared boolean variable signifies when to end the stream
    :type is_streaming: multiprocessing.Value
    """
    with cProfile.Profile() as pr:

        # prepare shared memory to be used as a frame buffer
        existing_shm = shared_memory.SharedMemory(name=shared_mem_name)
        next_frame = np.ndarray(buffer_shape, dtype=np.uint8, buffer=existing_shm.buf)

        # configure realsense pipeline and start recording
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, rs_width, rs_height, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        pipeline.start(config)
        print("started pipeline")

        # open test video
        # vid = cv2.VideoCapture(TEST_VIDEO_PATH)

        # camera feed loop
        fIx = 0
        while is_streaming.value:  # while write pipe is open
            # grab frames from the camera
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # ret, color_image = vid.read()
            # if not ret:
            #     print("failed :[")
            #     continue
            color_image = np.asanyarray(color_frame.get_data())

            # put the rotated frame's ndarray in shared memory
            # wait for the consumer process to consume the frame before overwriting it
            # busy wait spin lock alert, TODO make this a mutex
            while not frame_processed.value and is_streaming.value:
                pass
                # print("waiting for frame to be processed")

            # the 0 index hard coded cus only using array of one element
            next_frame[0] = np.rot90(color_image, 1).copy()
            frame_processed.value = False

    existing_shm.close()

    # pr.print_stats()
