import argparse
import os
import json
import pickle
from tqdm import tqdm
import h5py

import pyrealsense2 as rs

from piper_sdk import *
from record_data_joint import *
from record_data_img import *
from constants import *
from data_utils import *

def capture_episode(task_config, episode_name):
    piper = C_PiperInterface("can0")
    piper.ConnectPort()

    pipeline = rs.pipeline()
    rs_config = rs.config()

    rs_config.enable_stream(rs.stream.depth,)
    rs_config.enable_stream(rs.stream.color,)

    pipeline.start(rs_config)

    dataset_dir = task_config["DATASET_DIR"]
    if not os.path.isdir(dataset_dir):
        os.makedirs(dataset_dir)

    episode_len = task_config["EPISODE_LEN"]
    fps = task_config["FPS"]

    # create folder where data is saved
    try:
        if not os.path.exists(f"{dataset_dir}/{episode_name}"):
            os.makedirs(f"{dataset_dir}/{episode_name}")
    except OSError:
        print(f"Error: Creating directory. {episode_name}")


    dt = 1 / fps
    max_timestep = episode_len * fps
    # dataset = []
    robot_dataset = []
    image_dataset = []

    record_robot_time = []
    record_image_time = []

    t_start = time.time()
    for t in tqdm(range(max_timestep)):
        t0 = time.time()
        robot = record_real_data_joint(piper)
        t_robot = time.time()
        image_data = record_real_data_img(pipeline)
        # image = record_real_data_img(pipeline)
        t1 = time.time()

        record_robot_time.append(t_robot-t0)
        record_image_time.append(t1-t_robot)

        robot_data = {
            "index": t,
            "timestamp": t1-t_start,
            "robot": robot,
            # "image": image,
        }
        # dataset.append(robot_data)
        robot_dataset.append(robot_data)
        image_dataset.append(image_data)

        time.sleep(max(0, dt - (time.time() - t0)))

    print(f"average time on recording robot data : {np.mean(record_robot_time)}")
    print(f"average time on recording image data : {np.mean(record_image_time)}")

    save_episode(robot_dataset, image_dataset, episode_name)
    # with h5py.File(dataset_dir + f"/episode_{episode_name}.h5", "w") as f:
    #     robot_group = f.create_group("robot")
    #     image_group = f.create_group("image")
    #
    #     index, timestamp_data = [], []
    #     joint_data, end_pose_data, gripper_data, image_data = [], [], [], []
    #     while dataset:
    #         data = dataset.pop(0)
    #
    #         idx = data["index"]
    #         timestamp = data["timestamp"]
    #
    #         joint = data["robot"]["joint_data"]
    #         end_pose = data["robot"]["end_pose_data"]
    #         gripper = data["robot"]["gripper_data"]
    #         image = data["image"]
    #
    #         timestamp_data.append(timestamp)
    #         joint_data.append(joint)
    #         end_pose_data.append(end_pose)
    #         gripper_data.append(gripper)
    #         image_data.append(image)
    #
    #     f.create_dataset(name=f"timestamp", data=timestamp_data)
    #     robot_group.create_dataset(name=f'joint_data', data=joint_data)
    #     robot_group.create_dataset(name=f'end_pose_data', data=end_pose_data)
    #     robot_group.create_dataset(name=f'gripper_data', data=gripper_data)
    #     image_group.create_dataset(name=f'image_data', data=image_data)

    return True


def main(args):
    episode_len = args['episode_len']
    episode_name = args['episode_name']

    task_config = config()
    task_config['EPISODE_LEN'] = episode_len

    while True:
        is_healthy = capture_episode(task_config, episode_name)
        if is_healthy:
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_len', type=int, required=True)
    parser.add_argument('--episode_name', type=str, required=True)
    main(vars(parser.parse_args()))