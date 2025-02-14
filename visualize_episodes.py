import argparse
import os

import h5py
import cv2
from matplotlib import pyplot as plt
import numpy as np

FPS = 30
JOINT_LEGEND = ("joint 1", "joint 2", "joint 3", "joint 4", "joint 5", "joint 6")
END_POSE_LEGEND = ("X", "Y", "Z", "RX", "RY", "RZ")

def find_dataset(episode_name):
    dataset_path = os.path.join('/home/islab/islab_ws/ISLRO/dataset', f'episode_{episode_name}.h5')
    if not os.path.exists(dataset_path):
        print(f'Dataset {dataset_path} not found.')
        return False

    return dataset_path

def plot_robot(robot_data, episode_name):
    print(f'Plotting episode_{episode_name}.png')

    joint_data = robot_data["joint_data"]
    end_pose_data = robot_data["end_pose_data"]
    gripper_data = robot_data["gripper_data"]

    plt.figure(figsize=(10, 10))

    plt.subplot(2,2,1)
    x = range(joint_data.shape[0])
    joint_num = joint_data.shape[1]
    for i in range(joint_num):
        plt.plot(x,joint_data[:,i])
    joint_legend = JOINT_LEGEND
    plt.grid(True)
    plt.legend(joint_legend)

    plt.subplot(2,2,2)
    x = range(end_pose_data.shape[0])
    end_pose_num = end_pose_data.shape[1]
    for i in range(end_pose_num):
        plt.plot(x,end_pose_data[:,i])
    end_pose_legend = END_POSE_LEGEND
    plt.grid(True)
    plt.legend(end_pose_legend)

    plt.subplot(2,2,3)
    x = range(gripper_data.shape[0])
    gripper_num = gripper_data.shape[1]
    gripper_legend = ["gripper angle", "gripper effort"]
    for i in range(gripper_num):
        plt.plot(x,gripper_data[:,i])
    plt.grid(True)
    plt.legend(gripper_legend)

    ax = plt.subplot(2, 2, 4, projection='3d')
    x_coor = end_pose_data[:, 0]
    y_coor = end_pose_data[:, 1]
    z_coor = end_pose_data[:, 2]
    ax.scatter(x_coor, y_coor, z_coor, s= 1)
    ax.set_xlim([-500000, 500000])
    ax.set_ylim([-500000, 500000])
    ax.set_zlim([-500000, 500000])
    plt.grid(True)

    save_path = f'/home/islab/islab_ws/ISLRO/dataset/episode_{episode_name}.png'
    plt.savefig(save_path)
    # plt.show()
    print(f'Saved episode_{episode_name}.png')


def save_video(image_data, episode_name):
    print(f'Saving episode_{episode_name}_RGB.mp4 and episode_{episode_name}_gray.mp4')

    seq_length = image_data.shape[0]

    image_rgb = image_data[:,:,:,:3]
    image_gray = image_data[:,:,:,-1]

    height, width = int(image_rgb.shape[1]), int(image_rgb.shape[2])

    rgb_video_filename = f"dataset/episode_{episode_name}_RGB.avi"
    gray_video_filename = f"dataset/episode_{episode_name}_gray.avi"

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = FPS
    size = (width, height)

    rgb_video = cv2.VideoWriter(rgb_video_filename, fourcc, fps, size)
    gray_video = cv2.VideoWriter(gray_video_filename, fourcc, fps, size)

    for i in range(seq_length):
        rgb_frame = image_rgb[i]
        gray_frame = image_gray[i]

        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        bgr_frame = bgr_frame.astype(np.uint8)
        gray_frame = gray_frame.astype(np.uint8)

        # if i == 10:
        #     cv2.imwrite(f"test_{i}.jpg", bgr_frame)
        #     print(rgb_frame.shape)
        #     print(width, height)

        rgb_video.write(bgr_frame)
        gray_video.write(gray_frame)

    rgb_video.release()
    gray_video.release()
    print(f'Saved episode_{episode_name}_RGB.avi and episode_{episode_name}_gray.avi')


def main(args):
    episode_name = args['episode_name']

    dataset_path = find_dataset(episode_name)
    with h5py.File(dataset_path, 'r') as f:
        joint_data = np.array(f["robot"]["joint_data"])
        end_pose_data = np.array(f["robot"]["end_pose_data"])
        gripper_data = np.array(f["robot"]["gripper_data"])
        image_data = np.array(f["image"]["image_data"])

        # print("joint_data : ", joint_data)
        # print("end_pose_data : ", end_pose_data)
        # print("gripper_data : ", gripper_data)
        # print("image_data : ", image_data)

    robot_data = {
        "joint_data": joint_data,
        "end_pose_data": end_pose_data,
        "gripper_data": gripper_data,
    }

    plot_robot(robot_data, episode_name)
    save_video(image_data, episode_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_name', type=str, required=True)
    main(vars((parser.parse_args())))

    # args = {
    #     'episode_name': 'tutorial',
    # }
    # main(args)
