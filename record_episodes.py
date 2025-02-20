import argparse
import os
import json
import pickle
from tqdm import tqdm
import h5py
import cv2
import time

import pyrealsense2 as rs

from piper_sdk import *
from record_data_joint import *
from record_data_img import *
from constants import *
from data_utils import *


class EpisodeRecorder:
    def __init__(self, args):
        self.episode_len = args['episode_len']
        self.episode_name = args['episode_name']

        self.task_config = config()
        self.task_config['EPISODE_LEN'] = self.episode_len

        self.piper = C_PiperInterface("can0")
        self.piper.ConnectPort()
        self.piper.EnableArm(7)

        self.rs_config = rs.config()
        self.rs_config.enable_stream(rs.stream.color)
        self.rs_config.enable_stream(rs.stream.depth)

        self.pipeline = rs.pipeline()
        self.pipeline.start(self.rs_config)

        self.episode_len = self.task_config["EPISODE_LEN"]
        self.fps = self.task_config["FPS"]
        self.dataset_dir = self.task_config["DATASET_DIR"]

        self.create_dir()

        self.t_start, self.t_robot, self.t_image = time.time(),time.time(),time.time()
        self.dt = 1 / self.fps
        self.max_timestep = self.episode_len * self.fps
        self.index = 0

        self.robot_data = None
        self.image_data = None
        self.robot_time_data = None

        self.robot_dataset = []
        self.image_dataset = []

        self.record_robot_time = []
        self.record_image_time = []

        self.is_healthy = True

    def create_dir(self):
        if not os.path.isdir(self.dataset_dir):
            os.makedirs(self.dataset_dir)
        try:
            if not os.path.exists(f"{self.dataset_dir}/{self.episode_name}"):
                os.makedirs(f"{self.dataset_dir}/{self.episode_name}")
        except OSError:
            print(f"Error: Creating directory. {self.episode_name}")
            exit()

    def record(self):
        for i in tqdm(range(self.max_timestep)):
            self.index = i
            self.is_healthy = self.capture_timestep()
            if not self.is_healthy:
                raise Exception("Health check failed")

    def capture_timestep(self):
        self.t_start = time.time()

        self.record_robot_data()
        self.t_robot = time.time()

        self.record_image_data()
        self.t_image = time.time()

        self.robot_time_data = {
            "index": self.index,
            "timestamp": self.t_robot-self.t_start,
            "robot": self.robot_data,
        }

        self.robot_dataset.append(self.robot_time_data)
        self.image_data.append(self.image_data)

        self.record_robot_time.append(self.t_robot - self.t_start)
        self.record_image_time.append(self.t_image - self.t_start)

        time.sleep(max(0, self.dt - (time.time() - self.t_start)))

        print(f"average time on recording robot data : {np.mean(self.record_robot_time)}")
        print(f"average time on recording image data : {np.mean(self.record_image_time)}")

        save_episode(self.robot_dataset, self.image_dataset, self.episode_name)
        return True

    def record_robot_data(self):
        self.robot_data = {
            "joint_data": readJointCtrl(self.piper),
            "gripper_data": readGripperCtrl(self.piper),
            "end_pose_data": readEndPoseMsg(self.piper),
        }

    def record_image_data(self):
        self.depth_image = np.array(self.pipeline.wait_for_frames().get_depth_frame().get_data()).astype(np.uint8)
        self.color_image = np.array(self.pipeline.wait_for_frames().get_color_image().get_data()).astype(np.uint8)

        self.color_image = cv2.resize(self.color_image, (self.depth_image.shape[1], self.depth_image.shape[0]))
        self.image_data = [self.color_image, self.depth_image]

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
    args = vars(parser.parse_args())

    episode_recorder = EpisodeRecorder(args)
    episode_recorder.record()