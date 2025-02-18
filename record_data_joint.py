from robot_utils import *


def record_real_data_joint(piper):
    '''

    :param piper:
    :return: robot_data: {joint_data, gripper_data, end_pose_data}
    '''
    joint_data = readJointCtrl(piper)
    gripper_data = readGripperCtrl(piper)
    end_pose_data = readEndPoseMsg(piper)

    robot_data = {
        "joint_data": joint_data,
        "gripper_data": gripper_data,
        "end_pose_data": end_pose_data,
    }

    return robot_data