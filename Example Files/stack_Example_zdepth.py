

import pyrealsense2 as rs
import numpy as np
import cv2
pipeline = rs.pipeline()
config = rs.config()
profile = pipeline.start(config)
frames = pipeline.wait_for_frames()
try:
    i = 0
    while True:
        if i == 5:
            with open("fileahahah.txt", 'w') as outfile:
                for r in range(0, 640):
                    for c in range(0, 480):
                        depth_frame = frames.get_depth_frame()
                        zDepth = depth_frame.get_distance(c, r)
                        outfile.write(str(zDepth))
                        outfile.write("\n")
            break
        i = i + 1
finally:
    pipeline.stop()