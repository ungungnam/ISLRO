import time

def setZeroConfiguration(piper):
    piper.MotionCtrl_2(0x01, 0x01, 20, 0x00)
    piper.JointCtrl(0, 0, 0, 0, 0, 0)
    piper.GripperCtrl(0,0, 0x01, 0)
    time.sleep(5)
    return True


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