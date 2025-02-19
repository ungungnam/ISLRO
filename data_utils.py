import h5py
import os
import csv

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