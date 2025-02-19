import argparse
import os

import time
import h5py
import matplotlib.pyplot as plt
import numpy as np

from piper_sdk import *
from constants import *
from record_data_joint import *
from robot_utils import *
from data_utils import *


def get_slave_data(piper):
    slave_end_pose = record_real_data_joint(piper)['end_pose_data']
    slave_joints = piper.GetArmJointMsgs().joint_state
    slave_joint_data = [
        slave_joints.joint_1,
        slave_joints.joint_2,
        slave_joints.joint_3,
        slave_joints.joint_4,
        slave_joints.joint_5,
        slave_joints.joint_6,
    ]

    return slave_end_pose, slave_joint_data


def update_plot(ax, des_end_poses, meas_end_poses, index):
    x = range(index + 1)
    titles = ['X','RX', 'Y', 'RY', 'Z', 'RZ']

    # X
    ax[0, 0].plot(x, des_end_poses[0], c='b')
    ax[0, 0].plot(x, meas_end_poses[0], c='r')
    ax[0, 0].grid(True)

    # y
    ax[1, 0].plot(x, des_end_poses[1], c='b')
    ax[1, 0].plot(x, meas_end_poses[1], c='r')
    ax[1, 0].grid(True)

    # Z
    ax[2, 0].plot(x, des_end_poses[2], c='b')
    ax[2, 0].plot(x, meas_end_poses[2], c='r')
    ax[2, 0].grid(True)

    # RX
    ax[0, 1].plot(x, des_end_poses[3], c='b')
    ax[0, 1].plot(x, meas_end_poses[3], c='r')
    ax[0, 1].grid(True)

    # RY
    ax[1, 1].plot(x, des_end_poses[4], c='b')
    ax[1, 1].plot(x, meas_end_poses[4], c='r')
    ax[1, 1].grid(True)

    # RZ
    ax[2, 1].plot(x, des_end_poses[5], c='b')
    ax[2, 1].plot(x, meas_end_poses[5], c='r')
    ax[2, 1].grid(True)

    for row in range(ax.shape[0]):
        for col in range(ax.shape[1]):
            ax[row,col].grid(True)
            ax[row,col].set_xlim(0,750)
            ax[row,col].legend(['desired','measured'])
            ax[row,col].set_title(titles.pop(0))

            if col == 1:
                ax[row,col].set_ylim(-200, 200)
            else:
                ax[row,col].set_ylim(-500, 500)


