"""
This code handles the stream functions
@author Ruaa Abdulmajeed
@date April 30th, 2021
"""

import os
from multiprocessing import Pool, shared_memory, Queue
import numpy as np
from PIL import Image
import cv2

def generate_frames(shared_mem_name, buffer_shape, width, height, fps, frame_in_use, pending_frame, gui_communication_pipe, is_streaming):
    """
    Depth Camera Video Feed Process.
    Configures RealSense Depth Camera for stream in an isolated process.
    Updates the shared memory with most recent frame whenever one arrives.
    Facilitates saving of frames upon request using a multiproc Pool.

    Args:
        shared_mem_name (string): name of shared memory block
        buffer_shape (tuple): dimensions of the array backed by the shared memory
        width (string): width of the stream
        height (tuple): height of the stream
        fps (int): frames per seconds
        frame_in_use (multiprocessing.Value): shared boolean variable, pseudo mutex 
        pending_frame(multiprocessing.Value): shared boolean variable, true if a frame needs saving
        gui_communication_pipe (multiprocessing.Connection): read pipe that holds information on saving frames
        is_streaming (multiprocessing.Value): shared boolean variable signifies when to end the stream
    """
    # import in seperate process to avoid runtime COM error
    import pyrealsense2 as rs
    

    # prepare shared memory to be used as a frame buffer
    existing_shm = shared_memory.SharedMemory(name=shared_mem_name)
    frame_buf = np.ndarray(buffer_shape, dtype=np.uint8, buffer=existing_shm.buf)
    if len(rs.context().devices) > 0: # only start stream if camera connected
        
        # configure realsense pipeline and start recording
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        pipeline.start(config)
        print("started pipeline")

        # camera feed loop
        fIx = 0
        prev_frames = None
        is_streaming.value = True
        while is_streaming.value:

            # grab frames from the camera
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if not color_frame and not depth_frame:
                continue
            color_arr = np.asanyarray(color_frame.get_data())

            # wait for the consumer to process frame before overwriting it
            while frame_in_use.value:
                pass
            
            # handle save frame requests
            if gui_communication_pipe.poll() and prev_frames:
                exp_path, img_name = gui_communication_pipe.recv()

                # TODO find the latency of this func, if the stream is heavily interrupted (in a way we dont want)
                # then can rework the frame saving into a thread
                save_depth_images(prev_frames, exp_path, img_name)
                pending_frame.value = False # let em know its done saving

            # put the rotated frame's ndarray in shared memory
            frame_buf[fIx] = np.rot90(color_arr, 1).copy()
            fIx = (fIx + 1) % buffer_shape[0]  # 0 index is the buf size
            prev_frames = frames
        
        pipeline.stop()
    else:
        print("There is no camera connected")

    is_streaming.Value = False

    # cleanup pipe
    if gui_communication_pipe.poll():
        gui_communication_pipe.recv()
    gui_communication_pipe.close()

    # free shared memory
    existing_shm.close()

def save_depth_images(frames, experiment_path, image_name):
    """Saves RGB image and Depth data.

    Args:
        experiment_path (str): Directory of experiment that images belong to
        image_name (str): Root name to save images as, file extension will be tacked on
    """
    # grab the frames
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # grab the file names
    color_fname = os.path.join(experiment_path, "RGB", image_name + ".bmp")
    depth_fname = os.path.join(experiment_path, "Depth", image_name + ".txt")

    # represent them as numpy arrays
    color_arr = np.asanyarray(color_frame.get_data())
    depth_arr = np.asanyarray(depth_frame.get_data())

    # rotate them
    # convert BGR to RGB by rotating the channels
    color_arr = np.rot90(color_arr, 1).copy()[:, :, ::-1] 
    depth_arr = np.rot90(depth_arr, 1).copy()
    
    # to save depth in m, uncomment line below
    #     depth_arr = depth_arr/1000

    # save them
    Image.fromarray(color_arr, "RGB").save(color_fname)
    np.savetxt(depth_fname, depth_arr, fmt="%.3f \n", newline='')

# TODO find a way to do this, no import
def get_number_of_cameras():
    """Returns the number of cameras connected to the OS

    Returns:
        int: number of Intel RealSense cameras connected
    """
    import pyrealsense2 as rs
    ctx = rs.context()
    num_cameras = len(ctx.devices)
    return num_cameras


def get_camera_serial():
    import pyrealsense2 as rs
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