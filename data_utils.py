import shutil

import h5py
import os
import csv
import pickle

import cv2
import numpy as np
from constants import *

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


def save_episode(episode_name, robot_dataset, image_dataset=None ,is_record=True):
    save_episode_robot(robot_dataset, episode_name, is_record)
    save_episode_image(image_dataset, episode_name, is_record) if image_dataset else None


def load_episode(episode_name):
    dataset_dir = get_dataset_dir(is_record=True)
    try:
        with open(f"{dataset_dir}/{episode_name}/{episode_name}.pickle", "rb") as f:
            data = pickle.load(f)
        return data
    except:
        raise Exception(f"The file {dataset_dir}/{episode_name}/{episode_name}.pickle does not exist")


def save_episode_robot(robot_dataset, episode_name,is_record):
    index, timestamp = [],[]
    joint, gripper, end_pose = [],[],[]
    for data in robot_dataset:
        index.append(data['index'])
        timestamp.append(data['timestamp'])

        joint.append(data['robot']['joint_data'])
        gripper.append(data['robot']['gripper_data'])
        end_pose.append(data['robot']['end_pose_data'])

    robot_dataset_re = {
        'index': index,
        'timestamp': timestamp,
        'robot':{
            'joint_data':joint,
            'gripper_data':gripper,
            'end_pose_data':end_pose
        }
    }
    dataset_dir = get_dataset_dir(is_record)
    with open (f"{dataset_dir}/{episode_name}/{episode_name}.pickle", "wb") as f:
        pickle.dump(robot_dataset_re, f, pickle.HIGHEST_PROTOCOL)


def save_episode_image(image_dataset, episode_name, is_record):
    dataset_dir = get_dataset_dir(is_record)

    wrist_image_dataset = image_dataset['wrist_image_dataset']
    wrist_image_dataset_path = f"{dataset_dir}/{episode_name}/wrist"

    exo_image_dataset = image_dataset['exo_image_dataset']
    exo_image_dataset_path = f"{dataset_dir}/{episode_name}/exo"

    if os.path.exists(wrist_image_dataset_path):
        shutil.rmtree(wrist_image_dataset_path)
        os.mkdir(wrist_image_dataset_path)

    if os.path.exists(exo_image_dataset_path):
        shutil.rmtree(exo_image_dataset_path)
        os.mkdir(exo_image_dataset_path)

    save_episode_image_to_jpeg(wrist_image_dataset, wrist_image_dataset_path)
    save_episode_image_to_jpeg(exo_image_dataset, exo_image_dataset_path)


def save_episode_image_to_jpeg(image_dataset, image_dataset_path):
    for index, image_data in enumerate(image_dataset):
        color_image, depth_image = image_data
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB).astype(np.uint8)

        cv2.imwrite(f"{image_dataset_path}/color_img_{index}.jpeg", color_image)
        cv2.imwrite(f"{image_dataset_path}/depth_img_{index}.jpeg", depth_image)
    return True


def get_dataset_dir(is_record):
    if is_record:
        return RECORD_DATASET_DIR
    else:
        return REPLAY_DATASET_DIR


def save_exp_csv(data, instance_name, experiment_name):
    try:
        os.makedirs(f'experiments/{experiment_name}')
    except OSError:
        pass

    with open(f'experiments/{experiment_name}/{instance_name}.csv', 'w', newline='') as f:
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