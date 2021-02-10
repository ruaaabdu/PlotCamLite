import pyrealsense2 as rs
import numpy as np
import cv2




pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
profile = pipeline.start(config)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()


try:
	i = 0
	while True:
		print ('Fetching aligned frames from stream...')
		frames = pipeline.wait_for_frames()
		#aligned_frames = align.process(frames)

		aligned_depth_frame = frames.get_depth_frame()
		color_frame = frames.get_color_frame()

		if not aligned_depth_frame or not color_frame:
			continue

		##print ('frame: ',frame_num)

		#apply the filters

		depth_image = np.asanyarray(aligned_depth_frame.get_data())

		num_rows = depth_image.shape[0]
		num_cols = depth_image.shape[1]

		print ('Re sampled frame size (r,c)=', (num_rows, num_cols))
		if i == 5:
			with open("fileahahah.txt", 'w') as outfile:
				for r in range(0, num_rows):
					for c in range(0, num_cols):
						#THE FOLLOWING CALL FAILS
						depth2 = aligned_depth_frame.as_depth_frame()
						depth = depth2.get_distance(c, r)
						outfile.write(str(depth))
						outfile.write("\n")
			break
		i = i + 1
except Exception as e: 
	print(str(e))