import h5py
import os
import csv
import pickle

import cv2
import numpy as np
from constants import *

dataset_dir = DATASET_DIR

def load_h5_data(file_name):
    try:
        with h5py.File(file_name, 'r') as f:
            # print(list(f['robot'].keys()))
            robot_group = f['robot']
            joint_data = robot_group['joint_data'][:]
            gripper_data = robot_group['gripper_data'][:]
            end_pose_data = robot_group['end_pose_data'][:]

        return joint_data, gripper_data, end_pose_data
    except:
        raise Exception("The file " + file_name + " does not exist")


def save_episode(robot_dataset, image_dataset, episode_name):
    _save_episode_robot(robot_dataset, episode_name)
    _save_episode_image(image_dataset, episode_name)


def _save_episode_robot(robot_dataset, episode_name):
    with open (f"{dataset_dir}/{episode_name}/{episode_name}.pickle", "wb") as f:
        pickle.dump(robot_dataset, f, pickle.HIGHEST_PROTOCOL)


def _save_episode_image(image_dataset, episode_name):
    for index, image_data in enumerate(image_dataset):
        color_image, depth_image = image_data

        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB).astype(np.uint8)
        depth_image = depth_image.astype(np.uint8)

        cv2.imwrite(f"{dataset_dir}/{episode_name}/color_img_{index}.jpeg", color_image)
        cv2.imwrite(f"{dataset_dir}/{episode_name}/depth_img_{index}.jpeg", depth_image)


def save_exp_csv(data, data_name, experiment_name):
    try:
        os.makedirs(f'experiments/{experiment_name}')
    except OSError:
        pass

    with open(f'experiments/{experiment_name}/{data_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return 0


def load_exp_csv(experiment_name, instance_name):
    try:
        with open(f'experiments/{experiment_name}/{instance_name}.csv', 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data
    except:
        raise Exception(f'The file experiments/{experiment_name}/{instance_name}.csv does not exist')