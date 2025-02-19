import time
import csv
import h5py
import os
from constants import *

def setZeroConfiguration(piper):
    piper.MotionCtrl_2(0x01, 0x01, 20, 0x00)
    piper.JointCtrl(0, 0, 0, 0, 0, 0)
    piper.GripperCtrl(0,0, 0x01, 0)
    time.sleep(5)
    return True


def readJointCtrl(piper):
    joints = piper.GetArmJointCtrl().joint_ctrl
    joint_data = np.array([joints.joint_1, joints.joint_2, joints.joint_3, joints.joint_4, joints.joint_5, joints.joint_6])
    return joint_data


def readGripperCtrl(piper):
    grippers = piper.GetArmGripperCtrl().gripper_ctrl
    gripper_data = np.array([grippers.grippers_angle, grippers.grippers_effort])
    return gripper_data


def readEndPoseMsg(piper):
    end_pose = piper.GetArmEndPoseMsgs().end_pose
    end_pose_data =np.array([end_pose.X_axis, end_pose.Y_axis, end_pose.Z_axis, end_pose.RX_axis, end_pose.RY_axis, end_pose.RZ_axis])
    return end_pose_data


def readGripperMsg(piper):
    grippers = piper.GetArmGripperMsgs().gripper_state
    gripper_data = np.array([grippers.grippers_angle, grippers.grippers_effort])
    return gripper_data


def ctrlEndPose(piper, end_pose_data, gripper_data):
    gripper_angle, gripper_effort = gripper_data[:]

    piper.MotionCtrl_2(0x01, 0x00, 20, 0x00)
    piper.EndPoseCtrl(*end_pose_data)
    piper.GripperCtrl(abs(gripper_angle), gripper_effort, 0x01, 0)


def ctrlJoint(piper, joint_data, gripper_data):
    gripper_angle, gripper_effort = gripper_data[:]

    piper.MotionCtrl_2(0x01, 0x01, 20, 0x00)
    piper.JointCtrl(*joint_data)
    piper.GripperCtrl(abs(gripper_angle), gripper_effort, 0x01, 0)


def isMoved(piper, prev_data=None):
    if prev_data is None:
        prev_data = {'end_pose_data': [0] * 6, 'gripper_data': [0] * 6}
    current_data = {
        'end_pose': readEndPoseMsg(piper),
        'gripper': readGripperMsg(piper),
    }

    # diff = np.linalg.norm(current_data['end_pose'] - prev_data['end_pose'])
    # print(f'diff: {diff}')
    # print(f'prev_end_pose: {prev_data["end_pose"]}')
    # print(f'current_end_pose: {current_data["end_pose"]}')
    # end_pose_moved = (diff > MOVEMENT_THRESHOLD)

    end_pose_moved = (current_data["end_pose"] != prev_data["end_pose"]).all()

    if end_pose_moved:
        print('MOVED!')
        return True
    else:
        print('NOT MOVED!')
        return False
