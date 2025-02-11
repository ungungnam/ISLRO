import argparse
import os

import time
import h5py
import numpy as np

from piper_sdk import *
from constants import *


def enable_fun(piper: C_PiperInterface):
    enable_flag = False
    elapsed_time_flag = False
    timeout = 5
    start_time = time.time()
    while not (enable_flag):
        elapsed_time = time.time() - start_time
        enable_flag = piper.GetArmLowSpdInfoMsgs().motor_1.foc_status.driver_enable_status and \
                      piper.GetArmLowSpdInfoMsgs().motor_2.foc_status.driver_enable_status and \
                      piper.GetArmLowSpdInfoMsgs().motor_3.foc_status.driver_enable_status and \
                      piper.GetArmLowSpdInfoMsgs().motor_4.foc_status.driver_enable_status and \
                      piper.GetArmLowSpdInfoMsgs().motor_5.foc_status.driver_enable_status and \
                      piper.GetArmLowSpdInfoMsgs().motor_6.foc_status.driver_enable_status
        piper.EnableArm(7)
        piper.GripperCtrl(0, 1000, 0x01, 0)
        if elapsed_time > timeout:
            print("Timeout....")
            elapsed_time_flag = True
            enable_flag = True
            break
        time.sleep(1)
        pass
    if (elapsed_time_flag):
        print("The program automatically enables timeout, exit the program")
        exit(0)


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


def main(args):
    episode_name = args['episode_name']
    control_mode = args['control_mode']

    piper = C_PiperInterface("can0")
    piper.ConnectPort()
    piper.EnableArm(7)
    enable_fun(piper=piper)

    # recording actuation time
    record_act_time = []
    fps = FPS

    # Load the h5 file using episode_name
    joint_data, gripper_data, end_pose_data = load_h5_data(file_name=f'dataset/episode_{episode_name}.h5')

    if control_mode == 'JointCtrl':
        for i in range(len(joint_data)):
            t_before_act = time.time()

            joint_1 = joint_data[i][0]
            joint_2 = joint_data[i][1]
            joint_3 = joint_data[i][2]
            joint_4 = joint_data[i][3]
            joint_5 = joint_data[i][4]
            joint_6 = joint_data[i][5]

            gripper_angle = gripper_data[i][0]
            gripper_effort = gripper_data[i][1]

            piper.MotionCtrl_2(0x01, 0x01, 20, 0x00)
            piper.JointCtrl(joint_1, joint_2, joint_3, joint_4, joint_5, joint_6)
            piper.GripperCtrl(abs(gripper_angle), gripper_effort, 0x01, 0)

            time.sleep(1/fps)
            t_after_act = time.time()
            record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(record_act_time)}")

    elif control_mode == 'EndPoseCtrl':
        for i in range(len(end_pose_data)):
            t_before_act = time.time()

            x = end_pose_data[i][0]
            y = end_pose_data[i][1]
            z = end_pose_data[i][2]
            rx = end_pose_data[i][3]
            ry = end_pose_data[i][4]
            rz = end_pose_data[i][5]

            gripper_angle = gripper_data[i][0]
            gripper_effort = gripper_data[i][1]

            piper.MotionCtrl_2(0x01, 0x00, 20, 0x00)
            piper.EndPoseCtrl(x, y, z, rx, ry, rz)
            piper.GripperCtrl(abs(gripper_angle), gripper_effort, 0x01, 0)

            time.sleep(1 / fps)

            t_after_act = time.time()
            record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(record_act_time)}")

    else:
        print("Invalid control mode\n Try either 'JointCtrl' or 'EndPoseCtrl'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_name', type=str, required=True)
    parser.add_argument('--control_mode', type=str, required=True)
    main(vars(parser.parse_args()))