def main(args):
    episode_name = args['episode_name']
    control_mode = args['control_mode']

    piper = C_PiperInterface("can0")
    piper.ConnectPort()
    piper.EnableArm(7)
    setZeroConfiguration(piper)

    # recording actuation time
    record_act_time = []
    fps = FPS

    if not control_mode in ('JointCtrl', 'EndPoseCtrl'):
        print("Invalid control mode\n Try either 'JointCtrl' or 'EndPoseCtrl'")
        exit(1)

    # Load the h5 file using episode_name
    joint_data, gripper_data, end_pose_data = load_h5_data(file_name=f'dataset/episode_{episode_name}.h5')

    plt.ion()
    fig, ax = plt.subplots(3,2, figsize=[15, 10])
    des_end_poses = [[],[],[],[],[],[]]
    meas_end_poses = [[],[],[],[],[],[]]

    for i in range(end_pose_data.shape[0]):
        des_end_pose = end_pose_data[i]
        des_joint = joint_data[i]
        gripper = gripper_data[i]

        if control_mode == 'JointCtrl':
            ctrlJoint(piper, des_joint, gripper)
        elif control_mode == 'EndPoseCtrl':
            ctrlEndPose(piper, des_end_pose, gripper)
        time.sleep(1/fps)

        slave_end_pose, slave_joint_data = get_slave_data(piper)

        for j in range(6):
            des_end_poses[j].append(des_end_pose[j] * 0.001)
            meas_end_poses[j].append(slave_end_pose[j] * 0.001)

        update_plot(ax, np.array(des_end_poses), np.array(meas_end_poses), index= i)
        plt.pause(0.01)
        print(i)

    # if control_mode == 'JointCtrl':
    #     for i in range(end_pose_data.shape[0]):
    #         # t_before_act = time.time()
    #
    #         des_end_pose = end_pose_data[i]
    #         des_joint = joint_data[i]
    #         gripper = gripper_data[i]
    #         ctrlJoint(piper, des_joint, gripper)
    #         time.sleep(1 / fps)
    #
    #         # t_after_act = time.time()
    #         # record_act_time.append(t_after_act - t_before_act)
    #
    #
    #     print(f"average time on robot actuation : {np.mean(record_act_time)}")
    #
    # elif control_mode == 'EndPoseCtrl':
    #     for i in range(end_pose_data.shape[0]):
    #         # t_before_act = time.time()
    #         des_end_pose = end_pose_data[i]
    #         # des_end_pose[3:] = des_end_pose[3:]*(des_end_pose[3:]<=150000) - 160000*(des_end_pose[3:]>150000)
    #
    #         gripper = gripper_data[i]
    #         ctrlEndPose(piper, des_end_pose, gripper)
    #         time.sleep(1 / fps)
    #
    #         slave_end_pose, slave_joint_data = get_slave_data(piper)
    #
    #         for j in range(6):
    #             des_end_poses[j].append(des_end_pose[j])
    #             meas_end_poses[j].append(slave_end_pose[j])
    #
    #         update_plot(fig, ax, np.array(des_end_poses), np.array(meas_end_poses), index= i)
    #
    #         plt.pause(0.01)
    #         print(i)
    #
    #         # t_after_act = time.time()
    #         # record_act_time.append(t_after_act - t_before_act)
    #
    #     # print(f"average time on robot actuation : {np.mean(record_act_time)}")
    #
    #     x = range(end_pose_data.shape[0])
    #     end_pose_num = end_pose_data.shape[1]
    #
    #     # for i in range(end_pose_num):
    #     #         p = end_pose_data[:, i]
    #     #         if not i>2:
    #     #             ax1.plot(x, p)
    #     #         else:
    #     #             ax1.plot(x, p*(p<=0) + (p-360000)*(p>0))
    #
    #     # p = end_pose_data[:, 3]
    #     # ax1.plot(x, p * (p <= 0) + (p - 360000) * (p > 0))
    #     # ax1.plot(x, end_pose_perturbations[:,3])
    #     # ax1.grid(True)
    #     #
    #     # p = end_pose_data[:, 4]
    #     # ax2.plot(x, p)
    #     # ax2.plot(x, end_pose_perturbations[:,4])
    #     # ax2.grid(True)
    #     #
    #     # p = end_pose_data[:, 5]
    #     # ax3.plot(x, p * (p <= 0) + (p - 360000) * (p > 0))
    #     # ax3.plot(x, end_pose_perturbations[:,5])
    #     # ax3.grid(True)
    #
    #     # ax1.legend(['x','y','z','rx','ry','rz'])
    #     # ax1.axvline(singular_index, c='r', ls='--')
    #
    #     # x = range(len(end_pose_perturbations))
    #     # ax2.plot(x, np.linalg.norm(end_pose_perturbations,axis=1))
    #     # ax2.grid(True)
    #
    #     # x = range(joint_data.shape[0])
    #     # ax3.plot(x, joint_data)
    #     # ax3.grid(True)
    #     #
    #     # x = range(len(joint_perturbations))
    #     # ax4.plot(x, joint_perturbations)
    #     # ax4.grid(True)
    #     # ax4.set_ylim([-2000,2000])
    #     # ax2.axvline(singular_index, c='r', ls='--')
    #
    # else:
    #     print("Invalid control mode\n Try either 'JointCtrl' or 'EndPoseCtrl'")

    setZeroConfiguration(piper)
    plt.show()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--episode_name', type=str, required=True)
    # parser.add_argument('--control_mode', type=str, required=True)
    # main(vars(parser.parse_args()))

    argument = {
        'episode_name': 'cup_six_50',
        'control_mode': 'JointCtrl',
    }
    main(argument)