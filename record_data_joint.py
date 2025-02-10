def record_real_data_joint(piper):

    # Get the joint and gripper control data
    joints = piper.GetArmJointCtrl().joint_ctrl
    grippers = piper.GetArmGripperCtrl().gripper_ctrl
    end_pose = piper.GetArmEndPoseMsgs().end_pose

    # Prepare the data as a dictionary
    joint_data = [
        joints.joint_1,
        joints.joint_2,
        joints.joint_3,
        joints.joint_4,
        joints.joint_5,
        joints.joint_6,
    ]

    gripper_data = [
        grippers.grippers_angle,
        grippers.grippers_effort,
    ]

    end_pose_data = [
        end_pose.X_axis,
        end_pose.Y_axis,
        end_pose.Z_axis,
        end_pose.RX_axis,
        end_pose.RY_axis,
        end_pose.RZ_axis,
    ]

    robot_data = {
        "joint_data": joint_data,
        "gripper_data": gripper_data,
        "end_pose_data": end_pose_data,
    }

    return robot_data




