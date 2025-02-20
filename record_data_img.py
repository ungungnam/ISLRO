##########Image Recording with RealSense L515##########

import numpy as np
import cv2


def record_real_data_img(pipeline):
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    color_image = cv2.resize(color_image, (depth_image.shape[1], depth_image.shape[0]))
    # depth_image = np.expand_dims(depth_image, axis=2)
    # image_data = np.concatenate((color_image, depth_image), axis=2)

    # print(depth_image.shape)
    # print(color_image.shape)
    # print(image_data.shape)
    # return image_data
    # print(depth_image)
    return [color_image, depth_image]