import pyrealsense2 as rs

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